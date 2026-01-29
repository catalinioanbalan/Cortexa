from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List

from services.document_service import document_service
from services.embedding_service import embedding_service
from services.vector_store_service import vector_store_service
from services.rag_service import rag_service
from services.interpreter_service import interpreter_service

app = FastAPI(title="Cortexa - Document Interpretation", version="1.0.0")

ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.md'}


class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    chunks_created: int


class AskRequest(BaseModel):
    question: str
    doc_id: str


class AskResponse(BaseModel):
    answer: str
    source_pages: List[int]


class InterpretRequest(BaseModel):
    input: str
    tone: str = "insightful"  # insightful, supportive, analytical, creative, direct
    style: str = "concise"    # concise, detailed, bullet_points, narrative
    context: str | None = None


class InterpretResponse(BaseModel):
    interpretation: str
    tone: str
    style: str


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
        AskResponse with answer and source page numbers
    """
    try:
        result = rag_service.answer_question(request.question, request.doc_id)
        
        return AskResponse(
            answer=result["answer"],
            source_pages=result["source_pages"]
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
