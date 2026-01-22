"""
Conversation Store - RAG for chat history

Stores conversation turns with embeddings for semantic retrieval
of relevant past discussions.
"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ConversationTurn:
    """A single conversation turn"""
    id: Optional[int]
    timestamp: str
    user_query: str
    assistant_response: str
    session_id: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ConversationStore:
    """
    Stores and retrieves conversation history using embeddings.
    
    Features:
    - Persistent storage in SQLite + ChromaDB
    - Semantic search over past conversations
    - Session management
    """
    
    def __init__(
        self,
        persist_dir: Path,
        embedding_model: str = "nomic-embed-text",
        ollama_host: str = "http://localhost:11434",
    ):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.embedding_model = embedding_model
        self.ollama_host = ollama_host
        
        # SQLite for metadata and full text
        self.db_path = self.persist_dir / "conversations.db"
        self._init_database()
        
        # ChromaDB for embeddings
        self._collection = None
        self._client = None
        self._ollama_client = None
        
        # Current session
        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_query TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                session_id TEXT NOT NULL,
                metadata TEXT,
                embedding_id TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_session 
            ON conversations(session_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON conversations(timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def _get_ollama_client(self):
        """Get or create Ollama client"""
        if self._ollama_client is None:
            import ollama
            self._ollama_client = ollama.Client(host=self.ollama_host)
        return self._ollama_client
    
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            client = self._get_ollama_client()
            response = client.embeddings(model=self.embedding_model, prompt=text)
            return response['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def _get_collection(self):
        """Get or create ChromaDB collection"""
        if self._collection is None:
            import chromadb
            from chromadb.config import Settings
            
            self._client = chromadb.PersistentClient(
                path=str(self.persist_dir / "chroma"),
                settings=Settings(anonymized_telemetry=False)
            )
            
            self._collection = self._client.get_or_create_collection(
                name="conversations",
                metadata={"description": "ARIA conversation history"}
            )
        return self._collection
    
    def set_session(self, session_id: str):
        """Set current session ID"""
        self._session_id = session_id
    
    def new_session(self) -> str:
        """Start a new session"""
        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self._session_id
    
    def add_turn(
        self,
        user_query: str,
        assistant_response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Add a conversation turn.
        
        Args:
            user_query: User's message
            assistant_response: Assistant's response
            metadata: Optional metadata (files discussed, actions taken, etc.)
            
        Returns:
            Turn ID
        """
        timestamp = datetime.now().isoformat()
        metadata = metadata or {}
        
        # Store in SQLite first
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations 
            (timestamp, user_query, assistant_response, session_id, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            timestamp,
            user_query,
            assistant_response,
            self._session_id,
            json.dumps(metadata),
        ))
        
        turn_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Generate embedding for semantic search
        # Combine query and response for context
        combined_text = f"User: {user_query}\nAssistant: {assistant_response[:500]}"
        
        try:
            embedding = self._get_embedding(combined_text)
            
            collection = self._get_collection()
            embedding_id = f"turn_{turn_id}"
            
            collection.add(
                ids=[embedding_id],
                embeddings=[embedding],
                documents=[combined_text],
                metadatas=[{
                    "turn_id": turn_id,
                    "timestamp": timestamp,
                    "session_id": self._session_id,
                    "query_preview": user_query[:200],
                    "response_preview": assistant_response[:200],
                }]
            )
            
            # Update SQLite with embedding ID
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE conversations SET embedding_id = ? WHERE id = ?',
                (embedding_id, turn_id)
            )
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.warning(f"Could not create embedding for turn {turn_id}: {e}")
        
        return turn_id
    
    def search(
        self,
        query: str,
        limit: int = 5,
        session_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant past conversations.
        
        Args:
            query: Search query
            limit: Maximum results
            session_filter: Optional session ID to filter by
            
        Returns:
            List of relevant conversation turns with scores
        """
        try:
            collection = self._get_collection()
            
            # Generate query embedding
            query_embedding = self._get_embedding(query)
            
            # Build where filter
            where = None
            if session_filter:
                where = {"session_id": session_filter}
            
            # Query collection
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted = []
            if results['metadatas'] and results['metadatas'][0]:
                for i, metadata in enumerate(results['metadatas'][0]):
                    distance = results['distances'][0][i] if results['distances'] else 0
                    score = 1 / (1 + distance)
                    
                    # Get full conversation from SQLite
                    turn_id = metadata.get("turn_id")
                    full_turn = self._get_turn_by_id(turn_id) if turn_id else None
                    
                    formatted.append({
                        "turn_id": turn_id,
                        "query": full_turn.get("user_query", metadata.get("query_preview", "")) if full_turn else metadata.get("query_preview", ""),
                        "response": full_turn.get("assistant_response", metadata.get("response_preview", "")) if full_turn else metadata.get("response_preview", ""),
                        "timestamp": metadata.get("timestamp", ""),
                        "session_id": metadata.get("session_id", ""),
                        "score": score,
                    })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error searching conversations: {e}")
            return []
    
    def _get_turn_by_id(self, turn_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific turn by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT * FROM conversations WHERE id = ?',
                (turn_id,)
            )
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "id": row[0],
                    "timestamp": row[1],
                    "user_query": row[2],
                    "assistant_response": row[3],
                    "session_id": row[4],
                    "metadata": json.loads(row[5]) if row[5] else {},
                }
            return None
        except:
            return None
    
    def get_session_history(
        self,
        session_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session ID (default: current session)
            limit: Maximum turns to return
            
        Returns:
            List of conversation turns in chronological order
        """
        session_id = session_id or self._session_id
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM conversations 
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (session_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        turns = []
        for row in reversed(rows):  # Reverse to get chronological order
            turns.append({
                "id": row[0],
                "timestamp": row[1],
                "user_query": row[2],
                "assistant_response": row[3],
                "session_id": row[4],
                "metadata": json.loads(row[5]) if row[5] else {},
            })
        
        return turns
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get list of recent sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id, 
                   MIN(timestamp) as started,
                   MAX(timestamp) as last_activity,
                   COUNT(*) as turn_count
            FROM conversations
            GROUP BY session_id
            ORDER BY last_activity DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "session_id": row[0],
                "started": row[1],
                "last_activity": row[2],
                "turn_count": row[3],
            }
            for row in rows
        ]
    
    def count(self) -> int:
        """Get total number of stored turns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM conversations')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def clear(self, session_id: Optional[str] = None):
        """
        Clear conversation history.
        
        Args:
            session_id: If provided, only clear this session. Otherwise clear all.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute('DELETE FROM conversations WHERE session_id = ?', (session_id,))
        else:
            cursor.execute('DELETE FROM conversations')
        
        conn.commit()
        conn.close()
        
        # Clear ChromaDB
        try:
            if self._client:
                self._client.delete_collection("conversations")
                self._collection = None
        except Exception as e:
            logger.warning(f"Could not clear ChromaDB collection: {e}")
        
        logger.info(f"Cleared conversation history" + (f" for session {session_id}" if session_id else ""))
    
    def export_session(self, session_id: str) -> Dict[str, Any]:
        """Export a session as JSON"""
        turns = self.get_session_history(session_id, limit=1000)
        return {
            "session_id": session_id,
            "exported_at": datetime.now().isoformat(),
            "turns": turns,
        }
    
    def import_session(self, data: Dict[str, Any]) -> int:
        """
        Import a session from JSON.
        
        Returns:
            Number of turns imported
        """
        turns = data.get("turns", [])
        imported = 0
        
        for turn in turns:
            self.add_turn(
                user_query=turn.get("user_query", ""),
                assistant_response=turn.get("assistant_response", ""),
                metadata=turn.get("metadata", {}),
            )
            imported += 1
        
        return imported
