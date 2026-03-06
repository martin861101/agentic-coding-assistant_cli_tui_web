# ARIA - Logic & Architecture Documentation

## Overview
ARIA (Adaptive Real-time Intelligence Assistant) is an agentic AI coding assistant designed to run as a CLI tool (TUI) or a backend server (for VS Code). It follows a structured "Think -> Reason -> Plan -> Execute" workflow to handle complex coding tasks autonomously.

## Core Architecture

### 1. Entry Points
- **CLI (TUI)**: `main.go` initializes the TUI (`internal/tui`).
- **Server**: `internal/server` provides an HTTP API, primarily for the VS Code extension.

### 2. Configuration (`internal/config`)
- **Sources**: Environment variables, `.env` files (local and `~/.aria/.env`).
- **Modes**:
  - `auto`: Executes actions without confirmation.
  - `safe`: Requires confirmation for all actions.
  - `normal`: Requires confirmation for destructive actions (write, run, shell).
- **Providers**: Supports Ollama, Gemini, OpenRouter, OpenAI, and Anthropic.

### 3. Orchestration (`internal/orchestrator`)
The core "brain" of the application. It processes complex queries through a phased workflow:
1.  **Thinking**: Analyzes the user request (Input -> Analysis).
2.  **Reasoning**: Determines the approach and challenges (Analysis -> Reasoning).
3.  **Planning**: Creates a structured task list (Reasoning -> Plan).
4.  **Executing**: Iterates through tasks, executing actions for each.
5.  **Verifying**: Summarizes and checks results.

**Key Logic:**
- `IsComplex(query)`: Heuristic to decide between simple direct response and full orchestration.
- **Event System**: Emits events (thinking, task, action, output) for UI updates.

### 4. Planning (`internal/planner`)
Manages the state of the task list.
- **Structure**: `Plan` contains `Reasoning` and a list of `Tasks`.
- **Parsing**: Uses Regex to extract `<task_plan>` and `<task_update>` blocks from LLM responses.
- **Status Tracking**: Pending -> In Progress -> Completed/Failed.

### 5. Agents (`internal/agents`)
Specialized personas for specific tasks. A `Coordinator` routes tasks to the most capable agent.
- **Capabilities**:
  - `CodeReview`: Analyzes code for bugs/style.
  - `Refactoring`: Improves structure/SOLID principles.
  - `Debugging`: Identifies root causes and fixes.
  - `Testing`: Generates unit/integration tests.
  - `Documentation`: Writes docstrings and READMEs.

### 6. Memory & Knowledge (`internal/memory`)
SQLite-backed persistent memory (`~/.aria/memory.db`).
- **Conversations**: Stores chat history.
- **Code Chunks**: Indexes project files (RAG context).
- **Knowledge**: "Studies" Markdown files (ingests documentation) for retrieval.
- **Project Indexing**: Scans and chunks codebases.

### 7. Learning System (`internal/learning`)
Adaptive feedback loop (`~/.aria/learning.db`).
- **Feedback**: Records user corrections and ratings.
- **Patterns**: Learns preferences (e.g., "When asked about X, prefer Y").
- **Prompt Enhancement**: Dynamically injects learned patterns into the system prompt.

### 8. Actions & Tools (`internal/actions`, `internal/tools`)
The "hands" of the agent.
- **Parsing**: XML-like tags (`<action:type>...`) and Markdown code blocks are parsed from LLM output.
- **Tools**:
  - `read`, `write`, `ls`: File system operations.
  - `run`: Code execution (Python, Bash, Node, Go).
  - `shell`: Shell command execution.
  - `search`: DuckDuckGo web search.
  - `fetch`: Web scraping.
- **Safety**: Checks `OperationMode` to determine if user confirmation is needed.

## Logic Flow

1.  **User Input**: Received via TUI or API.
2.  **Context Building**:
    - Fetches relevant file context (locked files via `@`).
    - Retrieves memory context (RAG).
    - Enhances prompt with learned patterns.
3.  **Routing**:
    - **Simple**: Direct LLM stream + Action parsing.
    - **Complex**: Triggers Orchestrator (Think -> Reason -> Plan -> Execute).
    - **Command**: Specialized commands (`/review`, `/test`) trigger Agent Coordinator.
4.  **Execution**:
    - LLM generates response with Action blocks.
    - `actions.Executor` parses blocks.
    - Checks permissions/confirmation mode.
    - Calls `internal/tools` to perform OS operations.
    - Returns output to LLM (loop) or User.

## Features

- **Multi-Provider LLM Support**: Switch between local (Ollama) and cloud models on the fly.
- **Context Management**: Manual file locking (`/lock`, `@file`) and automatic RAG.
- **Self-Correction**: Learning system adapts to user preferences over time.
- **Specialized Agents**: Dedicated prompts for specific engineering tasks.
- **TUI Features**:
  - Command Palette (`Ctrl+P`).
  - Task Logging (`Ctrl+T`).
  - Markdown Rendering.
  - Interactive Mode Switching.

## Potential Issues & Bugs (Analysis)

1.  **Regex Parsing**:
    - Action parsing in `internal/actions/actions.go` relies on regex patterns. This can be brittle if the LLM malforms the XML-like tags or code blocks.
    - *Risk*: Missed actions or partial execution if the model output drifts from expected format.

2.  **Code Execution**:
    - `internal/tools/tools.go` executes code directly on the host machine (`exec.Command`).
    - *Risk*: Lack of sandboxing. `rm -rf /` is possible if not caught by "Safe" mode confirmation.

3.  **Learning Logic**:
    - `extractKeyTerms` in `internal/learning/learning.go` is primitive (first 50 chars of query).
    - *Limitation*: Might not capture the actual "intent" for pattern matching, leading to poor recall of learned preferences.

4.  **Memory Concurrency**:
    - SQLite is used with `db.SetMaxOpenConns(1)`.
    - *Limitation*: While safe, this might be a bottleneck if the Server and TUI try to access memory simultaneously or under high load.

5.  **Token Limits**:
    - File reading/context injection (`ToPromptSection`) has hardcoded limits (e.g., 2000 chars/lines).
    - *Limitation*: Large files might be truncated silently or lose critical context.

6.  **Orchestrator Error Handling**:
    - If an orchestration step fails (e.g., Planning), it might default to a generic error or stop.
    - `ParseTaskPlanFromResponse` might fail if the model decides to change the list format.
