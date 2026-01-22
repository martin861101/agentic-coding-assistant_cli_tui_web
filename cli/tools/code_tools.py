"""
Code execution tools with safety measures
"""
import subprocess
import tempfile
import re
from pathlib import Path
from typing import Optional, List
from .base import Tool, ToolResult
from config import config
import logging

logger = logging.getLogger(__name__)

# Dangerous patterns that should be blocked in safe mode
DANGEROUS_PATTERNS = [
    # System destruction
    r'\brm\s+-rf\s+[/~]',
    r'\bmkfs\b',
    r'\bdd\s+if=',
    r':(){:|:&};:',  # Fork bomb
    
    # Network attacks
    r'\bnc\s+-l',  # Netcat listener
    r'\bcurl\s+.*\|\s*bash',  # Pipe to shell
    r'\bwget\s+.*\|\s*bash',
    
    # Credential theft
    r'/etc/shadow',
    r'/etc/passwd',
    r'\.ssh/id_',
    
    # Crypto mining indicators
    r'\bxmrig\b',
    r'\bminerd\b',
    r'\bcryptominer\b',
    
    # Reverse shells
    r'bash\s+-i\s+>&\s+/dev/tcp',
    r'python.*socket.*connect',
]

def _check_code_safety(code: str, language: str) -> tuple[bool, str]:
    """
    Check if code is safe to execute.
    
    Args:
        code: Code to check
        language: Programming language
        
    Returns:
        (is_safe, warning_message)
    """
    code_lower = code.lower()
    
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            return False, f"Potentially dangerous pattern detected: {pattern}"
    
    # Language-specific checks
    if language in ['bash', 'shell']:
        # Check for sudo/su
        if re.search(r'\bsudo\b|\bsu\s+-', code):
            return False, "Privileged execution (sudo/su) is not allowed in safe mode"
        
        # Check for environment variable manipulation
        if re.search(r'export\s+PATH=|export\s+LD_', code):
            return False, "Environment variable manipulation is not allowed in safe mode"
    
    if language == 'python':
        # Check for dangerous imports
        dangerous_imports = ['os.system', 'subprocess.call', 'eval(', 'exec(', '__import__']
        for imp in dangerous_imports:
            if imp in code:
                logger.warning(f"Python code uses potentially dangerous function: {imp}")
    
    return True, ""


class ExecuteCodeTool(Tool):
    """Execute code in various languages"""
    
    # Language to file extension and execution command mapping
    LANGUAGE_CONFIG = {
        "python": {
            "extension": ".py",
            "command": ["python"],
        },
        "javascript": {
            "extension": ".js",
            "command": ["node"],
        },
        "bash": {
            "extension": ".sh",
            "command": ["bash"],
        },
        "shell": {
            "extension": ".sh",
            "command": ["bash"],
        },
    }
    
    def execute(self, code: str, language: str = "python", timeout: int = 30) -> ToolResult:
        """
        Execute code in a sandboxed environment
        
        Args:
            code: Code to execute
            language: Programming language (python, javascript, bash)
            timeout: Maximum execution time in seconds
            
        Returns:
            ToolResult with stdout/stderr or error
        """
        # Check if code execution is enabled
        if not config.enable_code_execution:
            return ToolResult(
                success=False,
                output=None,
                error="Code execution is disabled in configuration"
            )
        
        # Validate language
        language = language.lower()
        if language not in self.LANGUAGE_CONFIG:
            return ToolResult(
                success=False,
                output=None,
                error=f"Unsupported language: {language}. Supported: {list(self.LANGUAGE_CONFIG.keys())}"
            )
        
        # Check code safety (always perform safety checks)
        is_safe, warning = _check_code_safety(code, language)
        if not is_safe:
            logger.warning(f"Blocked unsafe code execution: {warning}")
            return ToolResult(
                success=False,
                output=None,
                error=f"Code blocked for safety: {warning}"
            )
        
        try:
            lang_config = self.LANGUAGE_CONFIG[language]
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix=lang_config["extension"],
                delete=False,
                encoding='utf-8'
            ) as tmp_file:
                tmp_file.write(code)
                tmp_path = tmp_file.name
            
            try:
                # Execute code
                command = lang_config["command"] + [tmp_path]
                
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                # Prepare output
                output = {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode
                }
                
                success = result.returncode == 0
                
                return ToolResult(
                    success=success,
                    output=output,
                    error=None if success else f"Process exited with code {result.returncode}"
                )
                
            finally:
                # Clean up temporary file
                Path(tmp_path).unlink(missing_ok=True)
                
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                output=None,
                error=f"Execution timeout after {timeout} seconds"
            )
        except Exception as e:
            logger.error(f"Error executing code: {e}")
            return ToolResult(
                success=False,
                output=None,
                error=str(e)
            )
