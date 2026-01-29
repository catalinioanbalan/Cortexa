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

    def get_all_documents(self) -> List[Dict]:
        """Get all unique documents with their chunk counts."""
        results = self.collection.get(include=["metadatas"])
        
        if not results["metadatas"]:
            return []
        
        # Group by doc_id and count chunks
        doc_map: Dict[str, Dict] = {}
        for meta in results["metadatas"]:
            doc_id = meta.get("doc_id")
            if doc_id:
                if doc_id not in doc_map:
                    doc_map[doc_id] = {"doc_id": doc_id, "chunks": 0}
                doc_map[doc_id]["chunks"] += 1
        
        return list(doc_map.values())

    def document_exists(self, doc_id: str) -> bool:
        """Check if a document exists in the collection."""
        results = self.collection.get(
            where={"doc_id": doc_id},
            limit=1
        )
        return len(results["ids"]) > 0

    def delete_document(self, doc_id: str) -> None:
        """Delete all chunks for a document."""
        self.collection.delete(where={"doc_id": doc_id})


vector_store_service = VectorStoreService()
