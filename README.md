# ARIA  
### Adaptive Real-time Intelligence Assistant

> An agentic AI coding assistant that can read, write, execute, and reason — directly in your terminal or VS Code.

---

## 🚦 Project Status

![Go Version](https://img.shields.io/badge/Go-1.21+-00ADD8?logo=go)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS-blue)
![UI](https://img.shields.io/badge/UI-Terminal%20%7C%20VS%20Code-purple)
![Agentic](https://img.shields.io/badge/Mode-Agentic_AI-red)

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

All while remaining **local-first**, **transparent**, and **developer-controlled**.

---

## ⚡ Quick Start (Local AI)

```bash
git clone [https://github.com/yourusername/aria-go.git](https://github.com/yourusername/aria-go.git)
cd aria-go

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

### 🛡️ Safety Modes

| Mode | Behavior |
| :--- | :--- |
| **AUTO** | Fully autonomous |
| **NORMAL** | Confirms destructive actions (default) |
| **SAFE** | Confirms every action |

---

## 🖥️ Terminal UI (TUI)

A fast, keyboard-driven interface built with **Bubble Tea**.

![View]
(https://github.com/martin861101/agentic-coding-assistant_cli_tui_web/Img/Tui1.jpg)

**Launch:**
```bash
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
![Task Execution](https://github.com/yourusername/aria-go/raw/main/assets/execution-flow.png)
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

---

## 🧩 VS Code Extension

ARIA integrates directly into VS Code.

![ARIA VS Code Extension](https://github.com/yourusername/aria-go/raw/main/assets/vscode-screenshot.png)

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

---

## ⚙️ Configuration

ARIA is configured using a `.env` file located in the project root or `~/.aria/.env`.

### Local (Recommended)
```env
LLM_PROVIDER=ollama-external
DEFAULT_MODEL=qwen3-8b
OLLAMA_EXTERNAL_HOST=http://localhost:11434
```

### Cloud Providers
```env
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

---

## 🛠️ Built For
* Terminal-first developers
* Local-first AI workflows
* Agent experimentation
* Long-running codebases
* Transparent and auditable automation

---

## 🧭 Roadmap
- [ ] Plugin system for custom tools
- [ ] Multi-agent orchestration
- [ ] Git-aware planning
- [ ] Session replay and audit logs
- [ ] Remote agent execution

---

## 📄 License
MIT License
