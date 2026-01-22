"""
Configuration management for ARIA
"""
import os
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv

# Load environment variables from explicit path - find_dotenv() can fail in some contexts
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path, override=True)


class OperationMode(str, Enum):
    """ARIA operation modes"""
    AUTO = "auto"      # Automatically performs actions without prompts
    SAFE = "safe"      # Prompts for confirmation before any file/code changes
    NORMAL = "normal"  # Smart prompting - prompts for destructive actions only


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OLLAMA = "ollama"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


# Default models for each provider
DEFAULT_MODELS: Dict[str, str] = {
    "ollama": "mistral:latest",
    "gemini": "gemini-2.5-flash",
    "openrouter": "meta-llama/llama-3.1-8b-instruct:free",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-haiku-20240307",
}

# Popular models for each provider (shown in /model)
PROVIDER_MODELS: Dict[str, list] = {
    "ollama": [
        "mistral:latest",
        "llama3:latest",
        "llama3.1:latest",
        "codellama:latest",
        "deepseek-coder:latest",
        "qwen2.5-coder:latest",
        "gemma2:latest",
        "phi3:latest",
    ],
    "gemini": [
        "gemini-3.0-flash",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash",
    ],
    "openrouter": [
        "meta-llama/llama-3.1-8b-instruct:free",
        "meta-llama/llama-3.1-70b-instruct",
        "mistralai/mistral-7b-instruct:free",
        "google/gemini-flash-1.5",
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4o-mini",
        "deepseek/deepseek-chat",
        "qwen/qwen-2.5-coder-32b-instruct",
    ],
    "openai": [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
    ],
    "anthropic": [
        "claude-3-haiku-20240307",
        "claude-3-sonnet-20240229",
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
    ],
}


class Config(BaseModel):
    """Main configuration for ARIA"""
    
    # Centralized data directory
    data_dir: Path = Path("/usr/local/bin/aria-files/data")
    
    # LLM Provider settings
    llm_provider: LLMProvider = LLMProvider(os.getenv("LLM_PROVIDER", "ollama"))
    
    # Ollama settings
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    default_model: str = os.getenv("DEFAULT_MODEL", "mistral:latest")
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # API Keys (for cloud providers)
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    openrouter_api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # Operation mode (auto, safe, normal)
    operation_mode: OperationMode = OperationMode(os.getenv("OPERATION_MODE", "normal"))
    
    # Paths - all centralized under data_dir
    @property
    def memory_dir(self) -> Path:
        return self.data_dir / "memory"
    
    @property
    def session_dir(self) -> Path:
        return self.data_dir / "sessions"
    
    @property
    def log_dir(self) -> Path:
        return self.data_dir / "logs"
    
    @property
    def chroma_persist_dir(self) -> Path:
        return self.data_dir / "memory" / "chroma"
    
    @property
    def learning_db(self) -> Path:
        return self.data_dir / "learning.db"
    
    @property
    def log_file(self) -> Path:
        return self.data_dir / "logs" / "aria.log"
    
    # Plugin dir stays in the app directory
    base_dir: Path = Path(__file__).parent
    
    @property
    def plugins_dir(self) -> Path:
        return self.base_dir / "plugins"
    
    # Memory settings
    max_context_messages: int = int(os.getenv("MAX_CONTEXT_MESSAGES", "50"))
    embedding_model: str = "nomic-embed-text"
    
    # Execution settings
    enable_code_execution: bool = os.getenv("ENABLE_CODE_EXECUTION", "true").lower() == "true"
    
    # Agent settings
    enable_agents: bool = os.getenv("ENABLE_AGENTS", "true").lower() == "true"
    agent_confidence_threshold: float = 0.3
    
    # Plugin settings
    enable_plugins: bool = os.getenv("ENABLE_PLUGINS", "true").lower() == "true"
    
    # Learning settings
    enable_learning: bool = os.getenv("ENABLE_LEARNING", "true").lower() == "true"
    
    # Auto-Claude settings
    enable_auto_claude: bool = os.getenv("ENABLE_AUTO_CLAUDE", "true").lower() == "true"
    auto_claude_model: str = os.getenv("AUTO_CLAUDE_MODEL", "claude-sonnet-4-20250514")
    auto_claude_max_iterations: Optional[int] = int(os.getenv("AUTO_CLAUDE_MAX_ITERATIONS", "0")) or None
    graphiti_url: Optional[str] = os.getenv("GRAPHITI_MCP_URL")
    enable_qa_loop: bool = os.getenv("ENABLE_QA_LOOP", "true").lower() == "true"
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Create all necessary directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
    
    def get_default_model_for_provider(self, provider: str) -> str:
        """Get the default model for a specific provider"""
        return DEFAULT_MODELS.get(provider, "mistral:latest")
    
    def get_models_for_provider(self, provider: str) -> list:
        """Get list of popular models for a provider"""
        return PROVIDER_MODELS.get(provider, [])
    
    def has_api_key(self, provider: str) -> bool:
        """Check if API key is configured for a provider"""
        key_map = {
            "gemini": self.gemini_api_key,
            "openrouter": self.openrouter_api_key,
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
        }
        key = key_map.get(provider)
        return key is not None and len(key) > 0


# Global config instance
config = Config()
