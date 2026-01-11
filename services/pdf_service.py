import os
import uuid
from pathlib import Path
from typing import List, Dict
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import settings


class PDFService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
    
    def save_pdf(self, file_content: bytes, filename: str) -> tuple[str, str]:
        """
        Save PDF file locally and return doc_id and file path.
        
        Returns:
            tuple: (doc_id, file_path)
        """
        doc_id = str(uuid.uuid4())
        file_path = self.upload_dir / f"{doc_id}_{filename}"
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return doc_id, str(file_path)
    
    def extract_and_chunk_text(self, file_path: str) -> List[Dict[str, any]]:
        """
        Extract text from PDF page by page and split into chunks.
        
        Returns:
            List of dicts with structure:
            [
                {
                    "text": "chunk text",
                    "page": page_number
                },
                ...
            ]
        """
        chunks_with_metadata = []
        
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                
                if text:
                    # Split the page text into chunks
                    page_chunks = self.text_splitter.split_text(text)
                    
                    # Add page metadata to each chunk
                    for chunk_text in page_chunks:
                        chunks_with_metadata.append({
                            "text": chunk_text,
                            "page": page_num
                        })
        
        return chunks_with_metadata


pdf_service = PDFService()
