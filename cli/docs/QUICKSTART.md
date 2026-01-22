# ARIA Quick Start Guide

## What is ARIA?

ARIA is an **AI coding agent** that lives in your terminal. Unlike simple chatbots, ARIA can actually **take action** - reading files, writing code, running commands - all from natural language.

Just say what you want:
```
"Look at my app and fix any syntax errors"
"Add error handling to utils.py"
"Create a new REST API endpoint for users"
```

And ARIA does it!

## Prerequisites

- Python 3.8+ 
- Ollama installed and running

## Quick Install

```bash
# 1. Install Ollama (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh

# 2. Pull a model
ollama pull mistral

# 3. Setup ARIA
cd aria
chmod +x setup.sh
./setup.sh

# 4. Run ARIA
source venv/bin/activate
python aria.py
```

## Operation Modes

ARIA has three modes for different workflows:

| Mode | Command | Description |
|------|---------|-------------|
| **AUTO** | `/auto` | Executes ALL actions without prompts - fastest |
| **SAFE** | `/safe` | Confirms before ANY file changes - safest |
| **NORMAL** | `/mode normal` | Smart confirmations - balanced (default) |

**Tip:** Use `/auto` when you trust ARIA to make changes, `/safe` when working on critical code.

## Using ARIA

### Natural Language (Agentic Mode)

Just describe what you want! ARIA will:
1. **Read** the relevant files
2. **Analyze** and understand the code
3. **Plan** the changes needed
4. **Execute** the changes automatically

**Examples:**

```
[A] You: Look at my project and fix any issues

ARIA: Let me scan your project first...
      [Reading main.py...]  OK
      [Reading utils.py...]  OK
      
      I found 3 issues:
      1. Missing import in main.py line 5
      2. Syntax error in utils.py line 23
      3. Unused variable in main.py line 42
      
      Let me fix these...
      [Writing main.py...]  OK
      [Writing utils.py...]  OK
      
      Done! Fixed all 3 issues.
```

```
[A] You: Add a new function to calculate fibonacci numbers in math_utils.py

ARIA: Let me read the current file first...
      [Reading math_utils.py...]  OK
      
      I'll add a fibonacci function that matches your existing style.
      [Writing math_utils.py...]  OK
      
      Added the fibonacci function with memoization for efficiency!
```

```
[A] You: Create a new config.yaml file with database settings

ARIA: [Writing config.yaml...]  OK
      
      Created config.yaml with standard database configuration.
```

### Quick Commands

When you need direct control:

| Command | Description |
|---------|-------------|
| `/read <file>` | Read and display a file |
| `/ls [dir]` | List directory contents |
| `/run <code>` | Execute Python code |
| `/scan` | Scan project structure |
| `/status` | Show current mode and model |

### Specialist Agents

For specialized tasks, use these commands:

| Command | What it does |
|---------|--------------|
| `/review` | Deep code review (security, performance, bugs) |
| `/debug` | Debug errors with stack trace analysis |
| `/test` | Generate unit tests for your code |
| `/docs` | Generate documentation |
| `/refactor` | Get refactoring suggestions |

### Mode Switching

```
/auto     # Switch to auto mode (no confirmations)
/safe     # Switch to safe mode (confirm everything)
/mode normal  # Back to default
```

## Example Session

```
$ python aria.py

╭────────────────────────────────────────────────────╮
│  ARIA - Adaptive Real-time Intelligence Assistant  │
│  Your AI Coding Agent - Powered by Ollama          │
│                                                    │
│  Model: mistral:latest  |  Mode: NORMAL            │
│                                                    │
│  Just describe what you want - I'll read, plan,    │
│  and execute!                                      │
╰────────────────────────────────────────────────────╯

[N] You: /auto

Switched to AUTO mode

[A] You: Scan my project and tell me what you see

ARIA: Let me look at your project structure...
      [Listing .]  OK

      Found 12 files:
      - main.py (Python - entry point)
      - utils.py (Python - utilities)
      - config.py (Python - configuration)
      - requirements.txt (Python dependencies)
      - README.md (Documentation)
      ...

[A] You: Read main.py and add better error handling

ARIA: [Reading main.py...]  OK

      I see the current code doesn't handle file not found errors.
      Let me add proper try/except blocks...

      [Writing main.py...]  OK

      Added error handling for:
      - FileNotFoundError with user-friendly message
      - ConnectionError with retry logic
      - Generic exceptions with logging

[A] You: Run the tests to make sure it works

ARIA: [Running code...]  OK

      All tests pass! Output:
      =====================================
      5 passed in 0.23s
      =====================================

[A] You: /exit
Goodbye!
```

## Tips

1. **Start with `/auto` for speed** - You can always undo with git
2. **Use `/scan` first** - Helps ARIA understand your project
3. **Be specific** - "Fix the auth bug in login.py" works better than "fix bugs"
4. **Check `/status`** - Know what mode you're in
5. **Use `/safe` for critical changes** - Better safe than sorry

## Command Reference

| Command | Description |
|---------|-------------|
| `/auto` | Switch to auto mode |
| `/safe` | Switch to safe mode |
| `/mode <name>` | Switch mode |
| `/read <file>` | Read a file |
| `/ls [dir]` | List files |
| `/run <code>` | Execute code |
| `/scan` | Scan project |
| `/model <name>` | Switch LLM model |
| `/review` | Code review agent |
| `/debug` | Debug agent |
| `/test` | Test generation agent |
| `/docs` | Documentation agent |
| `/status` | Show status |
| `/memory` | Memory info |
| `/clear` | Clear conversation |
| `/help` | Show help |
| `/exit` | Exit ARIA |

## Troubleshooting

**"Connection refused"**
- Start Ollama: `ollama serve`

**Model not found**
- Pull it: `ollama pull mistral`

**Actions not executing**
- Check you're in AUTO mode: `/auto`
- Or confirm prompts in SAFE mode

---

**Now go build something awesome with ARIA!**
