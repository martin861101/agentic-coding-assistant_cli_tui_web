# ARIA Function Reference

This document maps which scripts are responsible for which functions in ARIA.

---

## Entry Points

| Script | Command | Description |
|--------|---------|-------------|
| `aria.py` | `python aria.py` | CLI interface with Rich (prompt-toolkit) |
| `tui.py` | `python tui.py` | Modern TUI interface with Textual |

---

## aria.py - CLI Interface

**Main Class: `ARIA`** (lines 64-1250+)

### Initialization & Setup

| Method | Description |
|--------|-------------|
| `__init__` | Initialize console, LLM, tools, plugins, agents, learning, memory |
| `_build_agentic_prompt` | Build system prompt for agentic LLM behavior |
| `_register_tools` | Register file, code, and web tools |
| `_register_agents` | Register specialist agents (review, debug, docs, test, refactor) |

### Action Parsing & Execution (Agentic Mode)

| Method | Description |
|--------|-------------|
| `_parse_actions` | Parse `<action:read>`, `<action:write>`, `<action:ls>`, `<action:run>` blocks from LLM response |
| `_execute_action` | Execute a single parsed action |
| `_process_response_with_actions` | Process LLM response and execute embedded actions |

### Mode Management

| Method | Description |
|--------|-------------|
| `set_mode` | Set operation mode (auto/safe/normal) |
| `_get_mode_indicator` | Get colored mode indicator string |
| `_should_confirm` | Check if action needs user confirmation |
| `_confirm_action` | Prompt user for confirmation |

### Smart File Operations

| Method | Description |
|--------|-------------|
| `smart_read` | Read file with error handling |
| `smart_write` | Write file with confirmation in safe mode |
| `smart_exec` | Execute code with confirmation in safe mode |
| `_scan_project` | Scan project directory for context |

### Command Parsing & Handling

| Method | Description |
|--------|-------------|
| `_parse_command` | Parse user input into command type and params |
| `_handle_command` | Route commands to appropriate handlers |

### Commands Supported

| Command | Handler | Description |
|---------|---------|-------------|
| `/auto`, `/safe`, `/mode` | `set_mode` | Change operation mode |
| `/read <file>` | `smart_read` | Read and display file |
| `/edit <file>` | Opens file for editing | Read file and prompt for changes |
| `/ls [dir]` | `ListFilesTool` | List directory contents |
| `/run <code>` | `smart_exec` | Execute Python code |
| `/model` | `_show_models` | List available models |
| `/model <name>` | `llm.switch_model` | Switch to specific model |
| `/provider` | `_show_providers` | List available providers |
| `/provider <name>` | `_switch_provider` | Switch to specific provider |
| `/search <query>` | `_handle_web_search` | Tavily web search |
| `/web <cmd>` | `_handle_web_browser` | Browser automation |
| `/scrape <url>` | `_handle_web_scrape` | Scrape webpage |
| `/review [file]` | `_handle_agent_task` | Code review via agent |
| `/debug [file]` | `_handle_agent_task` | Debug assistance via agent |
| `/test [file]` | `_handle_agent_task` | Generate tests via agent |
| `/docs [file]` | `_handle_agent_task` | Generate docs via agent |
| `/refactor [file]` | `_handle_agent_task` | Refactoring via agent |
| `/index [path]` | `_handle_index_project` | Index project for RAG |
| `/memory` | `_show_memory_status` | Show memory/RAG status |
| `/memory clear` | `_handle_memory_clear` | Clear memory stores |
| `/clear`, `/reset` | `llm.clear_history` | Clear conversation |
| `/status` | `_show_status` | Show ARIA status |
| `/scan` | `_scan_project` | Scan project structure |
| `/correct <text>` | `_handle_correction` | Record correction feedback |
| `/rate <1-5>` | `_handle_rating` | Rate last response |
| `/learn` | `_show_learning_stats` | Show learning statistics |
| `/agents` | `_list_agents` | List registered agents |
| `/plugins` | `_list_plugins` | List loaded plugins |
| `/help` | `_get_help_text` | Show help |
| `/exit`, `/quit` | Exit | Stop ARIA |

### Display & Status Methods

| Method | Description |
|--------|-------------|
| `_show_status` | Display current ARIA status |
| `_show_memory_status` | Display memory/RAG context status |
| `_show_models` | Display available models |
| `_show_providers` | Display available providers |
| `_switch_provider` | Switch LLM provider |
| `_list_agents` | List specialist agents |
| `_list_plugins` | List loaded plugins |
| `_get_help_text` | Generate help text |
| `_display_welcome` | Display welcome banner |

### Memory/RAG Handlers

