from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List

from services.pdf_service import pdf_service
from services.embedding_service import embedding_service
from services.vector_store_service import vector_store_service
from services.rag_service import rag_service

app = FastAPI(title="PDF RAG Service", version="1.0.0")


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


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file, extract text, chunk it, generate embeddings, and store in ChromaDB.
    
    Args:
        file: The PDF file to upload
        
    Returns:
        UploadResponse with doc_id, filename, and number of chunks created
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Save PDF locally
        doc_id, file_path = pdf_service.save_pdf(file_content, file.filename)
        
        # Extract and chunk text
        chunks = pdf_service.extract_and_chunk_text(file_path)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")
        
        # Generate embeddings for all chunks
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding_service.generate_embeddings(chunk_texts)
        
        # Store in ChromaDB
        vector_store_service.add_chunks(doc_id, chunks, embeddings)
        
        return UploadResponse(
            doc_id=doc_id,
            filename=file.filename,
            chunks_created=len(chunks)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


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


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
