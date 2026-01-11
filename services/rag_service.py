from typing import Dict, List
from openai import OpenAI

from config import settings
from services.embedding_service import embedding_service
from services.vector_store_service import vector_store_service


class RAGService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.CHAT_MODEL
    
    def answer_question(self, question: str, doc_id: str) -> Dict[str, any]:
        """
        Answer a question based on retrieved document chunks.
        
        Args:
            question: The user's question
            doc_id: The document UUID to search in
            
        Returns:
            Dict with:
            - answer: The AI-generated answer
            - source_pages: List of page numbers used
        """
        # Generate embedding for the question
        question_embedding = embedding_service.generate_embedding(question)
        
        # Query vector store for relevant chunks
        results = vector_store_service.query_by_doc_id(
            query_embedding=question_embedding,
            doc_id=doc_id,
            top_k=3
        )
        
        if not results["documents"]:
            return {
                "answer": "No relevant information found in the document.",
                "source_pages": []
            }
        
        # Extract context and page numbers
        context_chunks = results["documents"]
        source_pages = [meta["page"] for meta in results["metadatas"]]
        
        # Build context string
        context = "\n\n".join([
            f"[Page {meta['page']}]\n{doc}"
            for doc, meta in zip(context_chunks, results["metadatas"])
        ])
        
        # Build prompt that forces strict context-based answers
        prompt = f"""You are a precise assistant that answers questions STRICTLY based on the provided context.

IMPORTANT RULES:
- Answer ONLY using information from the context below
- If the context doesn't contain enough information to answer the question, say "The provided document does not contain sufficient information to answer this question."
- Do NOT use any external knowledge
- Be concise and accurate
- Reference page numbers when relevant

Context:
{context}

Question: {question}

Answer:"""
        
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
            "source_pages": sorted(list(set(source_pages)))
        }


rag_service = RAGService()
