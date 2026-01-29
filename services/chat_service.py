"""
Chat service for session management, message handling, and export functionality.
"""

import json
import uuid
from io import BytesIO
from typing import Optional
from fpdf import FPDF

from services.database_service import database_service


class ChatService:
    """Service for managing chat sessions and exporting conversations."""
    
    def __init__(self):
        self.db = database_service
    
    async def initialize(self) -> None:
        """Initialize the underlying database."""
        await self.db.initialize()
    
    # ==================== Session Management ====================
    
    async def create_session(self, doc_id: str, title: Optional[str] = None) -> dict:
        """Create a new chat session for a document."""
        session_id = str(uuid.uuid4())
        if not title:
            title = "New Chat"
        
        return await self.db.create_session(session_id, doc_id, title)
    
    async def get_sessions(self, doc_id: Optional[str] = None) -> list[dict]:
        """Get all sessions, optionally filtered by document ID."""
        return await self.db.get_sessions(doc_id)
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get a session by ID."""
        return await self.db.get_session(session_id)
    
    async def get_session_with_messages(self, session_id: str) -> Optional[dict]:
        """Get a session with all its messages."""
        session = await self.db.get_session_with_messages(session_id)
        if session and session.get("messages"):
            # Parse citations_json for each message
            for msg in session["messages"]:
                if msg.get("citations_json"):
                    try:
                        msg["citations"] = json.loads(msg["citations_json"])
                    except json.JSONDecodeError:
                        msg["citations"] = []
                else:
                    msg["citations"] = []
        return session
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages."""
        return await self.db.delete_session(session_id)
    
    async def update_session_title(self, session_id: str, title: str) -> None:
        """Update the title of a session."""
        await self.db.update_session_title(session_id, title)
    
    # ==================== Message Management ====================
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        citations: Optional[list[dict]] = None
    ) -> dict:
        """Add a message to a session."""
        message_id = str(uuid.uuid4())
        citations_json = json.dumps(citations) if citations else None
        
        message = await self.db.add_message(
            message_id=message_id,
            session_id=session_id,
            role=role,
            content=content,
            citations_json=citations_json
        )
        
        # Return with parsed citations
        message["citations"] = citations or []
        return message
    
    async def get_messages(self, session_id: str) -> list[dict]:
        """Get all messages for a session with parsed citations."""
        messages = await self.db.get_messages(session_id)
        
        for msg in messages:
            if msg.get("citations_json"):
                try:
                    msg["citations"] = json.loads(msg["citations_json"])
                except json.JSONDecodeError:
                    msg["citations"] = []
            else:
                msg["citations"] = []
        
        return messages
    
    # ==================== Export Functions ====================
    
    async def export_markdown(self, session_id: str) -> Optional[str]:
        """Export a session as markdown."""
        session = await self.get_session_with_messages(session_id)
        if not session:
            return None
        
        lines = []
        lines.append(f"# {session['title']}")
        lines.append("")
        lines.append(f"*Document ID: {session['doc_id']}*")
        lines.append(f"*Created: {session['created_at']}*")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        for msg in session.get("messages", []):
            role_label = "**User:**" if msg["role"] == "user" else "**Assistant:**"
            lines.append(role_label)
            lines.append("")
            lines.append(msg["content"])
            lines.append("")
            
            # Add citations if present
            citations = msg.get("citations", [])
            if citations:
                lines.append("*Citations:*")
                for i, citation in enumerate(citations, 1):
                    page = citation.get("page", "N/A")
                    confidence = citation.get("confidence", 0)
                    text = citation.get("text", "")[:200]  # Truncate long citations
                    lines.append(f"  {i}. Page {page} (confidence: {confidence:.0%}): \"{text}...\"")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)
    
    async def export_pdf(self, session_id: str) -> Optional[bytes]:
        """Export a session as PDF."""
        session = await self.get_session_with_messages(session_id)
        if not session:
            return None
        
        pdf = FPDF()
        pdf.set_margins(15, 15, 15)
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        
        # Calculate effective width
        effective_width = pdf.w - pdf.l_margin - pdf.r_margin
        
        # Helper to safely encode text for PDF
        def safe_text(text: str) -> str:
            return text.encode('latin-1', 'replace').decode('latin-1')
        
        # Title
        pdf.set_font("Helvetica", "B", 14)
        title = safe_text(session["title"][:100])  # Truncate very long titles
        pdf.multi_cell(effective_width, 8, title)
        pdf.ln(2)
        
        # Metadata
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(effective_width, 5, f"Document ID: {session['doc_id']}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(effective_width, 5, f"Created: {session['created_at']}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)
        
        # Separator line
        pdf.set_draw_color(200, 200, 200)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(5)
        
        for msg in session.get("messages", []):
            # Role header
            role_label = "User:" if msg["role"] == "user" else "Assistant:"
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(effective_width, 7, role_label, new_x="LMARGIN", new_y="NEXT")
            
            # Message content
            pdf.set_font("Helvetica", "", 9)
            content = safe_text(msg["content"])
            pdf.multi_cell(effective_width, 5, content)
            pdf.ln(2)
            
            # Citations
            citations = msg.get("citations", [])
            if citations:
                pdf.set_font("Helvetica", "I", 8)
                pdf.cell(effective_width, 5, "Citations:", new_x="LMARGIN", new_y="NEXT")
                for i, citation in enumerate(citations, 1):
                    page = citation.get("page", "N/A")
                    confidence = citation.get("confidence", 0)
                    text = safe_text(citation.get("text", "")[:80])  # Shorter truncation
                    citation_text = f"{i}. Page {page} ({confidence:.0%}): {text}..."
                    pdf.multi_cell(effective_width, 4, citation_text)
                pdf.ln(2)
            
            # Separator
            pdf.set_draw_color(220, 220, 220)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(5)
        
        # Return as bytes
        return bytes(pdf.output())


# Singleton instance
chat_service = ChatService()
