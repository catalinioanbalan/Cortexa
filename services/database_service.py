"""
Database service for SQLite-based chat history persistence.
"""

import aiosqlite
import os
from datetime import datetime
from typing import Optional
from config import settings


class DatabaseService:
    """Async SQLite database service for chat sessions and messages."""
    
    def __init__(self, db_path: str = "./chat_history.db"):
        self.db_path = db_path
        self._initialized = False
    
    async def initialize(self) -> None:
        """Create tables if they don't exist."""
        if self._initialized:
            return
            
        async with aiosqlite.connect(self.db_path) as db:
            # Create chat_sessions table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    doc_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Create chat_messages table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    citations_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for faster queries
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_doc_id ON chat_sessions(doc_id)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session_id ON chat_messages(session_id)
            """)
            
            await db.commit()
        
        self._initialized = True
    
    async def _ensure_initialized(self) -> None:
        """Ensure database is initialized before operations."""
        if not self._initialized:
            await self.initialize()
    
    # ==================== Session Operations ====================
    
    async def create_session(self, session_id: str, doc_id: str, title: str) -> dict:
        """Create a new chat session."""
        await self._ensure_initialized()
        
        now = datetime.utcnow().isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO chat_sessions (id, doc_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, doc_id, title, now, now)
            )
            await db.commit()
        
        return {
            "id": session_id,
            "doc_id": doc_id,
            "title": title,
            "created_at": now,
            "updated_at": now
        }
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get a session by ID."""
        await self._ensure_initialized()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM chat_sessions WHERE id = ?",
                (session_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
        return None
    
    async def get_sessions(self, doc_id: Optional[str] = None) -> list[dict]:
        """Get all sessions, optionally filtered by doc_id."""
        await self._ensure_initialized()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            if doc_id:
                query = "SELECT * FROM chat_sessions WHERE doc_id = ? ORDER BY updated_at DESC"
                params = (doc_id,)
            else:
                query = "SELECT * FROM chat_sessions ORDER BY updated_at DESC"
                params = ()
            
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def update_session_timestamp(self, session_id: str) -> None:
        """Update the updated_at timestamp for a session."""
        await self._ensure_initialized()
        
        now = datetime.utcnow().isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE chat_sessions SET updated_at = ? WHERE id = ?",
                (now, session_id)
            )
            await db.commit()
    
    async def update_session_title(self, session_id: str, title: str) -> None:
        """Update the title of a session."""
        await self._ensure_initialized()
        
        now = datetime.utcnow().isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE chat_sessions SET title = ?, updated_at = ? WHERE id = ?",
                (title, now, session_id)
            )
            await db.commit()
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages."""
        await self._ensure_initialized()
        
        async with aiosqlite.connect(self.db_path) as db:
            # Delete messages first (foreign key)
            await db.execute(
                "DELETE FROM chat_messages WHERE session_id = ?",
                (session_id,)
            )
            # Delete session
            cursor = await db.execute(
                "DELETE FROM chat_sessions WHERE id = ?",
                (session_id,)
            )
            await db.commit()
            return cursor.rowcount > 0
    
    # ==================== Message Operations ====================
    
    async def add_message(
        self,
        message_id: str,
        session_id: str,
        role: str,
        content: str,
        citations_json: Optional[str] = None
    ) -> dict:
        """Add a message to a session."""
        await self._ensure_initialized()
        
        now = datetime.utcnow().isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO chat_messages (id, session_id, role, content, citations_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (message_id, session_id, role, content, citations_json, now)
            )
            await db.commit()
        
        # Update session timestamp
        await self.update_session_timestamp(session_id)
        
        return {
            "id": message_id,
            "session_id": session_id,
            "role": role,
            "content": content,
            "citations_json": citations_json,
            "created_at": now
        }
    
    async def get_messages(self, session_id: str) -> list[dict]:
        """Get all messages for a session."""
        await self._ensure_initialized()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM chat_messages WHERE session_id = ? ORDER BY created_at ASC",
                (session_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_session_with_messages(self, session_id: str) -> Optional[dict]:
        """Get a session with all its messages."""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        messages = await self.get_messages(session_id)
        session["messages"] = messages
        return session


# Singleton instance
database_service = DatabaseService()
