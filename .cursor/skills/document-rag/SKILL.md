---
name: document-rag
description: Document RAG pipeline for txt, pdf, md files. Use when implementing document upload, text extraction, chunking, embedding storage, or question answering over documents.
---

# Document RAG Pipeline

## Overview

Upload → Extract text → Chunk → Embed → Store → Query → Answer

## Existing Code Base

Current services in `services/`:
- `pdf_service.py` - PDF extraction (rename to `document_service.py`)
- `embedding_service.py` - OpenAI embeddings
- `vector_store_service.py` - ChromaDB storage
- `rag_service.py` - Q&A generation

## Extend Document Service

Rename `pdf_service.py` → `document_service.py` and add:

```python
class DocumentService:
    SUPPORTED_TYPES = {'.pdf', '.txt', '.md'}

    def save_document(self, content: bytes, filename: str) -> tuple[str, str]:
        doc_id = str(uuid.uuid4())
        file_path = self.upload_dir / f"{doc_id}_{filename}"
        with open(file_path, "wb") as f:
            f.write(content)
        return doc_id, str(file_path)

    def extract_and_chunk_text(self, file_path: str) -> list[dict]:
        ext = Path(file_path).suffix.lower()
        
        if ext == '.pdf':
            return self._extract_pdf(file_path)
        elif ext in {'.txt', '.md'}:
            return self._extract_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def _extract_text(self, file_path: str) -> list[dict]:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        chunks = self.text_splitter.split_text(text)
        return [{"text": chunk, "page": 1} for chunk in chunks]

    def _extract_pdf(self, file_path: str) -> list[dict]:
        # existing pdfplumber logic
        ...
```

## Update Upload Endpoint

```python
ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.md'}

@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Supported formats: {ALLOWED_EXTENSIONS}")
    
    content = await file.read()
    doc_id, file_path = document_service.save_document(content, file.filename)
    chunks = document_service.extract_and_chunk_text(file_path)
    # ... rest unchanged
```

## Query Flow (already implemented)

1. `/ask` receives question + doc_id
2. Generate question embedding
3. Query ChromaDB filtered by doc_id
4. Build context from top-k chunks
5. Send to OpenAI with strict context prompt
6. Return answer + source pages
