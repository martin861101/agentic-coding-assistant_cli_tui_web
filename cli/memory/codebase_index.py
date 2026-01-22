"""
Codebase Index - RAG for project files

Indexes project files into chunks and enables semantic search
to retrieve relevant code snippets for LLM context.
"""

import hashlib
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

# File patterns to index
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java',
    '.c', '.cpp', '.h', '.hpp', '.cs', '.rb', '.php', '.swift',
    '.kt', '.scala', '.sh', '.bash', '.zsh', '.sql', '.r',
}

CONFIG_EXTENSIONS = {
    '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
    '.env.example', '.gitignore', '.dockerignore',
}

DOC_EXTENSIONS = {
    '.md', '.rst', '.txt',
}

# Directories to skip
SKIP_DIRS = {
    '.git', 'node_modules', '__pycache__', '.venv', 'venv', 'env',
    '.env', 'dist', 'build', '.next', '.nuxt', 'target', 'vendor',
    '.idea', '.vscode', '.pytest_cache', '.mypy_cache', 'coverage',
    'htmlcov', '.tox', 'eggs', '*.egg-info', '.cache',
}


@dataclass
class CodeChunk:
    """A chunk of code for indexing"""
    content: str
    file_path: str
    chunk_type: str  # function, class, module, config
    start_line: int
    end_line: int
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "file_path": self.file_path,
            "chunk_type": self.chunk_type,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "name": self.name,
            "metadata": self.metadata or {},
        }


