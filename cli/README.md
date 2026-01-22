# ARIA - Adaptive Real-time Intelligence Assistant

A powerful AI coding assistant that lives in your terminal, featuring multi-provider LLM support, RAG-powered memory, agentic actions, and intelligent code understanding.

## Features

### Multi-Provider LLM Support
- **Ollama** (local, default) - Run models locally
- **Gemini** - Google's AI models
- **OpenRouter** - Access to 100+ models (has free tier)
- **OpenAI** - GPT-4, GPT-3.5, etc.
- **Anthropic** - Claude models

### RAG-Powered Memory System
- **Codebase Indexing** - Index your project for semantic code search
- **Conversation Memory** - Remember and retrieve past discussions
- **Project Context** - Auto-detect frameworks, languages, structure
- **Smart Retrieval** - Automatically inject relevant context into LLM prompts

### Agentic Capabilities
- Natural language commands: "Look at my app and fix syntax issues"
- Automatic action execution from LLM responses
- Multi-step task orchestration

### Operation Modes
- **AUTO** - Execute all actions without prompts
- **SAFE** - Confirm before any file/code changes
- **NORMAL** - Smart confirmations for destructive actions (default)

### Specialist Agents
- Code Review
- Debugging
- Documentation Generation
- Test Generation
- Refactoring

## Quick Start

### Prerequisites
```bash
# Install Ollama (for local models)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull mistral:latest

# Pull embedding model (for RAG)
ollama pull nomic-embed-text
```

### Installation
```bash
cd /usr/local/bin/aria-files

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and edit environment file
cp .env.example .env
# Edit .env with your API keys (optional for cloud providers)
```

### Running ARIA

**CLI Interface (Full Features):**
```bash
python aria.py
```

**Modern TUI Interface:**
```bash
python tui.py
```

## Commands

### Mode Commands
| Command | Description |
|---------|-------------|
| `/auto` | Switch to auto mode (execute without prompts) |
| `/safe` | Switch to safe mode (confirm all changes) |
| `/mode <name>` | Switch mode (auto/safe/normal) |

### File Commands
| Command | Description |
|---------|-------------|
| `/read <file>` | Read and display a file |
| `/edit <file>` | Open file for editing |
| `/ls [dir]` | List directory contents |
| `/run <code>` | Execute Python code |
| `/scan` | Scan project structure |

### Memory & RAG Commands
| Command | Description |
|---------|-------------|
| `/index` | Index current project for RAG |
| `/index <path>` | Index specific directory |
| `/memory` | Show memory status & stats |
| `/memory clear` | Clear all memory |
| `/memory clear codebase` | Clear just codebase index |
| `/memory clear conversations` | Clear conversation history |

### Model & Provider Commands
| Command | Description |
|---------|-------------|
| `/model` | List available models |
| `/model <name>` | Switch to specific model |
| `/provider` | List available providers |
| `/provider <name>` | Switch provider |

### Specialist Commands
| Command | Description |
|---------|-------------|
| `/review [file]` | Code review |
| `/debug [file]` | Debug assistance |
| `/test [file]` | Generate tests |
| `/docs [file]` | Generate documentation |
| `/refactor [file]` | Suggest refactoring |

### Session Commands
| Command | Description |
|---------|-------------|
| `/status` | Show current status |
| `/clear` | Clear conversation |
| `/help` | Show help |
| `/exit` | Exit ARIA |

### Learning Commands
| Command | Description |
|---------|-------------|
| `/correct <text>` | Record a correction |
| `/rate <1-5>` | Rate last response |
| `/learn` | Show learning stats |

## Architecture

```
aria-files/
├── aria.py              # Main CLI application
├── tui.py               # Textual TUI interface
├── config.py            # Configuration & settings
├── llm_interface.py     # Multi-provider LLM interface
├── learning_system.py   # Feedback & learning
├── plugin_system.py     # Plugin management
│
├── memory/              # RAG Memory System
│   ├── __init__.py
│   ├── memory_manager.py    # Core orchestrator
│   ├── codebase_index.py    # Code indexing & search
│   ├── conversation_store.py # Conversation history
│   └── retriever.py         # Unified retrieval
│
├── tools/               # Tool implementations
│   ├── base.py          # Tool base classes
│   ├── file_tools.py    # File operations
│   ├── code_tools.py    # Code execution
│   └── web_tools.py     # Web operations
│
├── agents/              # Specialist agents
│   ├── base.py          # Agent base classes
│   ├── code_agent.py    # Review & refactoring
│   ├── debug_agent.py   # Debugging
│   ├── doc_agent.py     # Documentation
│   └── test_agent.py    # Test generation
│
├── plugins/             # Custom plugins
├── data/                # Persistent data
│   ├── memory/          # RAG indexes
│   ├── sessions/        # Session history
│   ├── logs/            # Log files
│   └── learning.db      # Learning database
│
├── .env                 # API keys (create from .env.example)
├── .env.example         # Example environment file
└── requirements.txt     # Python dependencies
```

