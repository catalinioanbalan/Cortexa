import os
from dotenv import load_dotenv

load_dotenv(override=True)


class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    
    # Chunking settings - larger chunks preserve more context for better answers
    CHUNK_SIZE: int = 1000  # Increased from 500 for better semantic context
    CHUNK_OVERLAP: int = 200  # Increased from 100 to avoid breaking mid-thought
    
    # RAG retrieval settings
    RAG_TOP_K: int = 5  # Number of chunks to retrieve (increased from 3)
    
    # Embedding model
    EMBEDDING_MODEL: str = "text-embedding-3-large"
    
    # Chat model
    CHAT_MODEL: str = "gpt-4o-mini"
    
    # ChromaDB collection name
    COLLECTION_NAME: str = "pdf_documents"


settings = Settings()
