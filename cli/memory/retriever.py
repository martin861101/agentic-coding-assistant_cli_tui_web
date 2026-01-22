"""
Retriever - Unified retrieval interface for ARIA's memory system

Combines results from all memory sources:
- Codebase index (code snippets)
- Conversation store (past discussions)
- Project context (structure, frameworks)
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .codebase_index import CodebaseIndex
    from .conversation_store import ConversationStore
    from .memory_manager import MemoryManager, RetrievedContext

logger = logging.getLogger(__name__)


class Retriever:
    """
    Unified retrieval interface that combines all memory sources.
    
    Provides a single method to retrieve relevant context from:
    - Codebase (semantic code search)
    - Past conversations (similar discussions)
    - Project context (frameworks, structure)
    """
    
    def __init__(
        self,
        codebase_index: "CodebaseIndex",
        conversation_store: "ConversationStore",
        memory_manager: "MemoryManager",
    ):
        self.codebase_index = codebase_index
        self.conversation_store = conversation_store
        self.memory_manager = memory_manager
    
    def retrieve(
        self,
        query: str,
        project_path: Optional[Path] = None,
        max_code_results: int = 5,
        max_conversation_results: int = 3,
        include_code: bool = True,
        include_conversations: bool = True,
        include_project_info: bool = True,
    ) -> "RetrievedContext":
        """
        Retrieve relevant context for a query.
        
        Args:
            query: The user's query
            project_path: Current project path
            max_code_results: Maximum code snippets
            max_conversation_results: Maximum past conversations
            include_code: Whether to include code search
            include_conversations: Whether to include past conversations
            include_project_info: Whether to include project info
            
        Returns:
            RetrievedContext with all relevant information
        """
        from .memory_manager import RetrievedContext
        
        code_snippets = []
        conversations = []
        project_info = {}
        total_tokens = 0
        
        # 1. Search codebase for relevant code
        if include_code:
            try:
                code_snippets = self.codebase_index.search(
                    query=query,
                    limit=max_code_results,
                )
                # Estimate tokens
                for snippet in code_snippets:
                    total_tokens += len(snippet.get("content", "")) // 4
            except Exception as e:
                logger.warning(f"Codebase search failed: {e}")
        
        # 2. Search past conversations
        if include_conversations:
            try:
                conversations = self.conversation_store.search(
                    query=query,
                    limit=max_conversation_results,
                )
                # Estimate tokens
                for convo in conversations:
                    total_tokens += (len(convo.get("query", "")) + len(convo.get("response", ""))) // 4
            except Exception as e:
                logger.warning(f"Conversation search failed: {e}")
        
        # 3. Get project context
        if include_project_info and project_path:
            try:
                project_info = self.memory_manager.get_project_context(Path(project_path))
                total_tokens += 100  # Rough estimate for project info
            except Exception as e:
                logger.warning(f"Project context retrieval failed: {e}")
        
        return RetrievedContext(
            code_snippets=code_snippets,
            conversations=conversations,
            project_info=project_info,
            total_tokens_estimate=total_tokens,
        )
    
    def retrieve_for_file(
        self,
        file_path: str,
        query: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve context specifically for a file.
        
        Args:
            file_path: The file being discussed
            query: Optional additional query
            limit: Maximum results
            
        Returns:
            List of relevant code chunks from the file
        """
        try:
            # Search for chunks from this file
            results = self.codebase_index.search(
                query=query or f"code in {file_path}",
                limit=limit,
                file_filter=file_path,
            )
            return results
        except Exception as e:
            logger.warning(f"File-specific retrieval failed: {e}")
            return []
    
    def retrieve_similar_code(
        self,
        code_snippet: str,
        limit: int = 3,
        exclude_file: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find similar code in the codebase.
        
        Useful for:
        - Finding related implementations
        - Detecting duplicates
        - Understanding patterns
        
        Args:
            code_snippet: The code to find similarities for
            limit: Maximum results
            exclude_file: File to exclude from results
            
        Returns:
            List of similar code chunks
        """
        try:
            results = self.codebase_index.search(
                query=code_snippet,
                limit=limit + 1,  # Get extra in case we exclude
            )
            
            if exclude_file:
                results = [r for r in results if r.get("file_path") != exclude_file]
            
            return results[:limit]
        except Exception as e:
            logger.warning(f"Similar code search failed: {e}")
            return []
    
    def retrieve_by_topic(
        self,
        topic: str,
        limit: int = 5,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieve context by topic across all sources.
        
        Args:
            topic: The topic to search for
            limit: Maximum results per source
            
        Returns:
            Dict with 'code' and 'conversations' keys
        """
        code = []
        conversations = []
        
        try:
            code = self.codebase_index.search(query=topic, limit=limit)
        except:
            pass
        
        try:
            conversations = self.conversation_store.search(query=topic, limit=limit)
        except:
            pass
        
        return {
            "code": code,
            "conversations": conversations,
        }
    
    def get_context_summary(
        self,
        query: str,
        project_path: Optional[Path] = None,
    ) -> str:
        """
        Get a brief summary of available context.
        
        Useful for quick context checks without full retrieval.
        """
        context = self.retrieve(
            query=query,
            project_path=project_path,
            max_code_results=3,
            max_conversation_results=2,
        )
        
        summary_parts = []
        
        if context.code_snippets:
            files = list(set(s.get("file_path", "") for s in context.code_snippets))
            summary_parts.append(f"Found relevant code in: {', '.join(files[:3])}")
        
        if context.conversations:
            summary_parts.append(f"Found {len(context.conversations)} related past discussions")
        
        if context.project_info:
            info = context.project_info
            if info.get("frameworks"):
                summary_parts.append(f"Project uses: {', '.join(info['frameworks'][:3])}")
        
        return "; ".join(summary_parts) if summary_parts else "No relevant context found"