## RAG Memory System

ARIA uses Retrieval-Augmented Generation (RAG) to provide context-aware responses.

### How It Works

```
User Query: "Fix the auth bug"
        │
        ▼
┌───────────────────┐
│  Memory Manager   │
└───────────────────┘
        │
   ┌────┴────┬──────────┐
   ▼         ▼          ▼
┌──────┐  ┌──────┐  ┌──────┐
│Code  │  │Convo │  │Project│
│Index │  │Store │  │Context│
└──────┘  └──────┘  └──────┘
   │         │          │
   └────┬────┴──────────┘
        ▼
┌───────────────────┐
│ Retrieved Context │
│ - auth.py code    │
│ - past auth fixes │
│ - "uses FastAPI"  │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│   LLM + Context   │
│   = Smart Answer  │
└───────────────────┘
```

### Features

- **Codebase Indexing**: Smart chunking by language (functions, classes)
- **Semantic Search**: Find relevant code using embeddings
- **Conversation Memory**: Retrieve relevant past discussions
- **Project Understanding**: Auto-detect frameworks, languages
- **Incremental Updates**: Only re-index changed files

### Usage

```bash
# Index your project
/index

# Check memory status
/memory

# Clear and re-index
/memory clear codebase
/index
```

## Environment Variables

Create a `.env` file from `.env.example`:

```bash
# LLM Provider (ollama, gemini, openrouter, openai, anthropic)
LLM_PROVIDER=ollama

# Ollama Settings
OLLAMA_HOST=http://localhost:11434
DEFAULT_MODEL=mistral:latest

# API Keys (for cloud providers)
GEMINI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Operation Mode (auto, safe, normal)
OPERATION_MODE=normal

# Features
ENABLE_PLUGINS=true
ENABLE_AGENTS=true
ENABLE_LEARNING=true
ENABLE_CODE_EXECUTION=true

# Logging
LOG_LEVEL=INFO
```

## Keyboard Shortcuts (TUI only)

| Shortcut | Action |
|----------|--------|
| `Ctrl+P` | Command palette |
| `Ctrl+M` | Select model |
| `Ctrl+O` | Select provider |
| `Ctrl+E` | Select mode |
| `Ctrl+L` | Clear chat |
| `Ctrl+B` | Toggle sidebar |
| `Ctrl+Q` | Quit |

## Example Interactions

### Natural Language (Agentic Mode)
```
You: Look at my auth.py and fix any security issues

ARIA: Let me read the file first:
[Reading auth.py...]

I found 3 security issues:
1. Password stored in plaintext
2. No rate limiting
3. Missing CSRF protection

Let me fix these:
[Writing auth.py...]

Done! I've updated the file with:
- bcrypt password hashing
- Rate limiting decorator
- CSRF token validation
```

### With RAG Context
```
You: How does the auth system work?

ARIA: Based on the indexed codebase, your auth system:
[Retrieved from auth.py, middleware.py]

- Uses JWT tokens with 24h expiration
- Stores users in PostgreSQL
- Has middleware in middleware.py for route protection
- Implements refresh token rotation

Would you like me to explain any part in detail?
```

## Development

### Adding a New Provider

1. Create a class extending `BaseLLMProvider` in `llm_interface.py`
2. Implement required methods: `chat()`, `get_available_models()`, `is_available()`
3. Add to `LLMInterface.PROVIDERS` dict
4. Add config in `config.py`

### Adding a New Tool

1. Create a class extending `Tool` in `tools/`
2. Implement `execute()` method
3. Register in `ARIA._register_tools()`

### Adding a New Agent

1. Create a class extending `BaseAgent` in `agents/`
2. Define capabilities and implement `process()`
3. Register in `ARIA._register_agents()`

## Requirements

- Python 3.10+
- Ollama (for local models)
- ChromaDB (for RAG)
- See `requirements.txt` for full list

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

Built with love for developers who want AI assistance without leaving the terminal.
