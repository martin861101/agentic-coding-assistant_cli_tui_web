// ===============================================
// ARIA - Editor Module
// Extracted from app.js - Editor functionality
// ===============================================

class EditorModule {
  constructor(app) {
    this.app = app;
    this.undoStack = app.undoStack;
    this.autoSaveEnabled = true;
    this.autoSaveDelay = 2000;
    this.autoSaveTimeout = null;
    this.hasUnsavedChanges = false;
    this.foldedRegions = new Set();
  }

  init() {
    const editor = document.getElementById('codeEditor');
    if (!editor) return;

    this.undoStack.reset({
      value: editor.value,
      selectionStart: 0,
      selectionEnd: 0
    });

    let highlightTimeout;
    const debouncedHighlight = () => {
      clearTimeout(highlightTimeout);
      highlightTimeout = setTimeout(() => {
        this.updateSyntaxHighlighting(editor.value);
        this.undoStack.push({
          value: editor.value,
          selectionStart: editor.selectionStart,
          selectionEnd: editor.selectionEnd
        });
      }, 300);
    };

    const immediateHighlight = () => {
      this.updateSyntaxHighlighting(editor.value);
    };

    editor.addEventListener('input', () => {
      this.updateLineNumbers();
      this.updateCursorPosition();
      immediateHighlight();
      debouncedHighlight();
      this.markUnsaved(true);

      if (this.autoSaveEnabled && editor.dataset.path) {
        clearTimeout(this.autoSaveTimeout);
        this.autoSaveTimeout = setTimeout(() => this.autoSave(), this.autoSaveDelay);
      }
    });

    editor.addEventListener('scroll', () => {
      const lineNumbers = document.getElementById('lineNumbers');
      const highlightPre = document.getElementById('codeHighlight');
      if (lineNumbers) lineNumbers.scrollTop = editor.scrollTop;
      if (highlightPre) {
        highlightPre.scrollTop = editor.scrollTop;
        highlightPre.scrollLeft = editor.scrollLeft;
      }
      this.updateMinimap(editor.value);
    });

    editor.addEventListener('keyup', () => this.updateCursorPosition());
    editor.addEventListener('click', () => this.updateCursorPosition());
    this.initKeyboardShortcuts(editor, immediateHighlight);
  }

