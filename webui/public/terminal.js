// ===============================================
// ARIA - Terminal Module
// Extracted from app.js - Terminal functionality
// ===============================================

class TerminalModule {
  constructor(app) {
    this.app = app;
    this.terminal = null;
    this.fitAddon = null;
    this.ws = null;
    this.collapsed = false;
  }

  init() {
    const terminalContainer = document.getElementById('terminal');
    if (!terminalContainer || typeof Terminal === 'undefined') return;

    // Initialize xterm.js
    this.terminal = new Terminal({
      theme: this.getTheme('dark'),
      fontSize: 14,
      fontFamily: '"JetBrains Mono", "Fira Code", monospace',
      cursorBlink: true,
      allowProposedApi: true,
      scrollback: 5000
    });

    this.fitAddon = new FitAddon.FitAddon();
    this.terminal.loadAddon(this.fitAddon);

    this.terminal.open(terminalContainer);
    this.fitAddon.fit();

    // Connect to WebSocket for terminal I/O
    this.connectWebSocket();

    // Handle window resize
    window.addEventListener('resize', () => {
      if (this.fitAddon && !this.collapsed) {
        this.fitAddon.fit();
      }
    });

    // Terminal toggle button
    document.getElementById('terminalToggle')?.addEventListener('click', () => {
      this.toggle();
    });

    // Terminal header buttons
    document.getElementById('terminalMinimize')?.addEventListener('click', () => {
      this.toggle();
    });

    document.getElementById('terminalMaximize')?.addEventListener('click', () => {
      this.maximize();
    });

    document.getElementById('terminalClose')?.addEventListener('click', () => {
      this.hide();
    });

    // Initial write
    this.terminal.writeln('\x1b[1;35mARIA Terminal\x1b[0m - Ready');
    this.terminal.writeln('');
  }

  connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/terminal`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('[Terminal] WebSocket connected');
        this.terminal.writeln('\x1b[32m● Connected to shell\x1b[0m');
        this.terminal.writeln('');
      };

      this.ws.onmessage = (event) => {
        this.terminal.write(event.data);
      };

      this.ws.onerror = (error) => {
        console.error('[Terminal] WebSocket error:', error);
        this.terminal.writeln('\x1b[31m✗ Connection error\x1b[0m');
      };

      this.ws.onclose = () => {
        console.log('[Terminal] WebSocket closed');
        this.terminal.writeln('\x1b[33m○ Disconnected\x1b[0m');
        
        // Attempt reconnect after delay
        setTimeout(() => this.connectWebSocket(), 3000);
      };

      // Send terminal input to WebSocket
      this.terminal.onData((data) => {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
          this.ws.send(data);
        }
      });

    } catch (error) {
      console.error('[Terminal] Failed to connect:', error);
      this.terminal.writeln('\x1b[31m✗ Failed to connect to shell\x1b[0m');
    }
  }

  getTheme(theme) {
    const themes = {
      dark: {
        background: '#0a0b0f',
        foreground: '#f1f5f9',
        cursor: '#7c3aed',
        cursorAccent: '#0a0b0f',
        selectionBackground: 'rgba(124, 58, 237, 0.3)',
        black: '#1a1d24',
        red: '#ef4444',
        green: '#10b981',
        yellow: '#f59e0b',
        blue: '#3b82f6',
        magenta: '#a855f7',
        cyan: '#06b6d4',
        white: '#f1f5f9',
      },
      light: {
        background: '#f8fafc',
        foreground: '#0f172a',
        cursor: '#7c3aed',
        cursorAccent: '#f8fafc',
        selectionBackground: 'rgba(124, 58, 237, 0.2)',
        black: '#0f172a',
        red: '#dc2626',
        green: '#059669',
        yellow: '#d97706',
        blue: '#2563eb',
        magenta: '#9333ea',
        cyan: '#0891b2',
        white: '#f1f5f9',
      },
      midnight: {
        background: '#020617',
        foreground: '#e2e8f0',
        cursor: '#3b82f6',
        selectionBackground: 'rgba(59, 130, 246, 0.3)',
      },
      aurora: {
        background: '#0d1117',
        foreground: '#e6edf3',
        cursor: '#58a6ff',
        selectionBackground: 'rgba(88, 166, 255, 0.3)',
      }
    };

    return themes[theme] || themes.dark;
  }

  setTheme(theme) {
    if (this.terminal) {
      this.terminal.options.theme = this.getTheme(theme);
    }
  }

  toggle() {
    const container = document.getElementById('terminalContainer');
    if (!container) return;

    this.collapsed = !this.collapsed;
    container.classList.toggle('collapsed', this.collapsed);

    if (!this.collapsed && this.fitAddon) {
      setTimeout(() => this.fitAddon.fit(), 100);
    }
  }

  maximize() {
    const container = document.getElementById('terminalContainer');
    if (!container) return;

    container.classList.toggle('maximized');
    this.collapsed = false;

    if (this.fitAddon) {
      setTimeout(() => this.fitAddon.fit(), 100);
    }
  }

  hide() {
    const container = document.getElementById('terminalContainer');
    if (container) {
      container.style.display = 'none';
    }
  }

  show() {
    const container = document.getElementById('terminalContainer');
    if (container) {
      container.style.display = '';
      this.collapsed = false;
      if (this.fitAddon) {
        setTimeout(() => this.fitAddon.fit(), 100);
      }
    }
  }

  write(text) {
    if (this.terminal) {
      this.terminal.write(text);
    }
  }

  writeln(text) {
    if (this.terminal) {
      this.terminal.writeln(text);
    }
  }

  clear() {
    if (this.terminal) {
      this.terminal.clear();
    }
  }

  focus() {
    if (this.terminal) {
      this.terminal.focus();
    }
  }

  // Run a command programmatically
  runCommand(command) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(command + '\r');
    }
  }
}

// Export for use in main app
if (typeof module !== 'undefined' && module.exports) {
  module.exports = TerminalModule;
} else {
  window.TerminalModule = TerminalModule;
}
