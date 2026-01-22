"""
Auto-Claude Configuration Module
=================================

Configuration settings for the Auto-Claude integration with ARIA.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, List


@dataclass
class AutoClaudeConfig:
    """Configuration for Auto-Claude integration."""
    
    # Paths
    project_dir: Path = field(default_factory=Path.cwd)
    specs_dir: Path = field(default_factory=lambda: Path.cwd() / "auto-claude" / "specs")
    worktree_dir: Optional[Path] = None
    
    # Model settings
    default_model: str = "claude-sonnet-4-20250514"
    planner_model: str = "claude-sonnet-4-20250514"
    coder_model: str = "claude-sonnet-4-20250514"
    qa_model: str = "claude-sonnet-4-20250514"
    
    # Thinking levels
    planner_thinking: str = "high"
    coder_thinking: str = "none"
    qa_thinking: str = "high"
    
    # Session settings
    max_iterations: Optional[int] = None  # None = unlimited
    auto_continue_delay: int = 3  # seconds between sessions
    
    # Memory settings
    graphiti_url: Optional[str] = field(
        default_factory=lambda: os.environ.get("GRAPHITI_MCP_URL")
    )
    enable_graphiti: bool = True
    enable_file_memory: bool = True  # Fallback when Graphiti unavailable
    
    # MCP settings
    context7_enabled: bool = True
    linear_enabled: bool = False
    linear_api_key: Optional[str] = field(
        default_factory=lambda: os.environ.get("LINEAR_API_KEY")
    )
    electron_mcp_enabled: bool = False
    puppeteer_enabled: bool = False
    
    # QA settings
    enable_qa_loop: bool = True
    max_qa_iterations: int = 5
    auto_fix_issues: bool = True
    
    # Security settings
    allowed_paths: List[Path] = field(default_factory=list)
    blocked_commands: List[str] = field(default_factory=lambda: [
        "rm -rf /", "sudo rm", "format", "mkfs", "dd if=/dev/zero"
    ])
    
    def __post_init__(self):
        """Initialize computed properties."""
        if isinstance(self.project_dir, str):
            self.project_dir = Path(self.project_dir)
        if isinstance(self.specs_dir, str):
            self.specs_dir = Path(self.specs_dir)
        
        # Create directories if needed
        self.specs_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls, project_dir: Optional[Path] = None) -> "AutoClaudeConfig":
        """Create config from environment variables."""
        return cls(
            project_dir=project_dir or Path.cwd(),
            default_model=os.environ.get("AUTO_CLAUDE_MODEL", "claude-sonnet-4-20250514"),
            graphiti_url=os.environ.get("GRAPHITI_MCP_URL"),
            enable_graphiti=os.environ.get("ENABLE_GRAPHITI", "true").lower() == "true",
            linear_api_key=os.environ.get("LINEAR_API_KEY"),
            linear_enabled=bool(os.environ.get("LINEAR_API_KEY")),
            context7_enabled=os.environ.get("CONTEXT7_ENABLED", "true").lower() == "true",
            enable_qa_loop=os.environ.get("ENABLE_QA_LOOP", "true").lower() == "true",
            max_qa_iterations=int(os.environ.get("MAX_QA_ITERATIONS", "5")),
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AutoClaudeConfig":
        """Create config from dictionary."""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "project_dir": str(self.project_dir),
            "specs_dir": str(self.specs_dir),
            "default_model": self.default_model,
            "planner_model": self.planner_model,
            "coder_model": self.coder_model,
            "qa_model": self.qa_model,
            "max_iterations": self.max_iterations,
            "enable_graphiti": self.enable_graphiti,
            "enable_qa_loop": self.enable_qa_loop,
            "max_qa_iterations": self.max_qa_iterations,
            "linear_enabled": self.linear_enabled,
            "context7_enabled": self.context7_enabled,
        }


# Global config instance
_config: Optional[AutoClaudeConfig] = None


def get_config() -> AutoClaudeConfig:
    """Get the global Auto-Claude config."""
    global _config
    if _config is None:
        _config = AutoClaudeConfig.from_env()
    return _config


def setup_auto_claude(
    project_dir: Optional[Path] = None,
    **kwargs
) -> AutoClaudeConfig:
    """
    Initialize and configure Auto-Claude for a project.
    
    Args:
        project_dir: Root directory of the project
        **kwargs: Additional configuration options
        
    Returns:
        Configured AutoClaudeConfig instance
    """
    global _config
    
    # Create config
    config = AutoClaudeConfig(
        project_dir=project_dir or Path.cwd(),
        **kwargs
    )
    
    # Set up auto-claude directory structure
    auto_claude_dir = config.project_dir / "auto-claude"
    auto_claude_dir.mkdir(exist_ok=True)
    config.specs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create memory directory for file-based fallback
    memory_dir = auto_claude_dir / "memory"
    memory_dir.mkdir(exist_ok=True)
    
    # Store as global config
    _config = config
    
    return config


def reset_config():
    """Reset the global config (useful for testing)."""
    global _config
    _config = None
