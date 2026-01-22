"""
Graphiti Memory Integration
===========================

Bridges the Graphiti knowledge graph memory system with ARIA.
Provides context retrieval and session memory storage.
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Try to import from backend
try:
    BACKEND_PATH = Path(__file__).parent.parent / "Auto-Claude" / "apps" / "backend"
    if BACKEND_PATH.exists() and str(BACKEND_PATH) not in sys.path:
        sys.path.insert(0, str(BACKEND_PATH))
    
    from agents.memory_manager import (
        get_graphiti_context as _get_graphiti_context,
        save_session_memory as _save_session_memory,
        debug_memory_system_status as _debug_memory_status,
    )
    GRAPHITI_BACKEND_AVAILABLE = True
except ImportError:
    GRAPHITI_BACKEND_AVAILABLE = False


def is_graphiti_available() -> bool:
    """Check if Graphiti MCP is available and configured."""
    url = os.environ.get("GRAPHITI_MCP_URL")
    return bool(url) and GRAPHITI_BACKEND_AVAILABLE


class GraphitiMemoryManager:
    """
    Manages memory through Graphiti knowledge graph.
    
    Provides:
    - Session memory storage (discoveries, patterns, gotchas)
    - Context retrieval for agent prompts
    - Fallback to file-based memory when Graphiti unavailable
    """
    
    def __init__(self, spec_dir: Path, project_dir: Optional[Path] = None):
        """
        Initialize the memory manager.
        
        Args:
            spec_dir: Directory containing the spec
            project_dir: Root project directory
        """
        self.spec_dir = Path(spec_dir)
        self.project_dir = Path(project_dir) if project_dir else self.spec_dir.parent.parent.parent
        self.memory_dir = self.spec_dir / "memory"
        self.memory_dir.mkdir(exist_ok=True)
        
        self._graphiti_available = is_graphiti_available()
    
    @property
    def is_graphiti_enabled(self) -> bool:
        """Check if Graphiti is enabled and available."""
        return self._graphiti_available
    
    async def get_context(
        self,
        subtask: Optional[Dict[str, Any]] = None,
        query: Optional[str] = None,
    ) -> str:
        """
        Retrieve context from memory for a subtask or query.
        
        Args:
            subtask: Optional subtask dict with id and description
            query: Optional explicit query string
            
        Returns:
            Formatted context string to append to prompts
        """
        if self._graphiti_available and GRAPHITI_BACKEND_AVAILABLE:
            try:
                context = await _get_graphiti_context(
                    self.spec_dir,
                    self.project_dir,
                    subtask or {"description": query, "id": "query"},
                )
                if context:
                    return context
            except Exception as e:
                print(f"Warning: Graphiti context retrieval failed: {e}")
        
        # Fallback to file-based memory
        return self._get_file_based_context(subtask, query)
    
    def _get_file_based_context(
        self,
        subtask: Optional[Dict[str, Any]] = None,
        query: Optional[str] = None,
    ) -> str:
        """Retrieve context from file-based memory."""
        context_parts = []
        
        # Load discoveries
        discoveries_file = self.memory_dir / "discoveries.json"
        if discoveries_file.exists():
            try:
                discoveries = json.loads(discoveries_file.read_text())
                if discoveries:
                    context_parts.append("## Previous Discoveries")
                    for d in discoveries[-10:]:  # Last 10 discoveries
                        context_parts.append(f"- {d.get('content', d)}")
            except json.JSONDecodeError:
                pass
        
        # Load gotchas (common pitfalls)
        gotchas_file = self.memory_dir / "gotchas.json"
        if gotchas_file.exists():
            try:
                gotchas = json.loads(gotchas_file.read_text())
                if gotchas:
                    context_parts.append("\n## Known Gotchas (Watch Out!)")
                    for g in gotchas[-5:]:  # Last 5 gotchas
                        context_parts.append(f"- {g.get('content', g)}")
            except json.JSONDecodeError:
                pass
        
        # Load patterns
        patterns_file = self.memory_dir / "patterns.json"
        if patterns_file.exists():
            try:
                patterns = json.loads(patterns_file.read_text())
                if patterns:
                    context_parts.append("\n## Established Patterns")
                    for p in patterns[-5:]:
                        context_parts.append(f"- {p.get('pattern', p)}")
            except json.JSONDecodeError:
                pass
        
        return "\n".join(context_parts) if context_parts else ""
    
    async def save_session(
        self,
        subtask_id: str,
        session_num: int,
        success: bool,
        discoveries: Optional[List[Dict[str, Any]]] = None,
        patterns: Optional[List[str]] = None,
        gotchas: Optional[List[str]] = None,
    ) -> tuple[bool, str]:
        """
        Save session memory.
        
        Args:
            subtask_id: ID of the subtask worked on
            session_num: Session number
            success: Whether the session succeeded
            discoveries: Optional list of discoveries
            patterns: Optional list of patterns discovered
            gotchas: Optional list of gotchas encountered
            
        Returns:
            Tuple of (success, storage_type)
        """
        if self._graphiti_available and GRAPHITI_BACKEND_AVAILABLE:
            try:
                return await _save_session_memory(
                    spec_dir=self.spec_dir,
                    project_dir=self.project_dir,
                    subtask_id=subtask_id,
                    session_num=session_num,
                    success=success,
                    subtasks_completed=[subtask_id] if success else [],
                    discoveries={"file_insights": discoveries or [], "patterns_discovered": patterns or []},
                )
            except Exception as e:
                print(f"Warning: Graphiti save failed, using file fallback: {e}")
        
        # File-based fallback
        return self._save_file_based(
            subtask_id=subtask_id,
            session_num=session_num,
            success=success,
            discoveries=discoveries,
            patterns=patterns,
            gotchas=gotchas,
        )
    
    def _save_file_based(
        self,
        subtask_id: str,
        session_num: int,
        success: bool,
        discoveries: Optional[List[Dict[str, Any]]] = None,
        patterns: Optional[List[str]] = None,
        gotchas: Optional[List[str]] = None,
    ) -> tuple[bool, str]:
        """Save session memory to files."""
        try:
            timestamp = datetime.now().isoformat()
            
            # Save discoveries
            if discoveries:
                discoveries_file = self.memory_dir / "discoveries.json"
                existing = []
                if discoveries_file.exists():
                    try:
                        existing = json.loads(discoveries_file.read_text())
                    except json.JSONDecodeError:
                        existing = []
                
                for d in discoveries:
                    existing.append({
                        "content": d.get("content", str(d)),
                        "subtask_id": subtask_id,
                        "session": session_num,
                        "timestamp": timestamp,
                    })
                
                discoveries_file.write_text(json.dumps(existing, indent=2))
            
            # Save patterns
            if patterns:
                patterns_file = self.memory_dir / "patterns.json"
                existing = []
                if patterns_file.exists():
                    try:
                        existing = json.loads(patterns_file.read_text())
                    except json.JSONDecodeError:
                        existing = []
                
                for p in patterns:
                    existing.append({
                        "pattern": p,
                        "subtask_id": subtask_id,
                        "session": session_num,
                        "timestamp": timestamp,
                    })
                
                patterns_file.write_text(json.dumps(existing, indent=2))
            
            # Save gotchas
            if gotchas:
                gotchas_file = self.memory_dir / "gotchas.json"
                existing = []
                if gotchas_file.exists():
                    try:
                        existing = json.loads(gotchas_file.read_text())
                    except json.JSONDecodeError:
                        existing = []
                
                for g in gotchas:
                    existing.append({
                        "content": g,
                        "subtask_id": subtask_id,
                        "session": session_num,
                        "timestamp": timestamp,
                    })
                
                gotchas_file.write_text(json.dumps(existing, indent=2))
            
            # Save session log
            sessions_file = self.memory_dir / "sessions.json"
            sessions = []
            if sessions_file.exists():
                try:
                    sessions = json.loads(sessions_file.read_text())
                except json.JSONDecodeError:
                    sessions = []
            
            sessions.append({
                "session": session_num,
                "subtask_id": subtask_id,
                "success": success,
                "timestamp": timestamp,
                "discoveries_count": len(discoveries or []),
                "patterns_count": len(patterns or []),
                "gotchas_count": len(gotchas or []),
            })
            
            sessions_file.write_text(json.dumps(sessions, indent=2))
            
            return True, "file"
            
        except Exception as e:
            print(f"Error saving file-based memory: {e}")
            return False, "none"
    
    def record_discovery(self, content: str, category: str = "general") -> bool:
        """Record a discovery for future reference."""
        discoveries_file = self.memory_dir / "discoveries.json"
        existing = []
        if discoveries_file.exists():
            try:
                existing = json.loads(discoveries_file.read_text())
            except json.JSONDecodeError:
                existing = []
        
        existing.append({
            "content": content,
            "category": category,
            "timestamp": datetime.now().isoformat(),
        })
        
        discoveries_file.write_text(json.dumps(existing, indent=2))
        return True
    
    def record_gotcha(self, content: str) -> bool:
        """Record a gotcha (common pitfall) for future reference."""
        gotchas_file = self.memory_dir / "gotchas.json"
        existing = []
        if gotchas_file.exists():
            try:
                existing = json.loads(gotchas_file.read_text())
            except json.JSONDecodeError:
                existing = []
        
        existing.append({
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        
        gotchas_file.write_text(json.dumps(existing, indent=2))
        return True
    
    def clear_memory(self) -> bool:
        """Clear all memory for this spec."""
        try:
            for file in self.memory_dir.glob("*.json"):
                file.unlink()
            return True
        except Exception:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        stats = {
            "graphiti_enabled": self._graphiti_available,
            "discoveries_count": 0,
            "patterns_count": 0,
            "gotchas_count": 0,
            "sessions_count": 0,
        }
        
        discoveries_file = self.memory_dir / "discoveries.json"
        if discoveries_file.exists():
            try:
                discoveries = json.loads(discoveries_file.read_text())
                stats["discoveries_count"] = len(discoveries)
            except json.JSONDecodeError:
                pass
        
        patterns_file = self.memory_dir / "patterns.json"
        if patterns_file.exists():
            try:
                patterns = json.loads(patterns_file.read_text())
                stats["patterns_count"] = len(patterns)
            except json.JSONDecodeError:
                pass
        
        gotchas_file = self.memory_dir / "gotchas.json"
        if gotchas_file.exists():
            try:
                gotchas = json.loads(gotchas_file.read_text())
                stats["gotchas_count"] = len(gotchas)
            except json.JSONDecodeError:
                pass
        
        sessions_file = self.memory_dir / "sessions.json"
        if sessions_file.exists():
            try:
                sessions = json.loads(sessions_file.read_text())
                stats["sessions_count"] = len(sessions)
            except json.JSONDecodeError:
                pass
        
        return stats
