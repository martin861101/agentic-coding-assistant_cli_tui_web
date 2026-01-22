"""
ARIA - Textual TUI
A modern, unique terminal interface for ARIA
"""
import asyncio
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import (
    Button, Footer, Header, Input, Label, ListItem, ListView,
    Markdown, OptionList, RichLog, Rule, Static, Switch, Tree, LoadingIndicator
)
from textual.widgets.option_list import Option
from textual.widgets.tree import TreeNode
from rich.syntax import Syntax
from rich.text import Text
from rich.panel import Panel
from rich.markdown import Markdown as RichMarkdown

from config import config, OperationMode, PROVIDER_MODELS
from llm_interface import LLMInterface
from tools import ToolRegistry, ReadFileTool, WriteFileTool, ListFilesTool, ExecuteCodeTool


# ============================================================================
# Custom Widgets
# ============================================================================

class StatusBar(Static):
    """Custom status bar showing provider, model, and mode"""
    
    provider = reactive("ollama")
    model = reactive("mistral:latest")
    mode = reactive("normal")
    
    def render(self) -> Text:
        mode_colors = {"auto": "green", "safe": "yellow", "normal": "blue"}
        mode_color = mode_colors.get(self.mode, "white")
        
        text = Text()
        text.append("  ", style="dim")
        text.append(self.provider.upper(), style="bold cyan")
        text.append(" / ", style="dim")
        text.append(self.model, style="yellow")
        text.append("  │  ", style="dim")
        text.append("MODE: ", style="dim")
        text.append(self.mode.upper(), style=f"bold {mode_color}")
        text.append("  ", style="dim")
        return text