| Method | Description |
|--------|-------------|
| `_handle_index_project` | Index project for RAG retrieval |
| `_handle_memory_clear` | Clear memory stores |
| `_show_memory_status` | Show RAG memory statistics |

### Web Handlers

| Method | Description |
|--------|-------------|
| `_handle_web_browser` | Browser automation commands |
| `_handle_web_search` | Tavily search |
| `_handle_web_scrape` | Web scraping |

### Learning System

| Method | Description |
|--------|-------------|
| `_handle_correction` | Record user correction |
| `_handle_rating` | Record user rating |
| `_show_learning_stats` | Display learning statistics |

### Main Loop

| Method | Description |
|--------|-------------|
| `_agentic_chat` | Handle natural language with RAG context and action execution |
| `run` | Main REPL loop |
| `main` | Entry point function |

---

## tui.py - Textual TUI Interface

**Main Class: `AriaTUI`** (lines 349-800)

### Custom Widgets

| Widget | Description |
|--------|-------------|
| `StatusBar` | Shows provider, model, mode in header |
| `MessageBubble` | Chat message display widget |
| `ThinkingIndicator` | Animated "thinking..." indicator |
| `FileTreeWidget` | File browser tree in sidebar |

### Modal Screens

| Modal | Description |
|-------|-------------|
| `CommandPalette` | Ctrl+P command search modal |
| `ModelSelector` | Model selection modal |
| `ProviderSelector` | Provider selection modal |
| `ModeSelector` | Mode selection modal |

### AriaTUI Methods

#### Initialization

| Method | Description |
|--------|-------------|
| `__init__` | Initialize LLM, tools, mode, system prompt |
| `_register_tools` | Register file/code tools |
| `_build_system_prompt` | Build agentic system prompt |
| `compose` | Build UI layout |
| `on_mount` | Initialize on app start |

#### UI Updates

| Method | Description |
|--------|-------------|
| `_update_status_bar` | Update provider/model/mode display |
| `_add_welcome_message` | Show welcome panel |
| `_add_message` | Add chat message to log |
| `_add_system_message` | Add system notification |

#### Input Handling

| Method | Description |
|--------|-------------|
| `handle_input` | Handle Enter on chat input |
| `_handle_command` | Process `/` commands |
| `_show_help` | Display help text |
| `_show_status` | Display status |
| `_set_mode` | Change operation mode |
| `_read_file` | Read and display file |
| `_switch_provider` | Switch LLM provider |

#### AI Response

| Method | Description |
|--------|-------------|
| `_get_ai_response` | Threaded AI response with streaming |
| `_rebuild_chat_with_response` | Update chat after response |

#### Keyboard Actions

| Binding | Method | Description |
|---------|--------|-------------|
| `Ctrl+P` | `action_command_palette` | Open command palette |
| `Ctrl+M` | `action_select_model` | Open model selector |
| `Ctrl+O` | `action_select_provider` | Open provider selector |
| `Ctrl+E` | `action_select_mode` | Open mode selector |
| `Ctrl+L` | `action_clear_chat` | Clear chat |
| `Ctrl+B` | `action_toggle_sidebar` | Toggle file sidebar |
| `Ctrl+Q` | `action_quit` | Quit app |
| `Escape` | `action_focus_input` | Focus chat input |

---

## Comparison: aria.py vs tui.py

| Feature | aria.py | tui.py |
|---------|---------|--------|
| **UI Framework** | Rich + prompt_toolkit | Textual |
| **Interface Type** | CLI REPL | Full TUI |
| **File Browser** | No | Yes (sidebar) |
| **Command Palette** | No | Yes (Ctrl+P) |
| **Modal Dialogs** | No | Yes |
| **Keyboard Shortcuts** | No | Yes |
| **Plugin Support** | Yes | No |
| **Agent Support** | Yes | No |
| **Learning System** | Yes | No |
| **RAG Memory** | Yes | No |
| **Agentic Actions** | Full | Basic |
| **Web Tools** | Yes | No |
| **Streaming** | Yes | Yes (threaded) |

---

## Supporting Modules

### config.py
- `OperationMode` enum: AUTO, SAFE, NORMAL
- `LLMProvider` enum: OLLAMA, GEMINI, OPENROUTER, OPENAI, ANTHROPIC
- `Config` class: All settings and paths
- `DEFAULT_MODELS`, `PROVIDER_MODELS`: Model configurations

### llm_interface.py
- `BaseLLMProvider`: Abstract base class
- `OllamaProvider`: Local Ollama
- `GeminiProvider`: Google Gemini API
- `OpenRouterProvider`: OpenRouter API
- `OpenAIProvider`: OpenAI API
- `AnthropicProvider`: Anthropic Claude API
- `LLMInterface`: Unified interface used by ARIA

