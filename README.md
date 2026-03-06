@ -1,229 +1,149 @@
# ARIA  
### Adaptive Real-time Intelligence Assistant

![ARIA TUI](https://github.com/martin861101/agentic-coding-assistant_cli_tui_web/raw/master/Img/aria.png)

> An agentic AI coding assistant that can read, write, execute, and reason — directly in your terminal or VS Code.

---

## 🚦 Project Status

![Go Version](https://img.shields.io/badge/Go-1.21+-00ADD8?logo=go)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS-blue)
![UI](https://img.shields.io/badge/UI-Terminal%20%7C%20VS%20Code-purple)
![Agentic](https://img.shields.io/badge/Mode-Agentic_AI-red)
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

## ✨ What is ARIA?

ARIA is not a chatbot.  
It is an **agentic AI assistant** designed to **take action inside real codebases**.

ARIA can:
* Read and understand project files
* Edit and refactor code
* Execute shell commands and tests
* Search the web
* Maintain long-term project memory
## 📦 Installation

All while remaining **local-first**, **transparent**, and **developer-controlled**.

---

## ⚡ Quick Start (Local AI)
### 1. Build the Core Binary
ARIA's intelligence is powered by a shared Go backend. You need to build this first.

```bash
git clone [https://github.com/yourusername/aria-go.git](https://github.com/yourusername/aria-go.git)
# Clone the repository
git clone https://github.com/yourusername/aria-go.git
cd aria-go

# Build the binary (requires Go 1.21+ and CGO for SQLite)
CGO_ENABLED=1 go build -o aria .
./aria
```

### Requirements
* **Go 1.21+**
* **CGO enabled** (Required for SQLite)

---

## 🚀 Core Features

### 🧠 Agentic Workflow
ARIA follows a deterministic execution loop:  
**Reason → Plan → Execute** Every action is planned, logged, and auditable.

### 📂 Deep Project Awareness
* Full codebase indexing (RAG)
* Context-aware responses
* File locking and pinning
* Persistent memory across sessions
* Study specific documents or files

### 🔌 Multi-LLM Support

| Provider | Execution |
| :--- | :--- |
| **Ollama** | Local (default) |
| **Google Gemini** | Cloud |
| **OpenAI** | Cloud |
| **Anthropic Claude** | Cloud |
| **OpenRouter** | Hybrid |

Switch providers and models instantly without restarting.
# Verify it works
./aria --help
```

### 🛡️ Safety Modes
### 2. Install VS Code Extension (Optional)
If you prefer working in VS Code:

| Mode | Behavior |
| :--- | :--- |
| **AUTO** | Fully autonomous |
| **NORMAL** | Confirms destructive actions (default) |
| **SAFE** | Confirms every action |
```bash
cd vscode-extension
npm install
npm run compile
npx vsce package
code --install-extension aria-assistant-1.0.0.vsix
```

---

## 🖥️ Terminal UI (TUI)
## 🖥️ ARIA TUI (Terminal Interface)

A fast, keyboard-driven interface built with **Bubble Tea**.
The Terminal User Interface provides a beautiful, keyboard-centric way to interact with ARIA directly from your shell.

![ARIA TUI](https://github.com/martin861101/agentic-coding-assistant_cli_tui_web/raw/master/Img/Tui1.jpg)

**Launch:**
### Usage
```bash
# Start the TUI
./aria
```


### Keyboard Shortcuts
| Key | Action |
| :--- | :--- |
| `Ctrl + P` | Command Palette |
| `Ctrl + G` | Select Model |
| `Ctrl + O` | Select Provider |
| `Ctrl + E` | Toggle Safety Mode |
| `Ctrl + T` | Task Log |
| `Ctrl + L` | Clear Chat |
| `Ctrl + Q` | Quit |

### Slash Commands
* `/scan` - Scan project structure
* `/index` - Index the entire codebase
* `/study FILE` - Teach ARIA a specific file
* `/plan` - View execution plan

---

## 📸 Screenshots

### Agent Task Execution
![Task Execution](https://raw.githubusercontent.com/martin861101/agentic-coding-assistant_cli_tui_web/master/Img/taskview.jpg)
* Live execution phase indicator
* Explicit task breakdown with progress
* Per-step completion state
* Timestamped execution log

### Transparent Planning & Reasoning
* Reasoning → Tasks → Progress pipeline
* Deterministic planning
* Human-readable execution flow
* Designed for auditability and safety

### Real Codebase Interaction
* Platform-agnostic file operations
* No OS-specific APIs
* Explainable and traceable changes
* Works across Linux, macOS, and containers
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

## 🧩 VS Code Extension
## 📝 VS Code Extension

ARIA integrates directly into VS Code.
The VS Code extension integrates ARIA directly into your editor, allowing it to see your open files and selections.

![ARIA VS Code Extension]![ARIA TUI](https://github.com/martin861101/agentic-coding-assistant_cli_tui_web/raw/master/Img/Vscode.jpg)
### Usage
1. Open VS Code.
2. Click the **ARIA icon** in the Activity Bar.
3. The server starts automatically. Start chatting!

### Features
* Awareness of open files and selections
* Context-aware refactoring and explanations
* Test generation from selected code
* Integrated terminal execution

### Installation
```bash
cd vscode-extension
npm install
npm run compile
npx vsce package
code --install-extension aria-assistant-1.0.0.vsix
```
- **Context Awareness**: ARIA knows what file you are looking at.
- **Smart Actions**:
  - Select code and run **"ARIA: Refactor Code"**
  - Right-click and choose **"ARIA: Explain Code"**
  - **"ARIA: Generate Tests"** for the active function
- **Integrated Terminal**: ARIA can run terminals inside VS Code to execute its plans.

---

## ⚙️ Configuration

ARIA is configured using a `.env` file located in the project root or `~/.aria/.env`.
ARIA is configured via a `.env` file in the project directory or `~/.aria/.env`.

### Local (Recommended)
```env
### Recommended Setup (Local AI)
```bash
# .env
LLM_PROVIDER=ollama-external
DEFAULT_MODEL=qwen3-8b
OLLAMA_EXTERNAL_HOST=http://localhost:11434
```

### Cloud Providers
```env
```bash
# .env
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
```

---

## 🧠 Memory System

ARIA uses persistent SQLite-backed memory.
* `/index` reads and embeds the entire project.
* `/study docs/architecture.md` permanently stores documentation.
* `@filename` or `/lock filename` pins files into context.
* Memory persists across sessions.
### Operation Modes
- **AUTO**: Executes actions (file edits, commands) automatically. Best for autonomous tasks.
- **NORMAL**: Confirms destructive actions (like overwriting files) but runs safe commands automatically. (*Default*)
- **SAFE**: Asks for confirmation before *every* action.

---

## 🏗️ Architecture

```text
aria (Go backend)
│
├─ LLM Providers
├─ Tool Executor
├─ File System Access
├─ Memory (SQLite + embeddings)
├─ Terminal UI (Bubble Tea)
└─ REST API
      └─ VS Code Extension (TypeScript)
```
## 🧠 Memory & Study System

---
ARIA has a persistent memory powered by SQLite.

## 🛠️ Built For
* Terminal-first developers
* Local-first AI workflows
* Agent experimentation
* Long-running codebases
* Transparent and auditable automation
- **Indexing**: Run `/index` to let ARIA "read" your entire project. It creates vector embeddings to find relevant code later.
- **Studying**: Run `/study docs/architecture.md` to force ARIA to "memorize" a document. It will reference this knowledge in future conversations.
- **File Locking**: In TUI, use `@filename` or `/lock filename` to manually pin a file to the context window.

---

## 🧭 Roadmap
- [ ] Plugin system for custom tools
- [ ] Multi-agent orchestration
- [ ] Git-aware planning
- [ ] Session replay and audit logs
- [ ] Remote agent execution
## 🏗️ Architecture

---
ARIA consists of two main parts:
1.  **Core Backend (`aria`)**: A Go application that handles LLM communication, file operations, memory (SQLite), and tool execution. It runs as either a TUI or a REST API server.
2.  **Clients**:
    - **TUI**: Built-in Bubble Tea interface.
    - **VS Code Extension**: TypeScript client that talks to the backend via HTTP.

## 📄 License

MIT License