class MessageBubble(Static):
    """A chat message bubble"""
    
    def __init__(self, content: str, is_user: bool = False, timestamp: str = "", **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now().strftime("%H:%M")
    
    def compose(self) -> ComposeResult:
        yield Static(self.content, classes="message-content")


class ThinkingIndicator(Static):
    """Animated thinking indicator"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dots = 0
    
    def on_mount(self) -> None:
        self.set_interval(0.3, self._do_animate)
    
    def _do_animate(self) -> None:
        self._dots = (self._dots + 1) % 4
        dots = "●" * self._dots + "○" * (3 - self._dots)
        self.update(f"[cyan]Thinking {dots}[/cyan]")


class FileTreeWidget(Tree):
    """File tree browser"""
    
    def __init__(self, path: str = ".", **kwargs):
        super().__init__(label=path, **kwargs)
        self.path = Path(path)
        self.guide_depth = 3
    
    def on_mount(self) -> None:
        self._load_directory(self.root, self.path)
        self.root.expand()
    
    def _load_directory(self, node: TreeNode, path: Path) -> None:
        try:
            entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
            for entry in entries[:50]:  # Limit entries
                if entry.name.startswith('.'):
                    continue
                if entry.is_dir():
                    branch = node.add(f"[blue]{entry.name}/[/blue]", data=entry)
                    branch.allow_expand = True
                else:
                    icon = self._get_file_icon(entry.name)
                    node.add_leaf(f"{icon} {entry.name}", data=entry)
        except PermissionError:
            pass
    
    def _get_file_icon(self, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        icons = {
            '.py': '🐍', '.js': '📜', '.ts': '📘', '.json': '📋',
            '.md': '📝', '.txt': '📄', '.yaml': '⚙️', '.yml': '⚙️',
            '.html': '🌐', '.css': '🎨', '.sh': '💻', '.sql': '🗃️',
        }
        return icons.get(ext, '📄')
    
    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        node = event.node
        if node.data and isinstance(node.data, Path) and node.data.is_dir():
            if not node.children:
                self._load_directory(node, node.data)


# ============================================================================
# Modal Screens
# ============================================================================

class CommandPalette(ModalScreen):
    """Command palette modal"""
    
    BINDINGS = [
        Binding("escape", "close", "Close"),
    ]
    
    CSS = """
    CommandPalette {
        align: center middle;
    }
    
    #palette-container {
        width: 60;
        height: auto;
        max-height: 20;
        background: $surface;
        border: tall $primary;
        padding: 1;
    }
    
    #palette-input {
        margin-bottom: 1;
    }
    
    #palette-options {
        height: auto;
        max-height: 15;
    }
    """
    
    def __init__(self, commands: List[Dict[str, str]], **kwargs):
        super().__init__(**kwargs)
        self.commands = commands
    
    def compose(self) -> ComposeResult:
        with Container(id="palette-container"):
            yield Input(placeholder="Type a command...", id="palette-input")
            yield OptionList(
                *[Option(f"{cmd['name']}  [dim]{cmd['desc']}[/dim]", id=cmd['id']) 
                  for cmd in self.commands],
                id="palette-options"
            )
    
    def on_mount(self) -> None:
        self.query_one("#palette-input", Input).focus()
    
    @on(Input.Changed, "#palette-input")
    def filter_options(self, event: Input.Changed) -> None:
        query = event.value.lower()
        option_list = self.query_one("#palette-options", OptionList)
        option_list.clear_options()
        for cmd in self.commands:
            if query in cmd['name'].lower() or query in cmd['desc'].lower():
                option_list.add_option(Option(f"{cmd['name']}  [dim]{cmd['desc']}[/dim]", id=cmd['id']))
    
    @on(OptionList.OptionSelected, "#palette-options")
    def select_option(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(event.option.id)
    
    def action_close(self) -> None:
        self.dismiss(None)


class ModelSelector(ModalScreen):
    """Model selection modal"""
    
    BINDINGS = [Binding("escape", "close", "Close")]
    
    CSS = """
    ModelSelector {
        align: center middle;
    }
    
    #model-container {
        width: 70;
        height: auto;
        max-height: 25;
        background: $surface;
        border: tall $primary;
        padding: 1;
    }
    
    #model-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    """
    
    def __init__(self, provider: str, models: List[str], current: str, **kwargs):
        super().__init__(**kwargs)
        self.provider = provider
        self.models = models
        self.current = current
    
    def compose(self) -> ComposeResult:
        with Container(id="model-container"):
            yield Label(f"Select Model ({self.provider})", id="model-title")
            yield OptionList(
                *[Option(f"{'● ' if m == self.current else '  '}{m}", id=m) for m in self.models],
                id="model-options"
            )
    
    @on(OptionList.OptionSelected)
    def select_model(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(event.option.id)
    
    def action_close(self) -> None:
        self.dismiss(None)


class ProviderSelector(ModalScreen):
    """Provider selection modal"""
    
    BINDINGS = [Binding("escape", "close", "Close")]
    
    CSS = """
    ProviderSelector {
        align: center middle;
    }
    
    #provider-container {
        width: 50;
        height: auto;
        background: $surface;
        border: tall $primary;
        padding: 1;
    }
    
    #provider-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    """
    
    def __init__(self, providers: List[Dict], current: str, **kwargs):
        super().__init__(**kwargs)
        self.providers = providers
        self.current = current
    
    def compose(self) -> ComposeResult:
        with Container(id="provider-container"):
            yield Label("Select Provider", id="provider-title")
            options = []
            for p in self.providers:
                status = "[green]●[/green]" if p['available'] else "[red]○[/red]"
                marker = " [cyan](current)[/cyan]" if p['current'] else ""
                options.append(Option(f"{status} {p['name']}{marker}", id=p['name']))
            yield OptionList(*options, id="provider-options")
    
    @on(OptionList.OptionSelected)
    def select_provider(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(event.option.id)
    
    def action_close(self) -> None:
        self.dismiss(None)


class ModeSelector(ModalScreen):
    """Mode selection modal"""
    
    BINDINGS = [Binding("escape", "close", "Close")]
    
    CSS = """
    ModeSelector {
        align: center middle;
    }
    
    #mode-container {
        width: 55;
        height: auto;
        background: $surface;
        border: tall $primary;
        padding: 1;
    }
    """
    
    def __init__(self, current: str, **kwargs):
        super().__init__(**kwargs)
        self.current = current
    
    def compose(self) -> ComposeResult:
        modes = [
            ("auto", "Auto-execute all actions", "green"),
            ("safe", "Confirm before changes", "yellow"),
            ("normal", "Smart confirmations", "blue"),
        ]
        with Container(id="mode-container"):
            yield Label("Select Mode", id="mode-title")
            options = []
            for mode, desc, color in modes:
                marker = " ●" if mode == self.current else ""
                options.append(Option(f"[{color}]{mode.upper()}[/{color}]{marker}  [dim]{desc}[/dim]", id=mode))
            yield OptionList(*options)
    
    @on(OptionList.OptionSelected)
    def select_mode(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(event.option.id)
    
    def action_close(self) -> None:
        self.dismiss(None)


# ============================================================================
# Main Application
# ============================================================================

class AriaTUI(App):
    """ARIA - Adaptive Real-time Intelligence Assistant"""
    
    CSS = """
    /* Main Layout */
    #main-container {
        layout: horizontal;
    }
    
    /* Sidebar */
    #sidebar {
        width: 30;
        background: $surface;
        border-right: tall $primary-background;
    }
    
    #sidebar-header {
        height: 3;
        background: $primary;
        content-align: center middle;
        text-style: bold;
    }
    
    #file-tree {
        height: 1fr;
        padding: 0 1;
    }
    
    #sidebar-status {
        height: auto;
        padding: 1;
        background: $surface-darken-1;
        border-top: solid $primary-background;
    }
    
    /* Chat Area */
    #chat-container {
        width: 1fr;
    }
    
    #status-bar {
        height: 1;
        background: $surface-darken-2;
        dock: top;
    }
    
    #chat-log {
        height: 1fr;
        padding: 1;
        background: $background;
    }
    
    /* Input Area */
    #input-area {
        height: auto;
        padding: 1;
        background: $surface;
        border-top: tall $primary-background;
    }
    
    #chat-input {
        margin-bottom: 0;
    }
    
    #input-hints {
        height: 1;
        color: $text-muted;
        text-align: center;
    }
    
    /* Message Bubbles */
    .user-message {
        background: $primary-darken-2;
        margin: 1 0 1 10;
        padding: 1;
        border: round $primary;
    }
    
    .assistant-message {
        background: $surface;
        margin: 1 10 1 0;
        padding: 1;
        border: round $secondary;
    }
    
    .system-message {
        color: $text-muted;
        text-align: center;
        margin: 1 5;
    }
    
    /* Thinking Indicator */
    ThinkingIndicator {
        height: 1;
        margin: 1 0;
        text-align: center;
    }
    
    /* Mode Colors */
    .mode-auto {
        color: $success;
    }
    
    .mode-safe {
        color: $warning;
    }
    
    .mode-normal {
        color: $primary;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+p", "command_palette", "Commands", show=True),
        Binding("ctrl+m", "select_model", "Model", show=True),
        Binding("ctrl+o", "select_provider", "Provider", show=True),
        Binding("ctrl+e", "select_mode", "Mode", show=True),
        Binding("ctrl+l", "clear_chat", "Clear", show=True),
        Binding("ctrl+b", "toggle_sidebar", "Sidebar", show=True),
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("escape", "focus_input", "Focus Input", show=False),
    ]
    
    TITLE = "ARIA"
    SUB_TITLE = "Adaptive Real-time Intelligence Assistant"
    
    show_sidebar = reactive(True)
    
    def __init__(self):
        super().__init__()
        self.llm = LLMInterface()
        self.tool_registry = ToolRegistry()
        self._register_tools()
        self.operation_mode = config.operation_mode
        self.working_directory = Path.cwd()
        self._thinking = False
        
        # Build agentic prompt
        self.system_prompt = self._build_system_prompt()
    
    def _register_tools(self):
        self.tool_registry.register(ReadFileTool())
        self.tool_registry.register(WriteFileTool())
        self.tool_registry.register(ListFilesTool())
        self.tool_registry.register(ExecuteCodeTool())
    
    def _build_system_prompt(self) -> str:
        return """You are ARIA, an AI coding assistant in a terminal.
You can help with code, answer questions, and perform file operations.
Be concise but helpful. Use markdown formatting for code blocks.
When asked to read or modify files, use action blocks like:

To read: <action:read>path: filename</action:read>
To write: <action:write>path: filename
content: |
  file content here
</action:write>

Current directory: """ + str(self.working_directory)
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Horizontal(id="main-container"):
            # Sidebar
            with Container(id="sidebar"):
                yield Static("📁 Files", id="sidebar-header")
                yield FileTreeWidget(str(self.working_directory), id="file-tree")
                with Container(id="sidebar-status"):
                    yield Static(f"[dim]Dir:[/dim] {self.working_directory.name}/")
                    yield Static(f"[dim]Mode:[/dim] {self.operation_mode.value.upper()}")
            
            # Chat Area
            with Container(id="chat-container"):
                yield StatusBar(id="status-bar")
                yield RichLog(id="chat-log", wrap=True, highlight=True, markup=True)
                with Container(id="input-area"):
                    yield Input(placeholder="Ask anything or describe what you want to do...", id="chat-input")
                    yield Static("[dim]Ctrl+P: Commands  •  Ctrl+M: Model  •  Ctrl+E: Mode  •  Ctrl+Q: Quit[/dim]", id="input-hints")
        
        yield Footer()
    
    def on_mount(self) -> None:
        self._update_status_bar()
        self._add_welcome_message()
        self.query_one("#chat-input", Input).focus()
    
    def _update_status_bar(self) -> None:
        status = self.query_one("#status-bar", StatusBar)
        status.provider = self.llm.provider_name
        status.model = self.llm.model
        status.mode = self.operation_mode.value
    
    def _add_welcome_message(self) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write(Panel.fit(
            "[bold cyan]Welcome to ARIA![/bold cyan]\n\n"
            f"[dim]Provider:[/dim] [yellow]{self.llm.provider_name}[/yellow]\n"
            f"[dim]Model:[/dim] [yellow]{self.llm.model}[/yellow]\n"
            f"[dim]Mode:[/dim] [blue]{self.operation_mode.value.upper()}[/blue]\n\n"
            "[dim]Just describe what you want - I'll help you build it![/dim]",
            border_style="cyan"
        ))
    
    def _add_message(self, content: str, is_user: bool = False) -> None:
        log = self.query_one("#chat-log", RichLog)
        prefix = "[bold green]You:[/bold green] " if is_user else "[bold cyan]ARIA:[/bold cyan] "
        log.write(Text.from_markup(f"\n{prefix}"))
        if is_user:
            log.write(content)
        else:
            # Parse as markdown for assistant
            try:
                log.write(RichMarkdown(content))
            except:
                log.write(content)
    
    def _add_system_message(self, content: str) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write(Text.from_markup(f"\n[dim italic]{content}[/dim italic]"))
    
    @on(Input.Submitted, "#chat-input")
    def handle_input(self, event: Input.Submitted) -> None:
        message = event.value.strip()
        if not message:
            return
        
        input_widget = self.query_one("#chat-input", Input)
        input_widget.value = ""
        
        # Handle commands
        if message.startswith("/"):
            self._handle_command(message)
            return
        
        # Regular chat
        self._add_message(message, is_user=True)
        self._get_ai_response(message)
    
    def _handle_command(self, command: str) -> None:
        cmd = command.lower().strip()
        
        if cmd in ["/help", "/?"]:
            self._show_help()
        elif cmd == "/clear":
            self.action_clear_chat()
        elif cmd in ["/model", "/models"]:
            self.action_select_model()
        elif cmd in ["/provider", "/providers"]:
            self.action_select_provider()
        elif cmd in ["/mode", "/modes"]:
            self.action_select_mode()
        elif cmd == "/auto":
            self._set_mode("auto")
        elif cmd == "/safe":
            self._set_mode("safe")
        elif cmd == "/status":
            self._show_status()
        elif cmd.startswith("/read "):
            self._read_file(cmd[6:].strip())
        elif cmd.startswith("/model "):
            self.llm.switch_model(cmd[7:].strip())
            self._update_status_bar()
            self._add_system_message(f"Switched to model: {self.llm.model}")
        elif cmd.startswith("/provider "):
            self._switch_provider(cmd[10:].strip())
        else:
            self._add_system_message(f"Unknown command: {command}")
    
    def _show_help(self) -> None:
        help_text = """**Commands:**
- `/model` - Select model
- `/provider` - Select provider  
- `/mode` - Select mode (auto/safe/normal)
- `/auto` - Switch to auto mode
- `/safe` - Switch to safe mode
- `/read <file>` - Read a file
- `/clear` - Clear chat
- `/status` - Show status
- `/help` - Show this help

**Shortcuts:**
- `Ctrl+P` - Command palette
- `Ctrl+M` - Select model
- `Ctrl+O` - Select provider
- `Ctrl+E` - Select mode
- `Ctrl+L` - Clear chat
- `Ctrl+B` - Toggle sidebar
- `Ctrl+Q` - Quit"""
        self._add_message(help_text, is_user=False)
    
    def _show_status(self) -> None:
        status = f"""**ARIA Status**
- Provider: {self.llm.provider_name}
- Model: {self.llm.model}
- Mode: {self.operation_mode.value.upper()}
- Context: {self.llm.get_context_size()} messages
- Directory: {self.working_directory}"""
        self._add_message(status, is_user=False)
    
    def _set_mode(self, mode: str) -> None:
        mode_map = {"auto": OperationMode.AUTO, "safe": OperationMode.SAFE, "normal": OperationMode.NORMAL}
        if mode in mode_map:
            self.operation_mode = mode_map[mode]
            self._update_status_bar()
            self._add_system_message(f"Mode changed to {mode.upper()}")
    
    def _read_file(self, path: str) -> None:
        tool = self.tool_registry.get("ReadFileTool")
        if tool:
            result = tool.execute(file_path=path)
            if result.success:
                ext = Path(path).suffix.lower()
                lang = {'.py': 'python', '.js': 'javascript', '.json': 'json'}.get(ext, 'text')
                log = self.query_one("#chat-log", RichLog)
                log.write(f"\n[bold]📄 {path}[/bold]")
                log.write(Syntax(result.output, lang, theme="monokai", line_numbers=True))
            else:
                self._add_system_message(f"Error: {result.error}")
    
    def _switch_provider(self, provider: str) -> None:
        try:
            self.llm.switch_provider(provider)
            self._update_status_bar()
            self._add_system_message(f"Switched to {provider} ({self.llm.model})")
        except Exception as e:
            self._add_system_message(f"Error: {str(e)}")
    
    @work(exclusive=True, thread=True)
    def _get_ai_response(self, message: str) -> None:
        """Get AI response with streaming"""
        log = self.query_one("#chat-log", RichLog)
        
        # Show thinking
        self.call_from_thread(log.write, Text.from_markup("\n[bold cyan]ARIA:[/bold cyan] "))
        self.call_from_thread(log.write, Text.from_markup("[dim]thinking...[/dim]"))
        
        response = ""
        try:
            for token in self.llm.chat(message, self.system_prompt):
                response += token
            
            # Clear thinking and show response
            self.call_from_thread(log.clear)
            self.call_from_thread(self._rebuild_chat_with_response, message, response)
            
        except Exception as e:
            self.call_from_thread(log.write, f"\n[red]Error: {str(e)}[/red]")
    
    def _rebuild_chat_with_response(self, user_msg: str, ai_response: str) -> None:
        """Rebuild chat log with the new response"""
        log = self.query_one("#chat-log", RichLog)
        self._add_welcome_message()
        # Note: In a real app, you'd maintain a message history and rebuild
        self._add_message(user_msg, is_user=True)
        self._add_message(ai_response, is_user=False)
    
    # ========== Actions ==========
    
    def action_command_palette(self) -> None:
        commands = [
            {"id": "model", "name": "Select Model", "desc": "Change the AI model"},
            {"id": "provider", "name": "Select Provider", "desc": "Switch AI provider"},
            {"id": "mode", "name": "Select Mode", "desc": "Auto/Safe/Normal"},
            {"id": "clear", "name": "Clear Chat", "desc": "Clear conversation"},
            {"id": "status", "name": "Show Status", "desc": "Display current status"},
            {"id": "help", "name": "Help", "desc": "Show help"},
            {"id": "quit", "name": "Quit", "desc": "Exit ARIA"},
        ]
        self.push_screen(CommandPalette(commands), self._on_command_palette_dismiss)
    
    def _on_command_palette_dismiss(self, result: str | None) -> None:
        if result:
            if result == "model":
                self.action_select_model()
            elif result == "provider":
                self.action_select_provider()
            elif result == "mode":
                self.action_select_mode()
            elif result == "clear":
                self.action_clear_chat()
            elif result == "status":
                self._show_status()
            elif result == "help":
                self._show_help()
            elif result == "quit":
                self.exit()
    
    def action_select_model(self) -> None:
        models = self.llm.get_available_models()
        if not models:
            models = PROVIDER_MODELS.get(self.llm.provider_name, [])
        
        self.push_screen(
            ModelSelector(self.llm.provider_name, models, self.llm.model),
            self._on_model_selected
        )
    
    def _on_model_selected(self, result: str | None) -> None:
        if result:
            self.llm.switch_model(result)
            self._update_status_bar()
            self._add_system_message(f"Model changed to {result}")
    
    def action_select_provider(self) -> None:
        providers = self.llm.get_available_providers()
        self.push_screen(
            ProviderSelector(providers, self.llm.provider_name),
            self._on_provider_selected
        )
    
    def _on_provider_selected(self, result: str | None) -> None:
        if result and result != self.llm.provider_name:
            try:
                self.llm.switch_provider(result)
                self._update_status_bar()
                self._add_system_message(f"Switched to {result} ({self.llm.model})")
            except Exception as e:
                self._add_system_message(f"Error: {str(e)}")
    
    def action_select_mode(self) -> None:
        self.push_screen(
            ModeSelector(self.operation_mode.value),
            self._on_mode_selected
        )
    
    def _on_mode_selected(self, result: str | None) -> None:
        if result:
            self._set_mode(result)
    
    def action_clear_chat(self) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.clear()
        self.llm.clear_history()
        self._add_welcome_message()
        self._add_system_message("Chat cleared")
    
    def action_toggle_sidebar(self) -> None:
        sidebar = self.query_one("#sidebar")
        sidebar.display = not sidebar.display
    
    def action_focus_input(self) -> None:
        self.query_one("#chat-input", Input).focus()


def main():
    app = AriaTUI()
    app.run()


if __name__ == "__main__":
    main()
