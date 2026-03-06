# ARIA - Adaptive Real-time Intelligence Assistant

**ARIA** is a powerful **agentic AI coding assistant** that works where you work—whether in the terminal or in VS Code. Unlike passive chat bots, ARIA can **take action**: reading files, writing code, running commands, and searching the web to help you build software faster.

## 🚀 Key Capabilities

- **Agentic Workflow**: ARIA doesn't just talk; it acts. It can read your project files, edit code, execute shell commands, and run tests.
- **Reasoning Engine**: ARIA uses a "Reason → Plan → Execute" loop to solve complex tasks step-by-step.
- **Memory & Learning**:
  - **Project Indexing**: Index your codebase for RAG-enhanced responses.
  - **Study Mode**: Teach ARIA about specific files or documentation.
  - **Learning System**: ARIA learns from your corrections and feedback over time.
- **Multi-Provider Support**: Switch seamlessly between models:
  - **Ollama** (Local execution - *Default*)
  - **Google Gemini**
  - **OpenAI**
  - **Anthropic Claude**
  - **OpenRouter**
- **Safety Modes**: Control how much autonomy ARIA has (`Auto`, `Safe`, or `Normal`).

---

## 📦 Installation

### 1. Build the Core Binary
ARIA's intelligence is powered by a shared Go backend. You need to build this first.

```bash
# Clone the repository
git clone https://github.com/yourusername/aria-go.git
cd aria-go

# Build the binary (requires Go 1.21+ and CGO for SQLite)
CGO_ENABLED=1 go build -o aria .

# Verify it works
./aria --help
```

### 2. Install VS Code Extension (Optional)
If you prefer working in VS Code:

```bash
cd vscode-extension
npm install
npm run compile
npx vsce package
code --install-extension aria-assistant-1.0.0.vsix
```

---

## 🖥️ ARIA TUI (Terminal Interface)

The Terminal User Interface provides a beautiful, keyboard-centric way to interact with ARIA directly from your shell.

### Usage
```bash
# Start the TUI
./aria
```

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `Ctrl+P` | **Command Palette** - Access all features |
| `Ctrl+G` | **Select Model** - Switch LLMs instantly |
| `Ctrl+O` | **Select Provider** - Switch between Ollama, Gemini, etc. |
| `Ctrl+E` | **Select Mode** - Toggle Auto/Safe/Normal |
| `Ctrl+T` | **Task Log** - View the agent's plan & progress |
| `Ctrl+L` | **Clear Chat** |
| `Ctrl+B` | **Toggle Sidebar** |
| `Ctrl+Q` | **Quit** |

### Common Commands
- `/scan` - Scan project structure
- `/index` - Index the current project for context
- `/study <file>` - Teach ARIA about a specific file
- `/plan` - View the current task plan

---

## 📝 VS Code Extension

The VS Code extension integrates ARIA directly into your editor, allowing it to see your open files and selections.

### Usage
1. Open VS Code.
2. Click the **ARIA icon** in the Activity Bar.
3. The server starts automatically. Start chatting!

### Features
- **Context Awareness**: ARIA knows what file you are looking at.
- **Smart Actions**:
  - Select code and run **"ARIA: Refactor Code"**
  - Right-click and choose **"ARIA: Explain Code"**
  - **"ARIA: Generate Tests"** for the active function
- **Integrated Terminal**: ARIA can run terminals inside VS Code to execute its plans.

---

## ⚙️ Configuration

ARIA is configured via a `.env` file in the project directory or `~/.aria/.env`.

### Recommended Setup (Local AI)
```bash
# .env
LLM_PROVIDER=ollama-external
DEFAULT_MODEL=qwen3-8b
OLLAMA_EXTERNAL_HOST=http://localhost:11434
```

### Cloud Providers
```bash
# .env
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
```

### Operation Modes
- **AUTO**: Executes actions (file edits, commands) automatically. Best for autonomous tasks.
- **NORMAL**: Confirms destructive actions (like overwriting files) but runs safe commands automatically. (*Default*)
- **SAFE**: Asks for confirmation before *every* action.

---

## 🧠 Memory & Study System

ARIA has a persistent memory powered by SQLite.

- **Indexing**: Run `/index` to let ARIA "read" your entire project. It creates vector embeddings to find relevant code later.
- **Studying**: Run `/study docs/architecture.md` to force ARIA to "memorize" a document. It will reference this knowledge in future conversations.
- **File Locking**: In TUI, use `@filename` or `/lock filename` to manually pin a file to the context window.

---

## 🏗️ Architecture

ARIA consists of two main parts:
1.  **Core Backend (`aria`)**: A Go application that handles LLM communication, file operations, memory (SQLite), and tool execution. It runs as either a TUI or a REST API server.
2.  **Clients**:
    - **TUI**: Built-in Bubble Tea interface.
    - **VS Code Extension**: TypeScript client that talks to the backend via HTTP.

## 📄 License

MIT License