**Memory Integration Methods:**
| Method | Description |
|--------|-------------|
| `memory` | Property returning MemoryManager instance |
| `chat_with_context()` | RAG-enhanced chat with automatic context retrieval |
| `index_project()` | Index a project for RAG |
| `get_memory_stats()` | Get memory system statistics |
| `clear_memory()` | Clear memory stores |
| `enable_memory()` | Enable/disable memory system |

### tools/
- `base.py`: `Tool` base class, `ToolResult`, `ToolRegistry`
- `file_tools.py`: `ReadFileTool`, `WriteFileTool`, `ListFilesTool`
- `code_tools.py`: `ExecuteCodeTool`
- `web_tools.py`: `WebBrowserTool`, `WebScrapeTool`, `TavilySearchTool`, `WebExtractTool`

### agents/
- `base.py`: `BaseAgent`, `AgentTask`, `AgentResponse`, `AgentCoordinator`
- `code_agent.py`: `CodeReviewAgent`, `RefactoringAgent`
- `debug_agent.py`: `DebugAgent`
- `doc_agent.py`: `DocumentationAgent`
- `test_agent.py`: `TestGenerationAgent`

### learning_system.py
- `Feedback`: Feedback data class
- `LearningSystem`: Records feedback, learns patterns
- `Pattern`: Learned pattern data class

### plugin_system.py
- `PluginManager`: Load/manage plugins
- Plugin discovery and tool registration

---

## memory/ - RAG Memory System

The RAG (Retrieval-Augmented Generation) memory system provides intelligent context retrieval for enhanced LLM responses.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      USER QUERY                              │
│              "Fix the bug in the auth module"                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   RETRIEVAL LAYER                            │
│  Query embeddings → Search all memory stores → Rank results  │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬─────────────┐
        ▼             ▼             ▼             ▼
   ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
   │CODEBASE │  │ CONVO    │  │ PROJECT  │  │ LEARNED  │
   │ INDEX   │  │ HISTORY  │  │ CONTEXT  │  │ PATTERNS │
   └─────────┘  └──────────┘  └──────────┘  └──────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   CONTEXT ASSEMBLY                           │
