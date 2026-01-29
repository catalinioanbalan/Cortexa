from typing import List, Dict
import chromadb

from config import settings


class VectorStoreService:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR
        )
        self.collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_chunks(
        self,
        doc_id: str,
        chunks: List[Dict[str, any]],
        embeddings: List[List[float]]
    ):
        """
        Add document chunks with embeddings to ChromaDB.
        
        Args:
            doc_id: The document UUID
            chunks: List of chunk dicts with 'text' and 'page' keys
            embeddings: List of embedding vectors
        """
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        documents = [chunk["text"] for chunk in chunks]
        metadatas = [
            {
                "doc_id": doc_id,
                "page": chunk["page"]
            }
            for chunk in chunks
        ]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
    
    def query_by_doc_id(
        self,
        query_embedding: List[float],
        doc_id: str,
        top_k: int = 3
    ) -> Dict:
        """
        Query ChromaDB for relevant chunks filtered by doc_id.
        
        Args:
            query_embedding: The query embedding vector
            doc_id: The document UUID to filter by
            top_k: Number of results to return
            
        Returns:
            Dict containing:
            - documents: List of matched text chunks
            - metadatas: List of metadata dicts (with page numbers)
            - distances: List of distance scores
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"doc_id": doc_id}
        )
        
        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else []
        }


vector_store_service = VectorStoreService()