class CodeChunker:
    """Chunks code files into semantic units"""
    
    def __init__(self, chunk_size: int = 1500, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_file(self, file_path: Path) -> List[CodeChunk]:
        """Chunk a single file into semantic units"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return []
        
        suffix = file_path.suffix.lower()
        
        # Use language-specific chunking for code files
        if suffix == '.py':
            chunks = self._chunk_python(content, str(file_path))
        elif suffix in {'.js', '.ts', '.jsx', '.tsx'}:
            chunks = self._chunk_javascript(content, str(file_path))
        elif suffix in CONFIG_EXTENSIONS:
            chunks = self._chunk_config(content, str(file_path))
        elif suffix in DOC_EXTENSIONS:
            chunks = self._chunk_markdown(content, str(file_path))
        else:
            chunks = self._chunk_generic(content, str(file_path))
        
        return chunks
    
    def _chunk_python(self, content: str, file_path: str) -> List[CodeChunk]:
        """Chunk Python code by functions and classes"""
        chunks = []
        lines = content.split('\n')
        
        # Pattern for function and class definitions
        func_pattern = re.compile(r'^(\s*)(async\s+)?def\s+(\w+)')
        class_pattern = re.compile(r'^(\s*)class\s+(\w+)')
        
        current_chunk_lines = []
        current_name = None
        current_type = "module"
        current_start = 0
        current_indent = 0
        
        for i, line in enumerate(lines):
            func_match = func_pattern.match(line)
            class_match = class_pattern.match(line)
            
            # Check if we're starting a new definition
            if func_match or class_match:
                indent = len(func_match.group(1) if func_match else class_match.group(1))
                
                # If we have accumulated content, save it
                if current_chunk_lines and indent <= current_indent:
                    chunk_content = '\n'.join(current_chunk_lines)
                    if chunk_content.strip():
                        chunks.append(CodeChunk(
                            content=chunk_content,
                            file_path=file_path,
                            chunk_type=current_type,
                            start_line=current_start + 1,
                            end_line=i,
                            name=current_name,
                        ))
                    current_chunk_lines = []
                
                # Start new chunk
                if not current_chunk_lines:
                    current_start = i
                    current_indent = indent
                    if func_match:
                        current_name = func_match.group(3)
                        current_type = "function"
                    else:
                        current_name = class_match.group(2)
                        current_type = "class"
            
            current_chunk_lines.append(line)
            
            # Check if chunk is getting too large
            if len('\n'.join(current_chunk_lines)) > self.chunk_size:
                chunk_content = '\n'.join(current_chunk_lines)
                chunks.append(CodeChunk(
                    content=chunk_content,
                    file_path=file_path,
                    chunk_type=current_type,
                    start_line=current_start + 1,
                    end_line=i + 1,
                    name=current_name,
                ))
                # Keep some overlap
                overlap_lines = max(5, self.overlap // 50)
                current_chunk_lines = current_chunk_lines[-overlap_lines:]
                current_start = i - overlap_lines + 1
        
        # Don't forget the last chunk
        if current_chunk_lines:
            chunk_content = '\n'.join(current_chunk_lines)
            if chunk_content.strip():
                chunks.append(CodeChunk(
                    content=chunk_content,
                    file_path=file_path,
                    chunk_type=current_type,
                    start_line=current_start + 1,
                    end_line=len(lines),
                    name=current_name,
                ))
        
        # If no chunks created, chunk the whole file
        if not chunks and content.strip():
            chunks = self._chunk_generic(content, file_path)
        
        return chunks
    
    def _chunk_javascript(self, content: str, file_path: str) -> List[CodeChunk]:
        """Chunk JavaScript/TypeScript code"""
        chunks = []
        lines = content.split('\n')
        
        # Patterns for functions, classes, and exports
        patterns = [
            (re.compile(r'^\s*(export\s+)?(async\s+)?function\s+(\w+)'), 'function'),
            (re.compile(r'^\s*(export\s+)?class\s+(\w+)'), 'class'),
            (re.compile(r'^\s*const\s+(\w+)\s*=\s*(async\s+)?\('), 'function'),
            (re.compile(r'^\s*(export\s+)?const\s+(\w+)\s*='), 'const'),
        ]
        
        current_chunk_lines = []
        current_start = 0
        brace_count = 0
        
        for i, line in enumerate(lines):
            current_chunk_lines.append(line)
            brace_count += line.count('{') - line.count('}')
            
            # Check if we've completed a block
            chunk_content = '\n'.join(current_chunk_lines)
            if len(chunk_content) > self.chunk_size or (brace_count == 0 and len(chunk_content) > 200):
                # Find a name for this chunk
                name = None
                chunk_type = "code"
                for pattern, ctype in patterns:
                    match = pattern.match(current_chunk_lines[0] if current_chunk_lines else "")
                    if match:
                        name = match.group(match.lastindex) if match.lastindex else None
                        chunk_type = ctype
                        break
                
                if chunk_content.strip():
                    chunks.append(CodeChunk(
                        content=chunk_content,
                        file_path=file_path,
                        chunk_type=chunk_type,
                        start_line=current_start + 1,
                        end_line=i + 1,
                        name=name,
                    ))
                
                overlap_lines = max(3, self.overlap // 50)
                current_chunk_lines = current_chunk_lines[-overlap_lines:]
                current_start = i - overlap_lines + 1
        
        # Last chunk
        if current_chunk_lines:
            chunk_content = '\n'.join(current_chunk_lines)
            if chunk_content.strip():
                chunks.append(CodeChunk(
                    content=chunk_content,
                    file_path=file_path,
                    chunk_type="code",
                    start_line=current_start + 1,
                    end_line=len(lines),
                ))
        
        if not chunks and content.strip():
            chunks = self._chunk_generic(content, file_path)
        
        return chunks
    
    def _chunk_config(self, content: str, file_path: str) -> List[CodeChunk]:
        """Chunk config files - usually keep whole"""
        if len(content) <= self.chunk_size * 2:
            return [CodeChunk(
                content=content,
                file_path=file_path,
                chunk_type="config",
                start_line=1,
                end_line=len(content.split('\n')),
                name=Path(file_path).name,
            )]
        return self._chunk_generic(content, file_path)
    
    def _chunk_markdown(self, content: str, file_path: str) -> List[CodeChunk]:
        """Chunk markdown by sections"""
        chunks = []
        sections = re.split(r'\n(#{1,3}\s+)', content)
        
        current_content = ""
        current_start = 1
        line_count = 0
        
        for section in sections:
            if section.startswith('#'):
                current_content += section
            else:
                current_content += section
                section_lines = section.count('\n') + 1
                line_count += section_lines
                
                if len(current_content) >= self.chunk_size:
                    if current_content.strip():
                        chunks.append(CodeChunk(
                            content=current_content.strip(),
                            file_path=file_path,
                            chunk_type="documentation",
                            start_line=current_start,
                            end_line=line_count,
                        ))
                    current_content = ""
                    current_start = line_count + 1
        
        if current_content.strip():
            chunks.append(CodeChunk(
                content=current_content.strip(),
                file_path=file_path,
                chunk_type="documentation",
                start_line=current_start,
                end_line=line_count,
            ))
        
        if not chunks and content.strip():
            chunks = self._chunk_generic(content, file_path)
        
        return chunks
    
    def _chunk_generic(self, content: str, file_path: str) -> List[CodeChunk]:
        """Generic chunking by size"""
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        current_start = 0
        
        for i, line in enumerate(lines):
            current_chunk.append(line)
            
            if len('\n'.join(current_chunk)) >= self.chunk_size:
                chunk_content = '\n'.join(current_chunk)
                chunks.append(CodeChunk(
                    content=chunk_content,
                    file_path=file_path,
                    chunk_type="code",
                    start_line=current_start + 1,
                    end_line=i + 1,
                ))
                overlap_lines = max(3, self.overlap // 50)
                current_chunk = current_chunk[-overlap_lines:]
                current_start = i - overlap_lines + 1
        
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            if chunk_content.strip():
                chunks.append(CodeChunk(
                    content=chunk_content,
                    file_path=file_path,
                    chunk_type="code",
                    start_line=current_start + 1,
                    end_line=len(lines),
                ))
        
        return chunks


class CodebaseIndex:
    """
    Indexes codebase for semantic search using ChromaDB.
    
    Features:
    - Smart chunking by language
    - Incremental updates (only re-index changed files)
    - Semantic search with embeddings
    """
    
    def __init__(
        self,
        persist_dir: Path,
        embedding_model: str = "nomic-embed-text",
        ollama_host: str = "http://localhost:11434",
        chunk_size: int = 1500,
    ):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.embedding_model = embedding_model
        self.ollama_host = ollama_host
        self.chunker = CodeChunker(chunk_size=chunk_size)
        
        # Initialize ChromaDB with Ollama embeddings
        self._collection = None
        self._client = None
        self._ollama_client = None
        
        # Track indexed files
        self._file_hashes: Dict[str, str] = {}
        self._load_file_hashes()
    
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
                path=str(self.persist_dir),
                settings=Settings(anonymized_telemetry=False)
            )
            
            self._collection = self._client.get_or_create_collection(
                name="codebase",
                metadata={"description": "ARIA codebase index"}
            )
        return self._collection
    
    def _load_file_hashes(self):
        """Load file hashes from disk"""
        hash_file = self.persist_dir / "file_hashes.json"
        if hash_file.exists():
            try:
                import json
                self._file_hashes = json.loads(hash_file.read_text())
            except:
                self._file_hashes = {}
    
    def _save_file_hashes(self):
        """Save file hashes to disk"""
        import json
        hash_file = self.persist_dir / "file_hashes.json"
        hash_file.write_text(json.dumps(self._file_hashes))
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Get hash of file contents"""
        content = file_path.read_bytes()
        return hashlib.md5(content).hexdigest()
    
    def _should_index_file(self, file_path: Path) -> bool:
        """Check if file should be indexed"""
        # Check extension
        suffix = file_path.suffix.lower()
        if suffix not in CODE_EXTENSIONS | CONFIG_EXTENSIONS | DOC_EXTENSIONS:
            return False
        
        # Check if in skip directory
        for part in file_path.parts:
            if part in SKIP_DIRS or part.startswith('.'):
                return False
        
        # Check file size (skip very large files)
        try:
            if file_path.stat().st_size > 500000:  # 500KB
                return False
        except:
            return False
        
        return True
    
    def _needs_reindex(self, file_path: Path) -> bool:
        """Check if file needs re-indexing"""
        path_str = str(file_path)
        try:
            current_hash = self._get_file_hash(file_path)
            return self._file_hashes.get(path_str) != current_hash
        except:
            return True
    
    def index_directory(self, directory: Path, force: bool = False) -> Dict[str, Any]:
        """
        Index all code files in a directory.
        
        Args:
            directory: Path to index
            force: Force re-index all files
            
        Returns:
            Statistics about indexing
        """
        directory = Path(directory)
        if not directory.exists():
            return {"status": "error", "message": "Directory not found"}
        
        stats = {
            "status": "success",
            "files_scanned": 0,
            "files_indexed": 0,
            "files_skipped": 0,
            "chunks_created": 0,
            "errors": [],
        }
        
        collection = self._get_collection()
        
        # Find all files to potentially index
        files_to_index: List[Path] = []
        
        for file_path in directory.rglob("*"):
            if not file_path.is_file():
                continue
            
            stats["files_scanned"] += 1
            
            if not self._should_index_file(file_path):
                stats["files_skipped"] += 1
                continue
            
            if force or self._needs_reindex(file_path):
                files_to_index.append(file_path)
            else:
                stats["files_skipped"] += 1
        
        logger.info(f"Indexing {len(files_to_index)} files from {directory}")
        
        # Index files
        for file_path in files_to_index:
            try:
                # Remove old chunks for this file
                path_str = str(file_path)
                try:
                    # Delete existing chunks for this file
                    existing = collection.get(where={"file_path": path_str})
                    if existing and existing['ids']:
                        collection.delete(ids=existing['ids'])
                except:
                    pass
                
                # Chunk the file
                chunks = self.chunker.chunk_file(file_path)
                
                if not chunks:
                    continue
                
                # Generate embeddings and add to collection
                ids = []
                embeddings = []
                documents = []
                metadatas = []
                
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{path_str}:{i}"
                    
                    try:
                        embedding = self._get_embedding(chunk.content)
                    except Exception as e:
                        logger.warning(f"Could not embed chunk from {file_path}: {e}")
                        continue
                    
                    ids.append(chunk_id)
                    embeddings.append(embedding)
                    documents.append(chunk.content)
                    metadatas.append({
                        "file_path": chunk.file_path,
                        "chunk_type": chunk.chunk_type,
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                        "name": chunk.name or "",
                        "indexed_at": datetime.now().isoformat(),
                    })
                
                if ids:
                    collection.add(
                        ids=ids,
                        embeddings=embeddings,
                        documents=documents,
                        metadatas=metadatas,
                    )
                    
                    stats["chunks_created"] += len(ids)
                    stats["files_indexed"] += 1
                    
                    # Update file hash
                    self._file_hashes[path_str] = self._get_file_hash(file_path)
                
            except Exception as e:
                logger.error(f"Error indexing {file_path}: {e}")
                stats["errors"].append(str(file_path))
        
        # Save file hashes
        self._save_file_hashes()
        
        logger.info(f"Indexing complete: {stats['files_indexed']} files, {stats['chunks_created']} chunks")
        return stats
    
    def search(
        self,
        query: str,
        limit: int = 5,
        file_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant code chunks.
        
        Args:
            query: Search query
            limit: Maximum results
            file_filter: Optional file path pattern to filter
            
        Returns:
            List of relevant code chunks with scores
        """
        try:
            collection = self._get_collection()
            
            # Generate query embedding
            query_embedding = self._get_embedding(query)
            
            # Build where filter if specified
            where = None
            if file_filter:
                where = {"file_path": {"$contains": file_filter}}
            
            # Query collection
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results['distances'] else 0
                    
                    # Convert distance to similarity score (ChromaDB uses L2 distance)
                    score = 1 / (1 + distance)
                    
                    formatted.append({
                        "content": doc,
                        "file_path": metadata.get("file_path", "unknown"),
                        "chunk_type": metadata.get("chunk_type", "code"),
                        "start_line": metadata.get("start_line", 0),
                        "end_line": metadata.get("end_line", 0),
                        "name": metadata.get("name", ""),
                        "score": score,
                    })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error searching codebase: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        try:
            collection = self._get_collection()
            count = collection.count()
            return {
                "indexed": count > 0,
                "total_chunks": count,
                "files_tracked": len(self._file_hashes),
            }
        except:
            return {
                "indexed": False,
                "total_chunks": 0,
                "files_tracked": 0,
            }
    
    def clear(self):
        """Clear the entire index"""
        try:
            if self._client and self._collection:
                self._client.delete_collection("codebase")
                self._collection = None
            self._file_hashes = {}
            self._save_file_hashes()
            logger.info("Codebase index cleared")
        except Exception as e:
            logger.error(f"Error clearing index: {e}")