│  Combine: relevant code + past conversations + patterns      │
└─────────────────────────────────────────────────────────────┘
```

### Module Files

| File | Description |
|------|-------------|
| `__init__.py` | Exports: MemoryManager, CodebaseIndex, ConversationStore, Retriever |
| `memory_manager.py` | Core orchestrator for all memory operations |
| `codebase_index.py` | ChromaDB-based RAG index for project files |
| `conversation_store.py` | Stores and retrieves past conversations |
| `retriever.py` | Unified retrieval interface |

### memory_manager.py

**Class: `MemoryManager`** - Core orchestrator

| Method | Description |
|--------|-------------|
| `__init__(data_dir, embedding_model, ollama_host)` | Initialize with config |
| `index_project(path, force)` | Index a project directory |
| `store_conversation(query, response, metadata)` | Store a conversation turn |
| `retrieve_context(query, project_path, ...)` | Retrieve relevant context |
| `get_project_context(path)` | Get/build project understanding |
| `get_stats()` | Get memory system statistics |
| `clear_memory(what)` | Clear memory ("all", "codebase", "conversations") |

**Properties:**
| Property | Description |
|----------|-------------|
| `embeddings_available` | Check if Ollama embeddings are available |
| `codebase_index` | Lazy-loaded CodebaseIndex instance |
| `conversation_store` | Lazy-loaded ConversationStore instance |
| `retriever` | Lazy-loaded Retriever instance |

**Class: `RetrievedContext`** - Container for retrieved context

| Attribute | Type | Description |
|-----------|------|-------------|
| `code_snippets` | List[Dict] | Relevant code from codebase |
| `conversations` | List[Dict] | Relevant past conversations |
| `project_info` | Dict | Project metadata (languages, frameworks) |
| `total_tokens_estimate` | int | Estimated token count |

| Method | Description |
|--------|-------------|
| `to_prompt_section(max_tokens)` | Convert to prompt-ready string |

### codebase_index.py

**Class: `CodebaseIndex`** - Indexes codebase for semantic search

| Method | Description |
|--------|-------------|
| `__init__(persist_dir, embedding_model, ...)` | Initialize with ChromaDB |
| `index_directory(directory, force)` | Index all files in directory |
| `search(query, limit, file_filter)` | Semantic search for code |
| `get_stats()` | Get index statistics |
| `clear()` | Clear the entire index |

**Class: `CodeChunker`** - Chunks code files into semantic units

| Method | Description |
|--------|-------------|
| `chunk_file(file_path)` | Chunk a file by language |
| `_chunk_python(content, path)` | Python-specific chunking (functions, classes) |
| `_chunk_javascript(content, path)` | JS/TS chunking |
| `_chunk_config(content, path)` | Config file chunking |
| `_chunk_markdown(content, path)` | Markdown section chunking |
| `_chunk_generic(content, path)` | Size-based chunking |

**Class: `CodeChunk`** - Data class for a code chunk

| Attribute | Type | Description |
|-----------|------|-------------|
| `content` | str | The code content |
| `file_path` | str | Source file path |
| `chunk_type` | str | "function", "class", "module", "config" |
| `start_line` | int | Starting line number |
| `end_line` | int | Ending line number |
| `name` | Optional[str] | Function/class name if applicable |

**Supported File Types:**
- **Code**: `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.go`, `.rs`, `.java`, `.c`, `.cpp`, etc.
- **Config**: `.json`, `.yaml`, `.yml`, `.toml`, `.ini`, etc.
- **Docs**: `.md`, `.rst`, `.txt`

### conversation_store.py

**Class: `ConversationStore`** - Stores conversations with embeddings

| Method | Description |
|--------|-------------|
| `__init__(persist_dir, embedding_model, ...)` | Initialize with SQLite + ChromaDB |
| `set_session(session_id)` | Set current session |
| `new_session()` | Start a new session |
| `add_turn(query, response, metadata)` | Add a conversation turn |
| `search(query, limit, session_filter)` | Semantic search over conversations |
| `get_session_history(session_id, limit)` | Get history for a session |
| `get_recent_sessions(limit)` | List recent sessions |
| `count()` | Total stored conversations |
| `clear(session_id)` | Clear conversations |
| `export_session(session_id)` | Export session as JSON |
| `import_session(data)` | Import session from JSON |

**Class: `ConversationTurn`** - Data class for a turn

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | Optional[int] | Database ID |
| `timestamp` | str | ISO timestamp |
| `user_query` | str | User's message |
| `assistant_response` | str | Assistant's response |
| `session_id` | str | Session identifier |
| `metadata` | Dict | Additional metadata |

### retriever.py

**Class: `Retriever`** - Unified retrieval interface

| Method | Description |
|--------|-------------|
| `retrieve(query, project_path, ...)` | Retrieve from all sources |
| `retrieve_for_file(file_path, query)` | Get context for specific file |
| `retrieve_similar_code(snippet, limit)` | Find similar code |
| `retrieve_by_topic(topic, limit)` | Search by topic across sources |
| `get_context_summary(query, project_path)` | Quick context summary |

---

## Quick Reference: What Handles What

| Task | aria.py | tui.py |
|------|---------|--------|
| Natural chat | `_agentic_chat()` | `_get_ai_response()` |
| RAG-enhanced chat | `chat_with_context()` via `_agentic_chat()` | Not implemented |
| Index project | `_handle_index_project()` | Not implemented |
| Execute actions from LLM | `_parse_actions()` + `_execute_action()` | Not implemented |
| Switch model | `_handle_command()` -> `/model` | `action_select_model()` |
| Switch provider | `_switch_provider()` | `_switch_provider()` |
| Change mode | `set_mode()` | `_set_mode()` |
| Read file | `smart_read()` | `_read_file()` |
| Write file | `smart_write()` | Not implemented |
| Run code | `smart_exec()` | Not implemented |
| Call specialist agent | `_handle_agent_task()` | Not implemented |
| Learning/feedback | `_handle_correction()`, `_handle_rating()` | Not implemented |
| Memory status | `_show_memory_status()` | Not implemented |
| Clear memory | `_handle_memory_clear()` | Not implemented |

---

## Data Flow: RAG-Enhanced Chat

```
1. User enters message
        │
        ▼
2. _agentic_chat() called
        │
        ▼
3. llm.chat_with_context() invoked
        │
        ├─► memory.retrieve_context(query)
        │       │
        │       ├─► codebase_index.search()  → relevant code
        │       ├─► conversation_store.search() → past convos
        │       └─► get_project_context() → frameworks, etc.
        │       │
        │       └─► RetrievedContext assembled
        │
        ├─► context.to_prompt_section()
        │       └─► Context injected into system prompt
        │
        ├─► LLM called with enhanced prompt
        │       └─► Response streamed to user
        │
        └─► memory.store_conversation()
                └─► Conversation saved for future retrieval
```

---

## Dependencies

### Core
- `ollama` - Ollama Python client
- `chromadb` - Vector database for RAG
- `rich` - Terminal formatting
- `textual` - TUI framework
- `prompt_toolkit` - Input handling
- `pydantic` - Configuration
- `python-dotenv` - Environment loading

### Optional (for providers)
- `google-generativeai` - Gemini
- `openai` - OpenAI
- `anthropic` - Claude
- `httpx` - HTTP client for OpenRouter
