from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from services.document_service import document_service
from services.embedding_service import embedding_service
from services.vector_store_service import vector_store_service
from services.rag_service import rag_service
from services.interpreter_service import interpreter_service

app = FastAPI(title="Cortexa - Document Interpretation", version="1.0.0")

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
        request: AskRequest with question and doc_id
        
    Returns:
        AskResponse with answer and citations
    """
    try:
        result = rag_service.answer_question(request.question, request.doc_id)
        
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


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
