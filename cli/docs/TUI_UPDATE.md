Features
     Layout:
     ┌─────────────────────────────────────────────────────────┐
     │  ARIA - Adaptive Real-time Intelligence Assistant       │
     ├──────────────┬──────────────────────────────────────────┤
     │ 📁 Files     │  OLLAMA / mistral:latest  │  MODE: AUTO │
     │              ├──────────────────────────────────────────┤
     │ 📁 src/      │                                          │
     │   🐍 main.py │  Welcome to ARIA!                        │
     │   🐍 utils.py│                                          │
     │ 📋 config.json│ You: Hello                              │
     │ 📝 README.md │                                          │
     │              │  ARIA: Hi! How can I help?               │
     │              │                                          │
     ├──────────────┼──────────────────────────────────────────┤
     │ Dir: aria/   │  Ask anything or describe what to do... │
     │ Mode: AUTO   │  Ctrl+P: Commands • Ctrl+M: Model •...  │
     └──────────────┴──────────────────────────────────────────┘
     Keyboard Shortcuts:
     | Key | Action |
     |-----|--------|
     | Ctrl+P | Command palette |
     | Ctrl+M | Select model (modal) |
     | Ctrl+O | Select provider (modal) |
     | Ctrl+E | Select mode (modal) |
     | Ctrl+L | Clear chat |
     | Ctrl+B | Toggle sidebar |
     | Ctrl+Q | Quit |
     Unique Elements:
     1. File Tree Sidebar - Browse project files with icons
     2. Command Palette - VS Code-style fuzzy search (Ctrl+P)
     3. Modal Selectors - Beautiful popups for model/provider/mode
     4. Status Bar - Live display of provider, model, mode
     5. Streaming Responses - AI responses stream in real-time
     6. Color-coded Modes - Green (auto), Yellow (safe), Blue (normal)
     To Run:
     # Install textual
     pip install textual
     # Run the new TUI
     python tui.py
     Or to keep the old CLI available too:
     python aria.py   # Old CLI interface
     python tui.py    # New Textual TUI
     Commands (same as before):
     /model          - Open model selector
     /provider       - Open provider selector
     /mode           - Open mode selector
     /auto           - Quick switch to auto
     /safe           - Quick switch to safe
     /read <file>    - Read a file
     /clear          - Clear chat
     /status         - Show status
     /help           - Show help