  initKeyboardShortcuts(editor, immediateHighlight) {
    editor.addEventListener('keydown', (e) => {
      // Save: Ctrl+S
      if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        this.saveFile();
      }

      // Undo: Ctrl+Z
      if (e.ctrlKey && e.key === 'z') {
        e.preventDefault();
        const state = this.undoStack.undo();
        if (state) {
          editor.value = state.value;
          editor.selectionStart = state.selectionStart;
          editor.selectionEnd = state.selectionEnd;
          this.updateLineNumbers();
          immediateHighlight();
        }
      }

      // Redo: Ctrl+Y or Ctrl+Shift+Z
      if ((e.ctrlKey && e.key === 'y') || (e.ctrlKey && e.shiftKey && e.key === 'Z')) {
        e.preventDefault();
        const state = this.undoStack.redo();
        if (state) {
          editor.value = state.value;
          editor.selectionStart = state.selectionStart;
          editor.selectionEnd = state.selectionEnd;
          this.updateLineNumbers();
          immediateHighlight();
        }
      }

      // Find: Ctrl+F
      if (e.ctrlKey && e.key === 'f') {
        e.preventDefault();
        this.app.showFindWidget();
      }

      // Tab indentation
      if (e.key === 'Tab') {
        e.preventDefault();
        this.handleTabKey(editor, immediateHighlight);
      }

      // Bracket auto-complete
      this.handleBracketAutoComplete(e, editor, immediateHighlight);
    });
  }

  handleTabKey(editor, immediateHighlight) {
    this.undoStack.push({
      value: editor.value,
      selectionStart: editor.selectionStart,
      selectionEnd: editor.selectionEnd
    });

    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    editor.value = editor.value.substring(0, start) + '  ' + editor.value.substring(end);
    editor.selectionStart = editor.selectionEnd = start + 2;
    this.updateLineNumbers();
    immediateHighlight();

    this.undoStack.push({
      value: editor.value,
      selectionStart: editor.selectionStart,
      selectionEnd: editor.selectionEnd
    });
  }

  handleBracketAutoComplete(e, editor, immediateHighlight) {
    const brackets = { '(': ')', '[': ']', '{': '}', '"': '"', "'": "'", '`': '`' };
    if (!brackets[e.key]) return;

    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const selected = editor.value.substring(start, end);
    const nextChar = editor.value.charAt(end);

    if (!selected && /\S/.test(nextChar) && !brackets[nextChar] && 
        nextChar !== ')' && nextChar !== ']' && nextChar !== '}') {
      return;
    }

    e.preventDefault();

    this.undoStack.push({
      value: editor.value,
      selectionStart: editor.selectionStart,
      selectionEnd: editor.selectionEnd
    });

    editor.value = editor.value.substring(0, start) + e.key + selected + brackets[e.key] + editor.value.substring(end);
    editor.selectionStart = start + 1;
    editor.selectionEnd = end + 1;

    this.updateLineNumbers();
    immediateHighlight();

    this.undoStack.push({
      value: editor.value,
      selectionStart: editor.selectionStart,
      selectionEnd: editor.selectionEnd
    });
  }

  updateLineNumbers() {
    const editor = document.getElementById('codeEditor');
    const lineNumbers = document.getElementById('lineNumbers');
    if (!editor || !lineNumbers) return;

    const lines = editor.value.split('\n');
    const foldableLines = this.detectFoldableRegions(lines);

    lineNumbers.innerHTML = lines.map((_, i) => {
      const lineNum = i + 1;
      const isFoldable = foldableLines.has(i);
      const isFolded = this.foldedRegions.has(i);

      let foldIcon = '';
      if (isFoldable) {
        foldIcon = `<span class="fold-marker ${isFolded ? 'folded' : ''}" data-line="${i}">${isFolded ? '▶' : '▼'}</span>`;
      }

      return `<div class="line-num ${isFoldable ? 'foldable' : ''}">${foldIcon}<span class="num">${lineNum}</span></div>`;
    }).join('');

    this.updateMinimap(editor.value);
  }

  updateCursorPosition() {
    const editor = document.getElementById('codeEditor');
    if (!editor) return;

    const pos = editor.selectionStart;
    const text = editor.value.substring(0, pos);
    const lines = text.split('\n');
    const line = lines.length;
    const col = lines[lines.length - 1].length + 1;

    const posEl = document.getElementById('cursorPosition');
    if (posEl) posEl.textContent = `Ln ${line}, Col ${col}`;

    const selectionInfo = document.getElementById('selectionInfo');
    if (selectionInfo) {
      const start = editor.selectionStart;
      const end = editor.selectionEnd;
      if (start !== end) {
        const selected = editor.value.substring(start, end);
        selectionInfo.textContent = `(${selected.length} selected)`;
      } else {
        selectionInfo.textContent = '';
      }
    }
  }

  updateSyntaxHighlighting(content, path) {
    const highlightCode = document.getElementById('highlightCode');
    const highlightPre = document.getElementById('codeHighlight');
    const editor = document.getElementById('codeEditor');
    if (!highlightCode || !highlightPre) return;

    const lang = this.app.getPrismLanguage(path || editor?.dataset?.path || '');
    highlightCode.className = `language-${lang}`;

    const escapedContent = this.escapeHtml(content || editor?.value || '');
    highlightCode.innerHTML = escapedContent;

    if (window.Prism) {
      Prism.highlightElement(highlightCode);
    }

    if (editor && highlightPre) {
      highlightPre.scrollTop = editor.scrollTop;
      highlightPre.scrollLeft = editor.scrollLeft;
    }

    this.updateCodeLens(content || editor?.value || '', path || editor?.dataset?.path);
  }

  updateMinimap(content) {
    const canvas = document.getElementById('minimapCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const minimapContainer = document.getElementById('minimap');
    if (!minimapContainer) return;

    const width = minimapContainer.clientWidth;
    const height = minimapContainer.clientHeight;
    canvas.width = width * window.devicePixelRatio;
    canvas.height = height * window.devicePixelRatio;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    ctx.clearRect(0, 0, width, height);

    const lines = (content || '').split('\n');
    const lineHeight = 2;
    const charWidth = 0.5;
    const padding = 4;

    lines.forEach((line, i) => {
      const y = i * lineHeight;
      if (y > height) return;

      let color = 'rgba(148, 163, 184, 0.3)';
      const trimmed = line.trim();
      
      if (trimmed.startsWith('//') || trimmed.startsWith('#') || trimmed.startsWith('/*')) {
        color = 'rgba(106, 115, 125, 0.4)';
      } else if (trimmed.match(/^(function|const|let|var|class|import|export|def|async|await)/)) {
        color = 'rgba(124, 58, 237, 0.5)';
      } else if (trimmed.match(/^(if|else|for|while|return|try|catch|switch|case)/)) {
        color = 'rgba(168, 85, 247, 0.5)';
      } else if (trimmed.includes('=>') || trimmed.includes('function')) {
        color = 'rgba(6, 182, 212, 0.5)';
      } else if (trimmed.match(/["'`]/)) {
        color = 'rgba(16, 185, 129, 0.5)';
      }

      const lineWidth = Math.min(line.length * charWidth, width - padding * 2);
      if (lineWidth > 0) {
        ctx.fillStyle = color;
        ctx.fillRect(padding, y, lineWidth, lineHeight - 0.5);
      }
    });

    // Draw viewport indicator
    const editor = document.getElementById('codeEditor');
    if (editor) {
      const totalLines = lines.length;
      const visibleLines = Math.floor(editor.clientHeight / 21);
      const scrollTop = editor.scrollTop;
      const scrollLine = Math.floor(scrollTop / 21);

      const viewportTop = (scrollLine / totalLines) * height;
      const viewportHeight = Math.max((visibleLines / totalLines) * height, 20);

      ctx.fillStyle = 'rgba(124, 58, 237, 0.15)';
      ctx.fillRect(0, viewportTop, width, viewportHeight);
      ctx.strokeStyle = 'rgba(124, 58, 237, 0.4)';
      ctx.lineWidth = 1;
      ctx.strokeRect(0, viewportTop, width, viewportHeight);
    }
  }

  updateCodeLens(content, path) {
    const container = document.getElementById('codeLensContainer');
    if (!container) return;

    container.innerHTML = '';
    if (!content || !path) return;

    const lines = content.split('\n');
    const ext = path.split('.').pop().toLowerCase();
    if (!['js', 'ts', 'jsx', 'tsx'].includes(ext)) return;

    const lensItems = [];

    lines.forEach((line, i) => {
      const funcMatch = line.match(/^(\s*)(async\s+)?function\s+(\w+)/);
      const arrowMatch = line.match(/^(\s*)(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(/);
      const classMatch = line.match(/^(\s*)class\s+(\w+)/);

      if (funcMatch || arrowMatch) {
        const name = funcMatch ? funcMatch[3] : arrowMatch[2];
        lensItems.push({
          line: i,
          type: 'function',
          name,
          suggestions: ['AI: Explain', 'AI: Optimize', 'Generate Tests']
        });
      }

      if (classMatch) {
        lensItems.push({
          line: i,
          type: 'class',
          name: classMatch[2],
          suggestions: ['AI: Document', 'AI: Review']
        });
      }
    });

    lensItems.slice(0, 10).forEach(item => {
      const lens = document.createElement('div');
      lens.className = 'code-lens-item';
      lens.style.top = `${item.line * 21}px`;
      lens.innerHTML = item.suggestions.map(s =>
        `<span class="lens-action" data-action="${s}" data-line="${item.line}" data-name="${item.name}">${s}</span>`
      ).join(' | ');

      lens.querySelectorAll('.lens-action').forEach(action => {
        action.addEventListener('click', (e) => {
          e.stopPropagation();
          this.handleCodeLensAction(action.dataset.action, action.dataset.name, parseInt(action.dataset.line));
        });
      });

      container.appendChild(lens);
    });
  }

  handleCodeLensAction(action, name, line) {
    const editor = document.getElementById('codeEditor');
    if (!editor) return;

    const lines = editor.value.split('\n');
    let startLine = line;
    let endLine = line;
    let braceCount = 0;
    let started = false;

    for (let i = line; i < lines.length; i++) {
      const lineContent = lines[i];
      for (const char of lineContent) {
        if (char === '{') { braceCount++; started = true; }
        if (char === '}') braceCount--;
      }
      endLine = i;
      if (started && braceCount === 0) break;
    }

    const codeSnippet = lines.slice(startLine, endLine + 1).join('\n');

    this.app.showAISidebar();
    const aiInput = document.getElementById('aiInput');

    const prompts = {
      'Explain': `Explain this function "${name}":\n\`\`\`\n${codeSnippet}\n\`\`\``,
      'Optimize': `Suggest optimizations for this function "${name}":\n\`\`\`\n${codeSnippet}\n\`\`\``,
      'Tests': `Generate unit tests for this function "${name}":\n\`\`\`\n${codeSnippet}\n\`\`\``,
      'Document': `Generate documentation for "${name}":\n\`\`\`\n${codeSnippet}\n\`\`\``,
      'Review': `Review this code for issues:\n\`\`\`\n${codeSnippet}\n\`\`\``
    };

    for (const [key, prompt] of Object.entries(prompts)) {
      if (action.includes(key)) {
        aiInput.value = prompt;
        break;
      }
    }

    aiInput.focus();
  }

  detectFoldableRegions(lines) {
    const foldableLines = new Set();
    
    const foldStartPatterns = [
      /^\s*(function|async\s+function)\s+\w+\s*\([^)]*\)\s*\{?\s*$/,
      /^\s*(const|let|var)\s+\w+\s*=\s*(async\s+)?\([^)]*\)\s*=>\s*\{?\s*$/,
      /^\s*class\s+\w+/,
      /^\s*(if|else\s+if|else|for|while|switch|try|catch|finally)\s*\(?/,
      /\{\s*$/,
      /\[\s*$/,
    ];

    lines.forEach((line, i) => {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('//')) return;

      const openBrackets = (line.match(/\{/g) || []).length;
      const closeBrackets = (line.match(/\}/g) || []).length;
      
      if (openBrackets - closeBrackets > 0) {
        foldableLines.add(i);
      }

      if (foldStartPatterns.some(pattern => pattern.test(line))) {
        if (i < lines.length - 1 && !line.includes('}')) {
          foldableLines.add(i);
        }
      }
    });

    return foldableLines;
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  markUnsaved(unsaved) {
    this.hasUnsavedChanges = unsaved;
    const editor = document.getElementById('codeEditor');
    const path = editor?.dataset.path;

    if (path) {
      const tab = document.querySelector(`.tab-item[data-path="${path}"]`);
      if (tab) tab.classList.toggle('unsaved', unsaved);
    }
  }

  async autoSave() {
    const editor = document.getElementById('codeEditor');
    const path = editor?.dataset.path;
    if (!path || !this.hasUnsavedChanges) return;

    try {
      await fetch('/api/file', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path, content: editor.value })
      });

      this.markUnsaved(false);
      const status = document.getElementById('codeLensStatus');
      if (status) {
        status.innerHTML = '<span class="ai-dot"></span> Auto-saved';
        setTimeout(() => {
          status.innerHTML = '<span class="ai-dot"></span> AI Ready';
        }, 2000);
      }
    } catch (error) {
      console.error('Auto-save failed:', error);
    }
  }

  async saveFile() {
    const editor = document.getElementById('codeEditor');
    const path = editor?.dataset.path;

    if (!path) {
      this.app.showToast('No file to save', 'warning');
      return;
    }

    try {
      await fetch('/api/file', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path, content: editor.value })
      });

      this.markUnsaved(false);
      this.app.showToast('File saved', 'success');

      if (window.AriaMemory) {
        window.AriaMemory.trackFileEdit(path, { type: 'save' });
      }
    } catch (error) {
      this.app.showToast('Failed to save file', 'error');
    }
  }

  async openFile(path) {
    try {
      const response = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
      const data = await response.json();

      this.app.showEditorTab(data.name, path);

      const editor = document.getElementById('codeEditor');
      if (editor) {
        editor.value = data.content;
        editor.dataset.path = path;
      }

      const lang = this.app.getLanguage(path);
      const langEl = document.getElementById('fileLanguage');
      if (langEl) langEl.textContent = lang;

      this.updateLineNumbers();
      this.updateCursorPosition();
      this.updateSyntaxHighlighting(data.content, path);

      if (window.AriaMemory) {
        window.AriaMemory.trackFileOpen(path);
        window.AriaMemory.setCurrentContext({ currentFile: path });
      }
    } catch (error) {
      this.app.showToast('Failed to open file', 'error');
    }
  }
}

// Export for use in main app
if (typeof module !== 'undefined' && module.exports) {
  module.exports = EditorModule;
} else {
  window.EditorModule = EditorModule;
}
