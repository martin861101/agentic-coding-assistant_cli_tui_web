"""
File system operation tools
"""
import os
from pathlib import Path
from typing import Optional, List
from .base import Tool, ToolResult
import logging

logger = logging.getLogger(__name__)

# Directories that should never be accessed
RESTRICTED_PATHS = [
    '/etc/passwd', '/etc/shadow', '/etc/sudoers',
    '/root/.ssh', '/home/*/.ssh/id_rsa', '/home/*/.ssh/id_ed25519',
]

# File extensions that are dangerous to write
DANGEROUS_EXTENSIONS = ['.sh', '.bash', '.zsh', '.exe', '.bat', '.cmd', '.ps1']


def _validate_path(file_path: str, operation: str = "access") -> tuple[bool, str]:
    """
    Validate a file path for security.
    
    Args:
        file_path: Path to validate
        operation: Type of operation ('read', 'write', 'access')
        
    Returns:
        (is_valid, error_message)
    """
    try:
        path = Path(file_path).expanduser().resolve()
        path_str = str(path).lower()
        
        # Check for restricted paths
        for restricted in RESTRICTED_PATHS:
            if restricted.replace('*', '') in path_str:
                return False, f"Access to {file_path} is restricted for security reasons"
        
        # Check for sensitive file patterns
        sensitive_patterns = ['.env', 'credentials', 'secret', 'private_key', 'id_rsa', 'id_ed25519']
        if operation == 'read':
            for pattern in sensitive_patterns:
                if pattern in path_str and not file_path.endswith('.example'):
                    logger.warning(f"Attempting to read potentially sensitive file: {file_path}")
        
        # For write operations, warn about dangerous extensions
        if operation == 'write':
            if path.suffix.lower() in DANGEROUS_EXTENSIONS:
                logger.warning(f"Writing to executable file: {file_path}")
        
        return True, ""
        
    except Exception as e:
        return False, f"Invalid path: {str(e)}"


class ReadFileTool(Tool):
    """Read contents from a file"""
    
    def execute(self, file_path: str) -> ToolResult:
        """
        Read a file's contents
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            ToolResult with file contents or error
        """
        # Validate path for security
        is_valid, error_msg = _validate_path(file_path, 'read')
        if not is_valid:
            return ToolResult(success=False, output=None, error=error_msg)
        
        try:
            path = Path(file_path).expanduser().resolve()
            
            if not path.exists():
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"File not found: {file_path}"
                )
            
            if not path.is_file():
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"Path is not a file: {file_path}"
                )
            
            # Check file size to prevent reading huge files
            file_size = path.stat().st_size
            max_size = 10 * 1024 * 1024  # 10 MB limit
            if file_size > max_size:
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"File too large ({file_size} bytes). Maximum allowed: {max_size} bytes"
                )
            
            # Read file
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return ToolResult(
                success=True,
                output=content
            )
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return ToolResult(
                success=False,
                output=None,
                error=str(e)
            )

class WriteFileTool(Tool):
    """Write content to a file"""
    
    def execute(self, file_path: str, content: str, append: bool = False) -> ToolResult:
        """
        Write content to a file
        
        Args:
            file_path: Path to the file
            content: Content to write
            append: Whether to append instead of overwrite
            
        Returns:
            ToolResult indicating success or failure
        """
        # Validate path for security
        is_valid, error_msg = _validate_path(file_path, 'write')
        if not is_valid:
            return ToolResult(success=False, output=None, error=error_msg)
        
        try:
            path = Path(file_path).expanduser().resolve()
            
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            mode = 'a' if append else 'w'
            with open(path, mode, encoding='utf-8') as f:
                f.write(content)
            
            action = "appended to" if append else "wrote to"
            return ToolResult(
                success=True,
                output=f"Successfully {action} {file_path}"
            )
            
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return ToolResult(
                success=False,
                output=None,
                error=str(e)
            )

class ListFilesTool(Tool):
    """List files in a directory"""
    
    def execute(self, directory: str = ".", pattern: Optional[str] = None) -> ToolResult:
        """
        List files in a directory
        
        Args:
            directory: Directory to list
            pattern: Optional glob pattern to filter files
            
        Returns:
            ToolResult with list of files
        """
        try:
            path = Path(directory).expanduser().resolve()
            
            if not path.exists():
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"Directory not found: {directory}"
                )
            
            if not path.is_dir():
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"Path is not a directory: {directory}"
                )
            
            # List files
            if pattern:
                files = list(path.glob(pattern))
            else:
                files = list(path.iterdir())
            
            # Format output
            file_list = []
            for f in sorted(files):
                file_type = "DIR" if f.is_dir() else "FILE"
                size = f.stat().st_size if f.is_file() else 0
                file_list.append({
                    "name": f.name,
                    "type": file_type,
                    "size": size,
                    "path": str(f)
                })
            
            return ToolResult(
                success=True,
                output=file_list
            )
            
        except Exception as e:
            logger.error(f"Error listing directory {directory}: {e}")
            return ToolResult(
                success=False,
                output=None,
                error=str(e)
            )
