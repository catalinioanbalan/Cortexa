import uuid
from pathlib import Path
from typing import List, Dict, Any
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import settings


class DocumentService:
    SUPPORTED_EXTENSIONS = {'.pdf', '.txt', '.md'}

    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

    def save_document(self, file_content: bytes, filename: str) -> tuple[str, str]:
        """Save document locally and return doc_id and file path."""
        doc_id = str(uuid.uuid4())
        file_path = self.upload_dir / f"{doc_id}_{filename}"

        with open(file_path, "wb") as f:
            f.write(file_content)

        return doc_id, str(file_path)

    def extract_and_chunk_text(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text from document and split into chunks."""
        ext = Path(file_path).suffix.lower()

        if ext == '.pdf':
            return self._extract_pdf(file_path)
        elif ext in {'.txt', '.md'}:
            return self._extract_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def _extract_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF page by page."""
        chunks_with_metadata = []

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()

                if text:
                    page_chunks = self.text_splitter.split_text(text)
                    for chunk_text in page_chunks:
                        chunks_with_metadata.append({
                            "text": chunk_text,
                            "page": page_num
                        })

        return chunks_with_metadata

    def _extract_text(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text from txt/md files."""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        chunks = self.text_splitter.split_text(text)
        return [{"text": chunk, "page": 1} for chunk in chunks]


document_service = DocumentService()
