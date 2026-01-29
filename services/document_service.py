import uuid
import re
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
        # Use sentence-aware separators for better semantic chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=[
                "\n\n",      # Double newlines (paragraphs)
                "\n",        # Single newlines
                ". ",        # Sentence boundaries
                "? ",        # Question boundaries
                "! ",        # Exclamation boundaries  
                "; ",        # Semicolon boundaries
                ", ",        # Comma boundaries
                " ",         # Word boundaries
                ""           # Character boundaries (last resort)
            ],
            length_function=len,
            is_separator_regex=False,
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
        """Extract text from PDF with improved chunking strategy.
        
        Strategy: Combine all pages with page markers, then chunk semantically.
        This avoids breaking content that spans pages and preserves context.
        """
        chunks_with_metadata = []
        filename = Path(file_path).stem.split('_', 1)[-1]  # Get original filename without doc_id
        
        # First pass: extract all text with page markers
        page_texts = []
        page_boundaries = {}  # Maps character position to page number
        current_pos = 0
        
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    # Clean up text: normalize whitespace
                    text = re.sub(r'\s+', ' ', text).strip()
                    page_boundaries[current_pos] = page_num
                    page_texts.append(text)
                    current_pos += len(text) + 2  # +2 for "\n\n" separator
        
        if not page_texts:
            return []
        
        # Combine all text with paragraph separators
        full_text = "\n\n".join(page_texts)
        
        # Chunk the combined text
        raw_chunks = self.text_splitter.split_text(full_text)
        
        # Assign page numbers to chunks based on position
        for chunk_text in raw_chunks:
            # Find which page this chunk starts in
            chunk_start = full_text.find(chunk_text)
            page_num = 1
            for pos, pnum in sorted(page_boundaries.items()):
                if chunk_start >= pos:
                    page_num = pnum
                else:
                    break
            
            # Add contextual prefix for better retrieval
            context_prefix = f"[Document: {filename}] "
            chunks_with_metadata.append({
                "text": context_prefix + chunk_text,
                "page": page_num
            })

        return chunks_with_metadata

    def _extract_text(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text from txt/md files with contextual prefixing."""
        filename = Path(file_path).stem.split('_', 1)[-1]  # Get original filename without doc_id
        
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        chunks = self.text_splitter.split_text(text)
        
        # Add contextual prefix for better retrieval
        context_prefix = f"[Document: {filename}] "
        return [{"text": context_prefix + chunk, "page": 1} for chunk in chunks]

    def get_filename_by_doc_id(self, doc_id: str) -> str | None:
        """Get original filename from doc_id by searching uploads folder."""
        for file_path in self.upload_dir.iterdir():
            if file_path.name.startswith(f"{doc_id}_"):
                # Extract original filename (remove doc_id prefix)
                return file_path.name[len(doc_id) + 1:]
        return None

    def delete_document_file(self, doc_id: str) -> bool:
        """Delete document file from uploads folder."""
        for file_path in self.upload_dir.iterdir():
            if file_path.name.startswith(f"{doc_id}_"):
                file_path.unlink()
                return True
        return False


document_service = DocumentService()
