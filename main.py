from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional

from services.document_service import document_service
from services.embedding_service import embedding_service
from services.vector_store_service import vector_store_service
from services.rag_service import rag_service
from services.interpreter_service import interpreter_service
from services.chat_service import chat_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    await chat_service.initialize()
    yield


app = FastAPI(title="Cortexa - Document Interpretation", version="1.0.0", lifespan=lifespan)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.md'}


class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    chunks_created: int


class AskRequest(BaseModel):
    question: str
    doc_id: str
    session_id: Optional[str] = None  # Optional: auto-save to session if provided


class Citation(BaseModel):
    text: str
    page: int
    confidence: float
    chunk_id: str


class AskResponse(BaseModel):
    answer: str
    citations: List[Citation]


class InterpretRequest(BaseModel):
    input: str
    tone: str = "insightful"  # insightful, supportive, analytical, creative, direct
    style: str = "concise"    # concise, detailed, bullet_points, narrative
    context: str | None = None


class InterpretResponse(BaseModel):
    interpretation: str
    tone: str
    style: str


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    chunks: int


# ==================== Chat Session Models ====================

class CreateSessionRequest(BaseModel):
    doc_id: str
    title: Optional[str] = None


class ChatSession(BaseModel):
    id: str
    doc_id: str
    title: str
    created_at: str
    updated_at: str


class ChatMessage(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    citations: Optional[List[Citation]] = None
    created_at: str


class ChatSessionWithMessages(ChatSession):
    messages: List[ChatMessage] = []


class AddMessageRequest(BaseModel):
    role: str
    content: str
    citations: Optional[List[dict]] = None


class UpdateSessionRequest(BaseModel):
    title: str


@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """List all documents stored in the database."""
    try:
        docs = vector_store_service.get_all_documents()
        result = []
        for doc in docs:
            filename = document_service.get_filename_by_doc_id(doc["doc_id"])
            result.append(DocumentInfo(
                doc_id=doc["doc_id"],
                filename=filename or "Unknown",
                chunks=doc["chunks"]
            ))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document from the database and filesystem."""
    try:
        if not vector_store_service.document_exists(doc_id):
            raise HTTPException(status_code=404, detail="Document not found")
        
        vector_store_service.delete_document(doc_id)
        document_service.delete_document_file(doc_id)
        return {"status": "deleted", "doc_id": doc_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document (pdf, txt, md), extract text, chunk it, generate embeddings, and store in ChromaDB.
    """
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Supported formats: {', '.join(ALLOWED_EXTENSIONS)}")

    try:
        file_content = await file.read()
        doc_id, file_path = document_service.save_document(file_content, file.filename)
        chunks = document_service.extract_and_chunk_text(file_path)

        if not chunks:
            raise HTTPException(status_code=400, detail="No text could be extracted from the document")

        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding_service.generate_embeddings(chunk_texts)
        vector_store_service.add_chunks(doc_id, chunks, embeddings)

        return UploadResponse(
            doc_id=doc_id,
            filename=file.filename,
            chunks_created=len(chunks)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Ask a question about a specific document.
    
    Args:
        request: AskRequest with question, doc_id, and optional session_id
        
    Returns:
        AskResponse with answer and citations
    """
    try:
        result = rag_service.answer_question(request.question, request.doc_id)
        
        # Auto-save to session if session_id provided
        if request.session_id:
            # Save user question
            await chat_service.add_message(
                session_id=request.session_id,
                role="user",
                content=request.question
            )
            # Save assistant answer with citations
            await chat_service.add_message(
                session_id=request.session_id,
                role="assistant",
                content=result["answer"],
                citations=result["citations"]
            )
        
        return AskResponse(
            answer=result["answer"],
            citations=[Citation(**c) for c in result["citations"]]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")


@app.post("/interpret", response_model=InterpretResponse)
async def interpret_input(request: InterpretRequest):
    """Interpret user input with specified tone and style."""
    try:
        result = interpreter_service.interpret(
            user_input=request.input,
            tone=request.tone,
            style=request.style,
            context=request.context
        )
        return InterpretResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interpreting input: {str(e)}")


# ==================== Chat Session Endpoints ====================

@app.get("/sessions", response_model=List[ChatSession])
async def list_sessions(doc_id: Optional[str] = Query(None)):
    """List all chat sessions, optionally filtered by document ID."""
    try:
        sessions = await chat_service.get_sessions(doc_id)
        return [ChatSession(**s) for s in sessions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")


@app.post("/sessions", response_model=ChatSession)
async def create_session(request: CreateSessionRequest):
    """Create a new chat session for a document."""
    try:
        session = await chat_service.create_session(request.doc_id, request.title)
        return ChatSession(**session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


@app.get("/sessions/{session_id}", response_model=ChatSessionWithMessages)
async def get_session(session_id: str):
    """Get a chat session with all its messages."""
    try:
        session = await chat_service.get_session_with_messages(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Convert messages to proper format
        messages = []
        for msg in session.get("messages", []):
            messages.append(ChatMessage(
                id=msg["id"],
                session_id=msg["session_id"],
                role=msg["role"],
                content=msg["content"],
                citations=[Citation(**c) for c in msg.get("citations", [])] if msg.get("citations") else None,
                created_at=msg["created_at"]
            ))
        
        return ChatSessionWithMessages(
            id=session["id"],
            doc_id=session["doc_id"],
            title=session["title"],
            created_at=session["created_at"],
            updated_at=session["updated_at"],
            messages=messages
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session: {str(e)}")


@app.patch("/sessions/{session_id}", response_model=ChatSession)
async def update_session(session_id: str, request: UpdateSessionRequest):
    """Update a chat session's title."""
    try:
        session = await chat_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await chat_service.update_session_title(session_id, request.title)
        updated_session = await chat_service.get_session(session_id)
        return ChatSession(**updated_session)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating session: {str(e)}")


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session and all its messages."""
    try:
        deleted = await chat_service.delete_session(session_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"status": "deleted", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")


@app.post("/sessions/{session_id}/messages", response_model=ChatMessage)
async def add_message(session_id: str, request: AddMessageRequest):
    """Add a message to a chat session."""
    try:
        session = await chat_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        message = await chat_service.add_message(
            session_id=session_id,
            role=request.role,
            content=request.content,
            citations=request.citations
        )
        
        return ChatMessage(
            id=message["id"],
            session_id=message["session_id"],
            role=message["role"],
            content=message["content"],
            citations=[Citation(**c) for c in message.get("citations", [])] if message.get("citations") else None,
            created_at=message["created_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding message: {str(e)}")


@app.get("/sessions/{session_id}/export")
async def export_session(session_id: str, format: str = Query("md", pattern="^(md|pdf)$")):
    """Export a chat session as markdown or PDF."""
    try:
        session = await chat_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if format == "md":
            content = await chat_service.export_markdown(session_id)
            if not content:
                raise HTTPException(status_code=500, detail="Error generating markdown")
            return Response(
                content=content,
                media_type="text/markdown",
                headers={"Content-Disposition": f"attachment; filename={session['title']}.md"}
            )
        else:  # pdf
            content = await chat_service.export_pdf(session_id)
            if not content:
                raise HTTPException(status_code=500, detail="Error generating PDF")
            return Response(
                content=content,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={session['title']}.pdf"}
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting session: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
