import os
from dotenv import load_dotenv

load_dotenv(override=True)


class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    
    # Chunking settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    
    # Embedding model
    EMBEDDING_MODEL: str = "text-embedding-3-large"
    
    # Chat model
    CHAT_MODEL: str = "gpt-4o-mini"
    
    # ChromaDB collection name
    COLLECTION_NAME: str = "pdf_documents"


settings = Settings()
