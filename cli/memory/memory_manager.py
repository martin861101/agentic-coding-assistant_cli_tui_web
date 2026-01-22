"""
Memory Manager - Core orchestrator for ARIA's RAG memory system

Coordinates:
- Codebase indexing and retrieval
- Conversation history storage
- Context assembly for LLM calls
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RetrievedContext:
    """Container for retrieved context"""
    code_snippets: List[Dict[str, Any]]
    conversations: List[Dict[str, Any]]
    project_info: Dict[str, Any]
    total_tokens_estimate: int
    
    def to_prompt_section(self, max_tokens: int = 4000) -> str:
        """Convert to a prompt section string"""
        sections = []
        current_tokens = 0
        
        # Add project info first (small, always useful)
        if self.project_info:
            project_section = self._format_project_info()
            sections.append(project_section)
            current_tokens += len(project_section) // 4  # rough estimate
        
        # Add relevant code snippets
        if self.code_snippets:
            code_section = self._format_code_snippets(max_tokens - current_tokens)
            if code_section:
                sections.append(code_section)
                current_tokens += len(code_section) // 4
        
        # Add relevant past conversations
        if self.conversations and current_tokens < max_tokens:
            convo_section = self._format_conversations(max_tokens - current_tokens)
            if convo_section:
                sections.append(convo_section)
        
        if not sections:
            return ""
        
        return "\n\n---\n**Retrieved Context:**\n" + "\n\n".join(sections)
    
    def _format_project_info(self) -> str:
        """Format project info section"""
        info = self.project_info
        parts = ["**Project:**"]
        
        if info.get("name"):
            parts.append(f"- Name: {info['name']}")
        if info.get("languages"):
            parts.append(f"- Languages: {', '.join(info['languages'])}")
        if info.get("frameworks"):
            parts.append(f"- Frameworks: {', '.join(info['frameworks'])}")
        if info.get("description"):
            parts.append(f"- Description: {info['description']}")
            
        return "\n".join(parts) if len(parts) > 1 else ""
    
    def _format_code_snippets(self, max_tokens: int) -> str:
        """Format code snippets section"""
        if not self.code_snippets:
            return ""
        
        parts = ["**Relevant Code:**"]
        current_tokens = 0
        
        for snippet in self.code_snippets[:5]:  # Max 5 snippets
            file_path = snippet.get("file_path", "unknown")
            content = snippet.get("content", "")
            score = snippet.get("score", 0)
            
            # Estimate tokens
            snippet_tokens = len(content) // 4
            if current_tokens + snippet_tokens > max_tokens:
                break
            
            parts.append(f"\n`{file_path}` (relevance: {score:.2f}):")
            parts.append(f"```\n{content[:1500]}\n```")
            current_tokens += snippet_tokens
        
        return "\n".join(parts) if len(parts) > 1 else ""
    
    def _format_conversations(self, max_tokens: int) -> str:
        """Format past conversations section"""
        if not self.conversations:
            return ""
        
        parts = ["**Relevant Past Discussions:**"]
        current_tokens = 0
        
        for convo in self.conversations[:3]:  # Max 3 past conversations
            query = convo.get("query", "")
            response = convo.get("response", "")[:500]
            
            snippet_tokens = (len(query) + len(response)) // 4
            if current_tokens + snippet_tokens > max_tokens:
                break
            
            parts.append(f"\n- Q: {query[:200]}")
            parts.append(f"  A: {response}...")
            current_tokens += snippet_tokens
        
        return "\n".join(parts) if len(parts) > 1 else ""


class MemoryManager:
    """
    Central orchestrator for ARIA's memory system.
    
    Manages:
    - Codebase indexing (RAG for project files)
    - Conversation memory (past chat retrieval)
    - Project context (structure, dependencies)
    """
    
    def __init__(
        self,
        data_dir: Path,
        embedding_model: str = "nomic-embed-text",
        ollama_host: str = "http://localhost:11434"
    ):
        self.data_dir = Path(data_dir)
        self.embedding_model = embedding_model
        self.ollama_host = ollama_host
        
        # Ensure directories exist
        self.memory_dir = self.data_dir / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Lazy-loaded components
        self._codebase_index = None
        self._conversation_store = None
        self._retriever = None
        self._embeddings_available = None
        
        # Project context cache
        self._project_context: Dict[str, Any] = {}
        
        logger.info(f"MemoryManager initialized with data_dir: {self.data_dir}")
    
    @property
    def embeddings_available(self) -> bool:
        """Check if embedding model is available"""
        if self._embeddings_available is None:
            self._embeddings_available = self._check_embeddings()
        return self._embeddings_available
    
    def _check_embeddings(self) -> bool:
        """Check if Ollama embeddings are available"""
        try:
            import ollama
            client = ollama.Client(host=self.ollama_host)
            # Try to generate a test embedding
            client.embeddings(model=self.embedding_model, prompt="test")
            logger.info(f"Embeddings available with model: {self.embedding_model}")
            return True
        except Exception as e:
            logger.warning(f"Embeddings not available: {e}")
            return False
    
    @property
    def codebase_index(self):
        """Lazy-load codebase index"""
        if self._codebase_index is None:
            from .codebase_index import CodebaseIndex
            self._codebase_index = CodebaseIndex(
                persist_dir=self.memory_dir / "codebase",
                embedding_model=self.embedding_model,
                ollama_host=self.ollama_host
            )
        return self._codebase_index
    
    @property
    def conversation_store(self):
        """Lazy-load conversation store"""
        if self._conversation_store is None:
            from .conversation_store import ConversationStore
            self._conversation_store = ConversationStore(
                persist_dir=self.memory_dir / "conversations",
                embedding_model=self.embedding_model,
                ollama_host=self.ollama_host
            )
        return self._conversation_store
    
    @property
    def retriever(self):
        """Lazy-load unified retriever"""
        if self._retriever is None:
            from .retriever import Retriever
            self._retriever = Retriever(
                codebase_index=self.codebase_index,
                conversation_store=self.conversation_store,
                memory_manager=self
            )
        return self._retriever
    
    def index_project(self, project_path: Path, force: bool = False) -> Dict[str, Any]:
        """
        Index a project directory for RAG retrieval.
        
        Args:
            project_path: Path to project root
            force: Force re-index even if already indexed
            
        Returns:
            Indexing statistics
        """
        if not self.embeddings_available:
            logger.warning("Embeddings not available, skipping indexing")
            return {"status": "skipped", "reason": "embeddings_unavailable"}
        
        return self.codebase_index.index_directory(project_path, force=force)
    
    def store_conversation(
        self,
        user_query: str,
        assistant_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Store a conversation turn for future retrieval"""
        if not self.embeddings_available:
            return
        
        self.conversation_store.add_turn(
            user_query=user_query,
            assistant_response=assistant_response,
            metadata=metadata or {}
        )
    
    def retrieve_context(
        self,
        query: str,
        project_path: Optional[Path] = None,
        max_code_results: int = 5,
        max_conversation_results: int = 3
    ) -> RetrievedContext:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: The user's query
            project_path: Current project path (for project info)
            max_code_results: Maximum code snippets to retrieve
            max_conversation_results: Maximum past conversations
            
        Returns:
            RetrievedContext with all relevant information
        """
        return self.retriever.retrieve(
            query=query,
            project_path=project_path,
            max_code_results=max_code_results,
            max_conversation_results=max_conversation_results
        )
    
    def get_project_context(self, project_path: Path) -> Dict[str, Any]:
        """Get or build project context"""
        path_key = str(project_path.absolute())
        
        if path_key not in self._project_context:
            self._project_context[path_key] = self._analyze_project(project_path)
        
        return self._project_context[path_key]
    
    def _analyze_project(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project structure and detect frameworks"""
        context = {
            "name": project_path.name,
            "path": str(project_path),
            "languages": [],
            "frameworks": [],
            "description": "",
            "files_count": 0,
        }
        
        try:
            # Detect languages by file extensions
            extensions = set()
            for f in project_path.rglob("*"):
                if f.is_file() and not any(p.startswith('.') for p in f.parts):
                    extensions.add(f.suffix.lower())
                    context["files_count"] += 1
            
            lang_map = {
                '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
                '.go': 'Go', '.rs': 'Rust', '.java': 'Java', '.rb': 'Ruby',
                '.php': 'PHP', '.c': 'C', '.cpp': 'C++', '.cs': 'C#',
            }
            context["languages"] = [lang_map[ext] for ext in extensions if ext in lang_map]
            
            # Detect frameworks
            if (project_path / "package.json").exists():
                context["frameworks"].append("Node.js")
                try:
                    import json
                    pkg = json.loads((project_path / "package.json").read_text())
                    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                    if "react" in deps:
                        context["frameworks"].append("React")
                    if "vue" in deps:
                        context["frameworks"].append("Vue")
                    if "next" in deps:
                        context["frameworks"].append("Next.js")
                    if "express" in deps:
                        context["frameworks"].append("Express")
                except:
                    pass
            
            if (project_path / "requirements.txt").exists():
                context["frameworks"].append("Python")
                try:
                    reqs = (project_path / "requirements.txt").read_text().lower()
                    if "fastapi" in reqs:
                        context["frameworks"].append("FastAPI")
                    if "flask" in reqs:
                        context["frameworks"].append("Flask")
                    if "django" in reqs:
                        context["frameworks"].append("Django")
                    if "pytest" in reqs:
                        context["frameworks"].append("pytest")
                except:
                    pass
            
            if (project_path / "pyproject.toml").exists():
                context["frameworks"].append("Python (pyproject)")
            
            if (project_path / "Cargo.toml").exists():
                context["frameworks"].append("Rust/Cargo")
            
            if (project_path / "go.mod").exists():
                context["frameworks"].append("Go Modules")
            
            # Read README for description
            for readme_name in ["README.md", "README.rst", "README.txt", "README"]:
                readme_path = project_path / readme_name
                if readme_path.exists():
                    try:
                        content = readme_path.read_text()[:500]
                        # Get first paragraph
                        lines = content.split('\n')
                        desc_lines = []
                        for line in lines:
                            if line.strip() and not line.startswith('#'):
                                desc_lines.append(line.strip())
                                if len(' '.join(desc_lines)) > 200:
                                    break
                        context["description"] = ' '.join(desc_lines)[:200]
                    except:
                        pass
                    break
        
        except Exception as e:
            logger.warning(f"Error analyzing project: {e}")
        
        return context
    
    def clear_memory(self, what: str = "all"):
        """
        Clear memory stores.
        
        Args:
            what: "all", "codebase", "conversations"
        """
        if what in ("all", "codebase"):
            if self._codebase_index:
                self._codebase_index.clear()
        
        if what in ("all", "conversations"):
            if self._conversation_store:
                self._conversation_store.clear()
        
        if what == "all":
            self._project_context = {}
        
        logger.info(f"Cleared memory: {what}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        stats = {
            "embeddings_available": self.embeddings_available,
            "codebase_indexed": False,
            "codebase_chunks": 0,
            "conversations_stored": 0,
            "project_contexts_cached": len(self._project_context),
        }
        
        try:
            if self._codebase_index:
                codebase_stats = self._codebase_index.get_stats()
                stats["codebase_indexed"] = codebase_stats.get("indexed", False)
                stats["codebase_chunks"] = codebase_stats.get("total_chunks", 0)
        except:
            pass
        
        try:
            if self._conversation_store:
                stats["conversations_stored"] = self._conversation_store.count()
        except:
            pass
        
        return stats
