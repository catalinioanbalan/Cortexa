from typing import Dict, List
from openai import OpenAI

from config import settings
from services.embedding_service import embedding_service
from services.vector_store_service import vector_store_service

MAX_CITATION_LENGTH = 500


class RAGService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.CHAT_MODEL
    
    def _truncate_text(self, text: str, max_length: int = MAX_CITATION_LENGTH) -> str:
        """Truncate text to max_length, adding ellipsis if needed."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3].rsplit(' ', 1)[0] + "..."
    
    def _distance_to_confidence(self, distance: float) -> float:
        """Convert cosine distance to confidence score (0-1)."""
        # Cosine distance ranges from 0 (identical) to 2 (opposite)
        # We use 1 - (distance / 2) to get similarity, then clamp
        confidence = 1 - (distance / 2)
        return round(max(0.0, min(1.0, confidence)), 2)
    
    def answer_question(self, question: str, doc_id: str) -> Dict[str, any]:
        """
        Answer a question based on retrieved document chunks.
        
        Args:
            question: The user's question
            doc_id: The document UUID to search in
            
        Returns:
            Dict with:
            - answer: The AI-generated answer
            - citations: List of citation objects with text, page, confidence, chunk_id
        """
        # Generate embedding for the question
        question_embedding = embedding_service.generate_embedding(question)
        
        # Query vector store for relevant chunks
        results = vector_store_service.query_by_doc_id(
            query_embedding=question_embedding,
            doc_id=doc_id,
            top_k=settings.RAG_TOP_K  # Configurable, defaults to 5
        )
        
        if not results["documents"]:
            return {
                "answer": "No relevant information found in the document.",
                "citations": []
            }
        
        # Build citations with confidence scores
        citations = []
        for i, (doc, meta, distance) in enumerate(zip(
            results["documents"],
            results["metadatas"],
            results["distances"]
        )):
            citations.append({
                "text": self._truncate_text(doc),
                "page": meta["page"],
                "confidence": self._distance_to_confidence(distance),
                "chunk_id": f"{doc_id}_chunk_{i}"
            })
        
        # Build context string
        context = "\n\n".join([
            f"[Page {meta['page']}]\n{doc}"
            for doc, meta in zip(results["documents"], results["metadatas"])
        ])
        
        # Build prompt that forces strict context-based answers
        prompt = f"""You are a precise assistant that answers questions STRICTLY based on the provided context.

IMPORTANT RULES:
- Answer ONLY using information from the context below
- If the context doesn't contain enough information to answer the question, say "The provided document does not contain sufficient information to answer this question."
- Do NOT use any external knowledge or make assumptions beyond what's stated
- Be thorough - synthesize information from multiple passages if relevant
- Be concise but complete - include all relevant details from the context
- Reference page numbers when citing specific information (e.g., "According to page 3...")
- If multiple passages contain relevant information, combine them for a comprehensive answer

Context from the document:
{context}

Question: {question}

Provide a well-structured answer:"""
        
        # Call OpenAI Chat Completion
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions strictly based on provided context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        answer = response.choices[0].message.content
        
        return {
            "answer": answer,
            "citations": citations
        }


rag_service = RAGService()
