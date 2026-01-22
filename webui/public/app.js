// ===============================================
// ARIA - Synthetic Intelligence IDE
// Main Application v2.0
// ===============================================

class UndoStack {
  constructor(limit = 100) {
    this.stack = [];
    this.position = -1;
    this.limit = limit;
  }

  push(state) {
    // If we are in the middle of the stack, discard the future
    if (this.position < this.stack.length - 1) {
      this.stack = this.stack.slice(0, this.position + 1);
    }
    
    this.stack.push(state);
    if (this.stack.length > this.limit) {
      this.stack.shift();
    } else {
      this.position++;
    }
  }

  undo() {
    if (this.canUndo()) {
      this.position--;
      return this.stack[this.position];
    }
    return null;
  }

  redo() {
    if (this.canRedo()) {
      this.position++;
      return this.stack[this.position];
    }
    return null;
  }

  canUndo() {
    return this.position > 0;
  }

  canRedo() {
    return this.position < this.stack.length - 1;
  }
  
  reset(initialState) {
    this.stack = [initialState];
    this.position = 0;
  }
}

class ARIAUI {
  constructor() {
    // Core state
    this.terminal = null;
    this.fitAddon = null;
    this.ws = null;
    this.currentPath = '';
    this.selectedFile = null;
    this.openFiles = new Map();
    this.contextMenuTarget = null;
    this.isDragging = false;
    this.clipboardFile = null;
    this.currentAIAgent = null;
    this.undoStack = new UndoStack();
    
    // UI State
    this.currentView = 'explorer';
    this.aiSidebarVisible = false;
    this.commandPaletteVisible = false;
    this.terminalCollapsed = false;
    this.recentFilesVisible = false;
    this.findWidgetVisible = false;
    this.splitEditorActive = false;
    this.activePane = 1; // 1 = primary, 2 = secondary
    this.pane2File = null; // File open in secondary pane
    
    // Command Palette
    this.commands = [];
    this.commandIndex = 0;
    
    // Search State
    this.searchState = {
      query: '',
      matches: [],
      currentMatchIndex: -1,
      options: {
        caseSensitive: false,
        wholeWord: false,
        useRegex: false
      }
    };
    
    // Code Folding State
    this.foldedRegions = new Set(); // Set of line numbers where folds start
    
    // Initialize
    this.init();
  }
  
  async init() {
    console.log('[ARIA] Initializing Synthetic Intelligence IDE...');
    
    // Load system info first
    await this.loadSystemInfo();
    
    // Initialize all modules
    this.initTheme();
    this.initNeuralBackground();
    this.initHeader();
    this.initActivityBar();
    this.initSidebar();
    this.initResizer();
    this.initEditor();
    this.initSplitEditor();
    this.initCodeFolding();
    this.initBracketMatching();
    this.initTerminal();
    this.initCommandPalette();
    this.initAISidebar();
    this.initContextMenu();
    this.initModals();
    this.initFindWidget();
    this.initKeyboardShortcuts();
    this.initStatusBar();
    
    // Start services
    this.startSystemMonitor();
    this.loadAgents();
    this.loadWorkflows();
    this.initDragAndDrop();
    this.initSessionPersistence();
    
    // Track session start
    if (window.AriaMemory) {
      window.AriaMemory.setCurrentContext({
        startTime: Date.now(),
        currentFile: null,
        currentView: 'welcome'
      });
    }
    
    console.log('[ARIA] Initialization complete');
    this.showToast('ARIA ready', 'success');
  }
  
  // ===============================================
  // Theme Management
  // ===============================================
  
  initTheme() {
    const savedTheme = localStorage.getItem('aria_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    document.getElementById('themeToggle').addEventListener('click', () => {
      this.toggleTheme();
    });
    
    // Theme setting dropdown
    const themeSetting = document.getElementById('themeSetting');
    if (themeSetting) {
      themeSetting.value = savedTheme;
      themeSetting.addEventListener('change', (e) => {
        this.setTheme(e.target.value);
      });
    }
  }
  
  toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    this.setTheme(next);
  }
  
  setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('aria_theme', theme);
    
    if (this.terminal) {
      this.updateTerminalTheme(theme);
    }
    
    const themeSetting = document.getElementById('themeSetting');
    if (themeSetting) themeSetting.value = theme;
    
    if (window.AriaMemory) {
      window.AriaMemory.setPreference('theme', theme);
    }
  }
  
  updateTerminalTheme(theme) {
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
    
    this.terminal.options.theme = themes[theme] || themes.dark;
  }
  
  // ===============================================
  // Neural Background Animation
  // ===============================================
  
  initNeuralBackground() {
    const canvas = document.getElementById('neuralCanvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let animationFrame;
    let particles = [];
    
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    
    const createParticles = () => {
      particles = [];
      const count = Math.floor((canvas.width * canvas.height) / 15000);
      for (let i = 0; i < count; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          radius: Math.random() * 2 + 1
        });
      }
    };
    
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Update and draw particles
      particles.forEach((p, i) => {
        p.x += p.vx;
        p.y += p.vy;
        
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
        
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(124, 58, 237, 0.3)';
        ctx.fill();
        
        // Draw connections
        particles.slice(i + 1).forEach(p2 => {
          const dx = p.x - p2.x;
          const dy = p.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          
          if (dist < 150) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(124, 58, 237, ${0.1 * (1 - dist / 150)})`;
            ctx.stroke();
          }
        });
      });
      
      animationFrame = requestAnimationFrame(animate);
    };
    
    resize();
    createParticles();
    animate();
    
    window.addEventListener('resize', () => {
      resize();
      createParticles();
    });
  }
  
  // ===============================================
  // Header
  // ===============================================
  
  initHeader() {
    // Logo click - show welcome
    document.getElementById('logoIcon')?.addEventListener('click', () => {
      this.showWelcomeTab();
    });
    
    // Command trigger
    document.getElementById('commandTrigger')?.addEventListener('click', () => {
      this.showCommandPalette();
    });
    
    // Header buttons
    document.getElementById('aiChatBtn')?.addEventListener('click', () => {
      this.toggleAISidebar();
    });
    
    document.getElementById('insightsBtn')?.addEventListener('click', () => {
      this.toggleInsights();
    });
    
    document.getElementById('workflowBtn')?.addEventListener('click', () => {
      this.switchView('workflows');
    });
  }
  
  // ===============================================
  // Activity Bar
  // ===============================================
  
  initActivityBar() {
    document.querySelectorAll('.activity-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const view = btn.dataset.view;
        if (view) {
          this.switchView(view);
        }
      });
    });
  }
  
  switchView(view) {
    const isMobile = window.innerWidth <= 768;
    const sidebar = document.getElementById('sidebar');
    
    // Mobile logic: Toggle sidebar if clicking same view, or open if different
    if (isMobile) {
      if (this.currentView === view && sidebar.classList.contains('visible')) {
        sidebar.classList.remove('visible');
        // Deselect activity button when closing
        document.querySelectorAll('.activity-btn').forEach(btn => btn.classList.remove('active'));
        return;
      } else {
        sidebar.classList.add('visible');
      }
    }

    // Update activity bar
    document.querySelectorAll('.activity-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.view === view);
    });
    
    // Update sidebar views
    document.querySelectorAll('.sidebar-view').forEach(v => {
      v.classList.toggle('active', v.id === `${view}View`);
    });
    
    this.currentView = view;
    
    // Load view-specific data
    switch (view) {
      case 'git':
        this.loadGitInfo();
        break;
      case 'docker':
        this.loadDockerInfo();
        break;
      case 'system':
        this.loadSystemDetails();
        break;
    }
  }
  
  // ===============================================
  // Sidebar
  // ===============================================
  
  initSidebar() {
    // Mobile sidebar close button
    document.getElementById('sidebarMobileClose')?.addEventListener('click', () => {
      document.getElementById('sidebar').classList.remove('visible');
      document.querySelectorAll('.activity-btn').forEach(btn => btn.classList.remove('active'));
    });

    // File explorer actions
    document.getElementById('newFileBtn')?.addEventListener('click', () => {
      this.showInputModal('New File', 'Enter filename:', (name) => this.createFile(name));
    });
    
    document.getElementById('newFolderBtn')?.addEventListener('click', () => {
      this.showInputModal('New Folder', 'Enter folder name:', (name) => this.createFolder(name));
    });
    
    document.getElementById('refreshBtn')?.addEventListener('click', () => {
      this.loadDirectory(this.currentPath);
    });
    
    // Collapse all button
    document.getElementById('collapseAllBtn')?.addEventListener('click', () => {
      document.querySelectorAll('.file-item.directory.expanded').forEach(dir => {
        dir.classList.remove('expanded');
      });
    });
    
    // Git refresh button
    document.getElementById('gitRefreshBtn')?.addEventListener('click', () => {
      this.loadGitInfo();
      this.showToast('Git status refreshed', 'info');
    });
    
    // Git commit button
    document.getElementById('commitBtn')?.addEventListener('click', () => {
      this.gitCommit();
    });
    
    // Git stage all button
    document.getElementById('stageAllBtn')?.addEventListener('click', async () => {
      try {
        await this.runCommand('git add .');
        this.showToast('All changes staged', 'success');
        this.loadGitInfo();
      } catch (e) {
        this.showToast('Failed to stage changes', 'error');
      }
    });
    
    // Commit message Ctrl+Enter shortcut
    document.getElementById('commitMessage')?.addEventListener('keydown', (e) => {
      if (e.ctrlKey && e.key === 'Enter') {
        e.preventDefault();
        this.gitCommit();
      }
    });
    
    // Docker refresh button
    document.getElementById('dockerRefreshBtn')?.addEventListener('click', () => {
      this.loadDockerInfo();
      this.showToast('Docker status refreshed', 'info');
    });
    
    // Global search input
    document.getElementById('globalSearchInput')?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        this.performSearch();
      }
    });
    
    // Search type toggle
    document.getElementById('caseSensitive')?.addEventListener('change', () => this.performSearch());
    document.getElementById('wholeWord')?.addEventListener('change', () => this.performSearch());
    document.getElementById('useRegex')?.addEventListener('change', () => this.performSearch());
    
    // Load initial directory
    this.loadDirectory(this.currentPath);
  }
  
  async performSearch() {
    const query = document.getElementById('globalSearchInput')?.value.trim();
    if (!query) return;
    
    const container = document.getElementById('searchResultsContainer');
    container.innerHTML = '<div class="loading-spinner"><div class="spinner"></div><span>Searching...</span></div>';
    
    try {
      const caseSensitive = document.getElementById('caseSensitive')?.checked;
      const wholeWord = document.getElementById('wholeWord')?.checked;
      const useRegex = document.getElementById('useRegex')?.checked;
      
      const response = await fetch(`/api/search?query=${encodeURIComponent(query)}&path=${encodeURIComponent(this.currentPath)}&type=content`);
      const data = await response.json();
      
      if (data.results && data.results.length > 0) {
        container.innerHTML = `
          <div class="search-summary">${data.results.length} results found</div>
          <div class="search-results">
            ${data.results.map(result => `
              <div class="search-result-item" data-path="${result.path}">
                <div class="result-file">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14,2 14,8 20,8"/>
                  </svg>
                  <span class="result-filename">${result.name}</span>
                </div>
                <div class="result-path">${result.path}</div>
              </div>
            `).join('')}
          </div>
        `;
        
        // Add click handlers
        container.querySelectorAll('.search-result-item').forEach(item => {
          item.addEventListener('click', () => {
            this.openFile(item.dataset.path);
          });
        });
      } else {
        container.innerHTML = '<div class="search-placeholder">No results found</div>';
      }
      
      // Track search
      if (window.AriaMemory) {
        window.AriaMemory.trackSearch(query, 'content');
      }
    } catch (error) {
      container.innerHTML = '<div class="search-placeholder"><span style="color: var(--error);">Search failed</span></div>';
    }
  }
  
  async loadDirectory(path) {
    const fileTree = document.getElementById('fileTree');
    if (!fileTree) return;
    
    try {
      fileTree.innerHTML = '<div class="loading-spinner"><div class="spinner"></div><span>Loading files...</span></div>';
      
      const response = await fetch(`/api/files?path=${encodeURIComponent(path)}`);
      const data = await response.json();
      
      this.currentPath = data.path;
      this.updateBreadcrumb(data.path);
      
      fileTree.innerHTML = '';
      
      // Add parent directory
      if (data.parent !== data.path) {
        const parentItem = this.createFileItem({
          name: '..',
          path: data.parent,
          isDirectory: true
        });
        fileTree.appendChild(parentItem);
      }
      
      // Add files and directories
      data.files.forEach(file => {
        const item = this.createFileItem(file);
        fileTree.appendChild(item);
      });
      
      this.loadGitInfo();
      
    } catch (error) {
      console.error('Failed to load directory:', error);
      fileTree.innerHTML = '<div class="loading-spinner"><span style="color: var(--error);">Error loading files</span></div>';
    }
  }
  
  createFileItem(file) {
    const item = document.createElement('div');
    item.className = `file-item${file.isDirectory ? ' directory' : ''}`;
    item.dataset.path = file.path;
    
    const icon = this.getFileIcon(file);
    
    item.innerHTML = `
      ${file.isDirectory && file.name !== '..' ? '<span class="expand-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9,6 15,12 9,18"/></svg></span>' : ''}
      <span class="file-icon ${icon.class}">${icon.svg}</span>
      <span class="file-name">${file.name}</span>
    `;
    
    item.addEventListener('click', (e) => {
      e.stopPropagation();
      
      document.querySelectorAll('.file-item.selected').forEach(el => el.classList.remove('selected'));
      item.classList.add('selected');
      this.selectedFile = file;
      
      if (file.isDirectory) {
        this.loadDirectory(file.path);
      } else {
        this.openFile(file.path);
      }
    });
    
    item.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      this.contextMenuTarget = file;
      this.showContextMenu(e.clientX, e.clientY);
    });
    
    return item;
  }
  
  getFileIcon(file) {
    if (file.isDirectory) {
      // Special folder icons
      const folderIcons = {
        'node_modules': 'folder-node',
        '.git': 'folder-git',
        'src': 'folder-src',
        'public': 'folder-public',
        'dist': 'folder-dist',
        'build': 'folder-dist',
        'assets': 'folder-assets',
        'images': 'folder-images',
        'components': 'folder-components',
        'pages': 'folder-pages',
        'api': 'folder-api',
        'test': 'folder-test',
        'tests': 'folder-test',
        '__tests__': 'folder-test'
      };
      
      const folderClass = folderIcons[file.name] || 'folder';
      
      return {
        class: folderClass,
        svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M10 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/></svg>'
      };
    }
    
    const ext = file.name.split('.').pop().toLowerCase();
    const fileName = file.name.toLowerCase();
    
    // Special file icons
    const specialFiles = {
      'package.json': { class: 'npm', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="2" y="2" width="20" height="20" rx="2"/><path fill="#fff" d="M5 5h14v14H12V8H9v11H5z"/></svg>' },
      'package-lock.json': { class: 'npm', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="2" y="2" width="20" height="20" rx="2"/><path fill="#fff" d="M5 5h14v14H12V8H9v11H5z"/></svg>' },
      'tsconfig.json': { class: 'ts-config', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h18v18H3V3m10.71 13.47c.5.98 1.51 1.73 3.09 1.73 1.6 0 2.8-.83 2.8-2.36 0-1.41-.81-2.04-2.25-2.66z"/></svg>' },
      '.gitignore': { class: 'git', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.44 9.8 8.2 11.38.6.11.82-.26.82-.58v-2.03c-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.09-.75.08-.73.08-.73 1.21.08 1.84 1.24 1.84 1.24 1.07 1.84 2.81 1.31 3.5 1 .11-.78.42-1.31.76-1.61-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.12-.3-.54-1.52.12-3.18 0 0 1.01-.32 3.3 1.23.96-.27 1.98-.4 3-.4s2.04.14 3 .4c2.28-1.55 3.29-1.23 3.29-1.23.66 1.66.24 2.88.12 3.18.77.84 1.24 1.91 1.24 3.22 0 4.61-2.81 5.63-5.48 5.92.43.37.81 1.1.81 2.22v3.29c0 .32.21.69.82.57C20.56 21.8 24 17.3 24 12c0-6.63-5.37-12-12-12z"/></svg>' },
      'dockerfile': { class: 'docker', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M13 4h3v3h-3zM9 4h3v3H9zM5 4h3v3H5zM9 0h3v3H9zM22 9c-.5-.4-1.6-.6-2.4-.4-.2-1.4-1-2.6-2.1-3.4l-.4-.3-.3.4c-.4.6-.6 1.3-.6 2 0 .7.1 1.4.5 2-.7.4-2 .5-2.4.5H.3l-.1.5c-.2 1.5 0 3 .6 4.4.8 1.5 2 2.6 3.6 3.2 1.8.7 3.8.8 5.8.5 1.5-.2 3-.6 4.3-1.4 1.1-.7 2-1.5 2.8-2.6.7-.9 1.2-2 1.6-3.2h.1c1 0 1.6-.4 2-.8.3-.2.5-.6.6-.9l.1-.4-.4-.3z"/></svg>' },
      '.env': { class: 'env', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 6c1.4 0 2.8 1.1 2.8 2.5V11c.6 0 1.2.6 1.2 1.2v3.5c0 .7-.5 1.3-1.2 1.3H9.2c-.7 0-1.2-.6-1.2-1.2v-3.5c0-.7.5-1.3 1.2-1.3V9.5C9.2 8.1 10.6 7 12 7zm0 1.2c-.8 0-1.5.7-1.5 1.5V11h3V9.7c0-.8-.7-1.5-1.5-1.5z"/></svg>' },
      'readme.md': { class: 'readme', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L4 5v6.09c0 5.05 3.41 9.76 8 10.91 4.59-1.15 8-5.86 8-10.91V5l-8-3zm-1 15h2v2h-2v-2zm0-8h2v6h-2V9z"/></svg>' }
    };
    
    if (specialFiles[fileName]) {
      return specialFiles[fileName];
    }
    
    const icons = {
      // JavaScript/TypeScript
      js: { class: 'js', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h18v18H3V3m4.73 15.04c.4.85 1.19 1.55 2.54 1.55 1.5 0 2.53-.8 2.53-2.55v-5.78h-1.7V17c0 .86-.35 1.08-.9 1.08-.58 0-.82-.4-1.09-.87l-1.38.83z"/></svg>' },
      mjs: { class: 'js', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h18v18H3V3m4.73 15.04c.4.85 1.19 1.55 2.54 1.55 1.5 0 2.53-.8 2.53-2.55v-5.78h-1.7V17c0 .86-.35 1.08-.9 1.08-.58 0-.82-.4-1.09-.87l-1.38.83z"/></svg>' },
      ts: { class: 'ts', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h18v18H3V3m10.71 13.47c.5.98 1.51 1.73 3.09 1.73 1.6 0 2.8-.83 2.8-2.36 0-1.41-.81-2.04-2.25-2.66z"/></svg>' },
      jsx: { class: 'jsx', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="11.245" r="1.785"/><path d="m7.002 14.794-.395-.101c-2.934-.741-4.617-2.001-4.617-3.452 0-1.452 1.684-2.711 4.617-3.452l.395-.1.111.391a19.507 19.507 0 0 0 1.136 2.983l.085.178-.085.178c-.46.963-.841 1.961-1.136 2.985l-.111.39z"/></svg>' },
      tsx: { class: 'tsx', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="11.245" r="1.785"/><path d="m7.002 14.794-.395-.101c-2.934-.741-4.617-2.001-4.617-3.452 0-1.452 1.684-2.711 4.617-3.452l.395-.1.111.391a19.507 19.507 0 0 0 1.136 2.983l.085.178-.085.178c-.46.963-.841 1.961-1.136 2.985l-.111.39z"/></svg>' },
      
      // Python
      py: { class: 'py', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M9.585 11.692h4.328s2.432.039 2.432-2.35V5.391S16.714 3 11.936 3C7.362 3 7.647 4.983 7.647 4.983l.006 2.055h4.363v.617H5.92S3 7.283 3 11.692z"/></svg>' },
      
      // Go
      go: { class: 'go', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M1.811 10.231c-.047 0-.058-.023-.035-.059l.246-.315c.023-.035.081-.058.128-.058h4.172z"/></svg>' },
      
      // Rust
      rs: { class: 'rust', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>' },
      
      // Data formats
      json: { class: 'json', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5 3h2v2H5v5a2 2 0 0 1-2 2 2 2 0 0 1 2 2v5h2v2H5c-1.07-.27-2-.9-2-2v-4a2 2 0 0 0-2-2H0v-2h1a2 2 0 0 0 2-2V5a2 2 0 0 1 2-2z"/></svg>' },
      yaml: { class: 'yaml', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5 3h2v2H5v5a2 2 0 0 1-2 2 2 2 0 0 1 2 2v5h2v2H5c-1.07-.27-2-.9-2-2v-4a2 2 0 0 0-2-2H0v-2h1a2 2 0 0 0 2-2V5a2 2 0 0 1 2-2z"/></svg>' },
      yml: { class: 'yaml', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5 3h2v2H5v5a2 2 0 0 1-2 2 2 2 0 0 1 2 2v5h2v2H5c-1.07-.27-2-.9-2-2v-4a2 2 0 0 0-2-2H0v-2h1a2 2 0 0 0 2-2V5a2 2 0 0 1 2-2z"/></svg>' },
      toml: { class: 'toml', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5 3h2v2H5v5a2 2 0 0 1-2 2 2 2 0 0 1 2 2v5h2v2H5c-1.07-.27-2-.9-2-2v-4a2 2 0 0 0-2-2H0v-2h1a2 2 0 0 0 2-2V5a2 2 0 0 1 2-2z"/></svg>' },
      
      // Web
      md: { class: 'md', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.56 18H3.44A1.44 1.44 0 0 1 2 16.56V7.44A1.44 1.44 0 0 1 3.44 6h17.12A1.44 1.44 0 0 1 22 7.44v9.12A1.44 1.44 0 0 1 20.56 18z"/></svg>' },
      html: { class: 'html', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 17.56L16.07 16.43L16.62 10.33H9.38L9.2 8.3H16.8L17 6.31H7L7.56 12.32H14.45L14.22 14.9L12 15.5L9.78 14.9z"/></svg>' },
      htm: { class: 'html', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 17.56L16.07 16.43L16.62 10.33H9.38L9.2 8.3H16.8L17 6.31H7L7.56 12.32H14.45L14.22 14.9L12 15.5L9.78 14.9z"/></svg>' },
      css: { class: 'css', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5 3L4.35 6.34H17.94L17.5 8.5H3.92L3.26 11.83H16.85L16.09 15.64L10.61 17.45L5.86 15.64L6.19 14H2.85L2.06 18L9.91 21L18.96 18L20.16 11.97z"/></svg>' },
      scss: { class: 'scss', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5 3L4.35 6.34H17.94L17.5 8.5H3.92L3.26 11.83H16.85L16.09 15.64L10.61 17.45L5.86 15.64L6.19 14H2.85L2.06 18L9.91 21L18.96 18L20.16 11.97z"/></svg>' },
      less: { class: 'less', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5 3L4.35 6.34H17.94L17.5 8.5H3.92L3.26 11.83H16.85L16.09 15.64L10.61 17.45L5.86 15.64L6.19 14H2.85L2.06 18L9.91 21L18.96 18L20.16 11.97z"/></svg>' },
      svg: { class: 'svg', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5 3l-2 9h2l.5-2h3l.5 2h2l-2-9H5zm1.5 5l1-4 1 4h-2z"/></svg>' },
      
      // Shell
      sh: { class: 'shell', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5 3h14c1.1 0 2 .9 2 2v14c0 1.1-.9 2-2 2H5c-1.1 0-2-.9-2-2V5c0-1.1.9-2 2-2zm1 4l5 4-5 4v-2l3-2-3-2V7zm6 6h6v2h-6v-2z"/></svg>' },
      bash: { class: 'shell', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5 3h14c1.1 0 2 .9 2 2v14c0 1.1-.9 2-2 2H5c-1.1 0-2-.9-2-2V5c0-1.1.9-2 2-2zm1 4l5 4-5 4v-2l3-2-3-2V7zm6 6h6v2h-6v-2z"/></svg>' },
      zsh: { class: 'shell', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5 3h14c1.1 0 2 .9 2 2v14c0 1.1-.9 2-2 2H5c-1.1 0-2-.9-2-2V5c0-1.1.9-2 2-2zm1 4l5 4-5 4v-2l3-2-3-2V7zm6 6h6v2h-6v-2z"/></svg>' },
      
      // Images
      png: { class: 'image', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>' },
      jpg: { class: 'image', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>' },
      jpeg: { class: 'image', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>' },
      gif: { class: 'image', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>' },
      webp: { class: 'image', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>' },
      ico: { class: 'image', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>' },
      
      // Database
      sql: { class: 'sql', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v12c0 1.66 3.58 3 8 3s8-1.34 8-3V6"/><path d="M4 12c0 1.66 3.58 3 8 3s8-1.34 8-3"/></svg>' },
      
      // Documents
      pdf: { class: 'pdf', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm-1 7V3.5L18.5 9H13z"/></svg>' },
      txt: { class: 'txt', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/></svg>' },
      
      // Lock files
      lock: { class: 'lock', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 1C8.68 1 6 3.68 6 7v2H4c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V11c0-1.1-.9-2-2-2h-2V7c0-3.32-2.68-6-6-6zm0 2c2.21 0 4 1.79 4 4v2H8V7c0-2.21 1.79-4 4-4z"/></svg>' },
      
      // XML
      xml: { class: 'xml', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.89 3L14.85 3.4 11.11 21 9.15 20.6 12.89 3M19.59 12L16 8.41V5.58L22.42 12 16 18.41V15.58L19.59 12M1.58 12L8 5.58V8.41L4.41 12 8 15.58V18.41L1.58 12Z"/></svg>' },
      
      // Java
      java: { class: 'java', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8.851 18.56s-.917.534.653.714c1.902.218 2.874.187 4.969-.211 0 0 .552.346 1.321.646-4.699 2.013-10.633-.118-6.943-1.149"/></svg>' },
      
      // C/C++
      c: { class: 'c', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15h-2v-6H7v-2h2V7h2v2h2v2h-2v6z"/></svg>' },
      cpp: { class: 'cpp', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>' },
      h: { class: 'h', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15h-2v-6H7v-2h2V7h2v2h2v2h-2v6z"/></svg>' },
      hpp: { class: 'hpp', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>' }
    };
    
    return icons[ext] || {
      class: 'file',
      svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/></svg>'
    };
  }
  
  updateBreadcrumb(path) {
    const breadcrumb = document.getElementById('pathBreadcrumb');
    if (!breadcrumb) return;
    
    const home = '/home/dev';
    let displayPath = path;
    if (path.startsWith(home)) {
      displayPath = '~' + path.substring(home.length);
    }
    
    const segments = displayPath.split('/').filter(Boolean);
    breadcrumb.innerHTML = segments.map((seg, i) => 
      `<span class="breadcrumb-item">${seg}</span>${i < segments.length - 1 ? '<span class="breadcrumb-separator">/</span>' : ''}`
    ).join('');
  }
  
  // ===============================================
  // Editor
  // ===============================================
  
  initEditor() {
    const editor = document.getElementById('codeEditor');
    const lineNumbers = document.getElementById('lineNumbers');
    const highlightPre = document.getElementById('codeHighlight');
    
    if (!editor) return;
    
    // Auto-save configuration
    this.autoSaveEnabled = true;
    this.autoSaveDelay = 2000; // 2 seconds
    this.autoSaveTimeout = null;
    this.hasUnsavedChanges = false;
    
    // Undo/Redo State
    this.undoStack.reset({
      value: editor.value,
      selectionStart: 0,
      selectionEnd: 0
    });
    
    // Debounce helper for syntax highlighting and undo
    let highlightTimeout;
    const debouncedHighlight = () => {
      clearTimeout(highlightTimeout);
      highlightTimeout = setTimeout(() => {
        this.updateSyntaxHighlighting(editor.value);
        
        // Save state for undo
        this.undoStack.push({
          value: editor.value,
          selectionStart: editor.selectionStart,
          selectionEnd: editor.selectionEnd
        });
      }, 300); // Higher delay for undo state to avoid capturing every keystroke
    };
    
    // Immediate highlight for responsiveness
    const immediateHighlight = () => {
      this.updateSyntaxHighlighting(editor.value);
    };
    
    editor.addEventListener('input', () => {
      this.updateLineNumbers();
      this.updateCursorPosition();
      immediateHighlight();
      debouncedHighlight();
      
      // Mark as having unsaved changes
      this.markUnsaved(true);
      
      // Auto-save
      if (this.autoSaveEnabled && editor.dataset.path) {
        clearTimeout(this.autoSaveTimeout);
        this.autoSaveTimeout = setTimeout(() => {
          this.autoSave();
        }, this.autoSaveDelay);
      }
    });
    
    editor.addEventListener('scroll', () => {
      if (lineNumbers) {
        lineNumbers.scrollTop = editor.scrollTop;
      }
      if (highlightPre) {
        highlightPre.scrollTop = editor.scrollTop;
        highlightPre.scrollLeft = editor.scrollLeft;
      }
      // Update minimap viewport
      this.updateMinimap(editor.value);
    });
    
    editor.addEventListener('keyup', () => this.updateCursorPosition());
    editor.addEventListener('click', () => this.updateCursorPosition());
    
    editor.addEventListener('keydown', (e) => {
      // Save
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
        this.showFindWidget();
      }
      
      // Indentation
      if (e.key === 'Tab') {
        e.preventDefault();
        
        // Snapshot before change
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
        
        // Snapshot after change
        this.undoStack.push({
          value: editor.value,
          selectionStart: editor.selectionStart,
          selectionEnd: editor.selectionEnd
        });
      }
      
      // Bracket auto-complete
      const brackets = { '(': ')', '[': ']', '{': '}', '"': '"', "'": "'", '`': '`' };
      if (brackets[e.key]) {
        const start = editor.selectionStart;
        const end = editor.selectionEnd;
        const selected = editor.value.substring(start, end);
        
        // Only auto-close if selecting or single cursor (not typing over)
        // Simplified logic: always auto-close if selecting or at end of line/whitespace
        // For now, keep existing logic but add undo snapshot
        
        if (selected.length > 0 || true) { // Always try to auto-close for now, can refine
           // Check if we should actually insert (basic check)
           const nextChar = editor.value.charAt(end);
           if (!selected && /\S/.test(nextChar) && !brackets[nextChar] && nextChar !== ')' && nextChar !== ']' && nextChar !== '}') {
             // Don't auto-close if typing before non-whitespace/non-closing bracket
             return;
           }
           
           e.preventDefault();
           
           // Snapshot before
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
           
           // Snapshot after
           this.undoStack.push({
             value: editor.value,
             selectionStart: editor.selectionStart,
             selectionEnd: editor.selectionEnd
           });
        }
      }
    });
    
    // Welcome page cards
    document.getElementById('openFolderCard')?.addEventListener('click', () => {
      this.switchView('explorer');
    });
    
    document.getElementById('aiAssistCard')?.addEventListener('click', () => {
      this.toggleAISidebar();
    });
    
    document.getElementById('workflowsCard')?.addEventListener('click', () => {
      this.switchView('workflows');
    });
    
    document.getElementById('settingsCard')?.addEventListener('click', () => {
      this.switchView('settings');
    });
  }
  
  // ===============================================
  // Split Editor
  // ===============================================
  
  initSplitEditor() {
    const splitBtn = document.getElementById('splitEditorBtn');
    const closeSplitBtn = document.getElementById('closeSplitBtn');
    const resizer = document.getElementById('splitEditorResizer');
    const pane1 = document.getElementById('editorPane1');
    const pane2 = document.getElementById('editorPane2');
    const editor2 = document.getElementById('codeEditor2');
    
    if (!splitBtn || !pane2) return;
    
    // Toggle split view
    splitBtn.addEventListener('click', () => {
      this.toggleSplitEditor();
    });
    
    // Close split view
    closeSplitBtn?.addEventListener('click', () => {
      this.closeSplitEditor();
    });
    
    // Initialize secondary editor events
    if (editor2) {
      editor2.addEventListener('input', () => {
        this.updateLineNumbers2();
        this.updateCursorPosition2();
        this.updateSyntaxHighlighting2(editor2.value);
      });
      
      editor2.addEventListener('scroll', () => {
        const lineNumbers2 = document.getElementById('lineNumbers2');
        const highlightPre2 = document.getElementById('codeHighlight2');
        if (lineNumbers2) lineNumbers2.scrollTop = editor2.scrollTop;
        if (highlightPre2) {
          highlightPre2.scrollTop = editor2.scrollTop;
          highlightPre2.scrollLeft = editor2.scrollLeft;
        }
      });
      
      editor2.addEventListener('click', () => {
        this.setActivePane(2);
        this.updateCursorPosition2();
      });
      
      editor2.addEventListener('keydown', (e) => {
        // Save Ctrl+S for pane 2
        if (e.ctrlKey && e.key === 's') {
          e.preventDefault();
          this.saveFile2();
        }
      });
    }
    
    // Split resizer drag
    if (resizer) {
      this.initSplitResizer(resizer, pane1, pane2);
    }
    
    // Click on primary editor sets active pane
    const editor1 = document.getElementById('codeEditor');
    if (editor1) {
      editor1.addEventListener('click', () => {
        this.setActivePane(1);
      });
    }
  }
  
  toggleSplitEditor() {
    const pane2 = document.getElementById('editorPane2');
    const resizer = document.getElementById('splitEditorResizer');
    const splitBtn = document.getElementById('splitEditorBtn');
    
    if (!pane2) return;
    
    this.splitEditorActive = !this.splitEditorActive;
    
    if (this.splitEditorActive) {
      pane2.classList.add('visible');
      resizer?.classList.add('visible');
      splitBtn?.classList.add('active');
      
      // If we have a current file, offer to open it in pane 2 or show welcome
      const editor1 = document.getElementById('codeEditor');
      if (editor1?.dataset.path) {
        // Open same file in pane 2 for comparison (or could open a different file)
        this.openFileInPane2(editor1.dataset.path);
      }
      
      this.showToast('Split view enabled', 'info');
    } else {
      this.closeSplitEditor();
    }
  }
  
  closeSplitEditor() {
    const pane2 = document.getElementById('editorPane2');
    const resizer = document.getElementById('splitEditorResizer');
    const splitBtn = document.getElementById('splitEditorBtn');
    const pane1 = document.getElementById('editorPane1');
    
    this.splitEditorActive = false;
    pane2?.classList.remove('visible');
    resizer?.classList.remove('visible');
    splitBtn?.classList.remove('active');
    
    // Reset pane 1 width
    if (pane1) pane1.style.flex = '1';
    
    this.setActivePane(1);
    this.showToast('Split view closed', 'info');
  }
  
  async openFileInPane2(path) {
    try {
      const response = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
      const data = await response.json();
      
      const editor2 = document.getElementById('codeEditor2');
      if (editor2) {
        editor2.value = data.content;
        editor2.dataset.path = path;
        this.pane2File = path;
      }
      
      // Update pane 2 tabs
      this.updatePane2Tabs(data.name, path);
      
      // Update language indicator
      const lang = this.getLanguage(path);
      const langEl = document.getElementById('fileLanguage2');
      if (langEl) langEl.textContent = lang;
      
      this.updateLineNumbers2();
      this.updateSyntaxHighlighting2(data.content, path);
      
    } catch (error) {
      console.error('Failed to open file in pane 2:', error);
    }
  }
  
  updatePane2Tabs(name, path) {
    const paneTabs = document.getElementById('pane2Tabs');
    if (!paneTabs) return;
    
    const icon = this.getFileIcon(path.split('.').pop() || '');
    
    paneTabs.innerHTML = `
      <div class="pane-tab active" data-path="${path}">
        <span class="pane-tab-icon">${icon.svg}</span>
        <span class="pane-tab-name">${name}</span>
      </div>
    `;
  }
  
  updateLineNumbers2() {
    const editor = document.getElementById('codeEditor2');
    const lineNumbers = document.getElementById('lineNumbers2');
    if (!editor || !lineNumbers) return;
    
    const lines = editor.value.split('\n').length;
    lineNumbers.innerHTML = Array.from({ length: lines }, (_, i) => `<div>${i + 1}</div>`).join('');
  }
  
  updateCursorPosition2() {
    const editor = document.getElementById('codeEditor2');
    const positionEl = document.getElementById('cursorPosition2');
    if (!editor || !positionEl) return;
    
    const text = editor.value.substring(0, editor.selectionStart);
    const lines = text.split('\n');
    const line = lines.length;
    const col = lines[lines.length - 1].length + 1;
    
    positionEl.textContent = `Ln ${line}, Col ${col}`;
  }
  
  updateSyntaxHighlighting2(code, path) {
    const highlightCode = document.getElementById('highlightCode2');
    const highlightPre = document.getElementById('codeHighlight2');
    if (!highlightCode || !highlightPre) return;
    
    const lang = path ? this.getPrismLanguage(path) : 'javascript';
    highlightCode.className = `language-${lang}`;
    
    // Add newline to prevent scrollbar issues
    highlightCode.textContent = code + '\n';
    
    if (window.Prism) {
      Prism.highlightElement(highlightCode);
    }
  }
  
  async saveFile2() {
    const editor = document.getElementById('codeEditor2');
    const path = editor?.dataset.path;
    
    if (!path) {
      this.showToast('No file to save in pane 2', 'warning');
      return;
    }
    
    try {
      await fetch('/api/file', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path, content: editor.value })
      });
      
      this.showToast('File saved', 'success');
    } catch (error) {
      this.showToast('Failed to save file', 'error');
    }
  }
  
  setActivePane(pane) {
    this.activePane = pane;
    
    const pane1 = document.getElementById('editorPane1');
    const pane2 = document.getElementById('editorPane2');
    
    pane1?.classList.toggle('active', pane === 1);
    pane2?.classList.toggle('active', pane === 2);
  }
  
  initSplitResizer(resizer, pane1, pane2) {
    let isDragging = false;
    let startX = 0;
    let startPane1Width = 0;
    
    resizer.addEventListener('mousedown', (e) => {
      isDragging = true;
      startX = e.clientX;
      startPane1Width = pane1.offsetWidth;
      resizer.classList.add('dragging');
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    });
    
    document.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      
      const delta = e.clientX - startX;
      const container = pane1.parentElement;
      const containerWidth = container.offsetWidth;
      
      // Calculate new width as percentage
      let newPane1Width = startPane1Width + delta;
      const minWidth = 200;
      const maxWidth = containerWidth - minWidth - resizer.offsetWidth;
      
      newPane1Width = Math.max(minWidth, Math.min(maxWidth, newPane1Width));
      
      const pane1Flex = newPane1Width / containerWidth;
      const pane2Flex = 1 - pane1Flex - (resizer.offsetWidth / containerWidth);
      
      pane1.style.flex = `${pane1Flex} 0 auto`;
      pane2.style.flex = `${pane2Flex} 0 auto`;
    });
    
    document.addEventListener('mouseup', () => {
      if (isDragging) {
        isDragging = false;
        resizer.classList.remove('dragging');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      }
    });
  }
  
  // ===============================================
  // Code Folding
  // ===============================================
  
  initCodeFolding() {
    const lineNumbers = document.getElementById('lineNumbers');
    if (!lineNumbers) return;
    
    // Delegate click events for fold markers
    lineNumbers.addEventListener('click', (e) => {
      const marker = e.target.closest('.fold-marker');
      if (marker) {
        const lineIndex = parseInt(marker.dataset.line, 10);
        this.toggleFold(lineIndex);
      }
    });
  }
  
  detectFoldableRegions(lines) {
    const foldableLines = new Set();
    const bracketStack = [];
    
    // Patterns that start foldable regions
    const foldStartPatterns = [
      /^\s*(function|async\s+function)\s+\w+\s*\([^)]*\)\s*\{?\s*$/,      // function declarations
      /^\s*(const|let|var)\s+\w+\s*=\s*(async\s+)?\([^)]*\)\s*=>\s*\{?\s*$/, // arrow functions
      /^\s*(const|let|var)\s+\w+\s*=\s*function\s*\([^)]*\)\s*\{?\s*$/,   // function expressions
      /^\s*class\s+\w+/,                                                    // class declarations
      /^\s*(if|else\s+if|else|for|while|switch|try|catch|finally)\s*\(?/, // control structures
      /^\s*\w+\s*\([^)]*\)\s*\{?\s*$/,                                     // method definitions
      /^\s*\{$/,                                                            // plain blocks
      /^\s*\[$/,                                                            // array literals
      /\{\s*$/,                                                             // lines ending with {
      /\[\s*$/,                                                             // lines ending with [
    ];
    
    lines.forEach((line, i) => {
      const trimmed = line.trim();
      
      // Skip empty lines and comments
      if (!trimmed || trimmed.startsWith('//')) return;
      
      // Check if line opens a foldable region
      const openBrackets = (line.match(/\{/g) || []).length;
      const closeBrackets = (line.match(/\}/g) || []).length;
      const openBracketsDiff = openBrackets - closeBrackets;
      
      // If line has more opens than closes, it's foldable
      if (openBracketsDiff > 0) {
        foldableLines.add(i);
      }
      
      // Also check for multi-line patterns
      if (foldStartPatterns.some(pattern => pattern.test(line))) {
        // Look ahead to see if next line continues the block
        if (i < lines.length - 1 && !line.includes('}')) {
          foldableLines.add(i);
        }
      }
    });
    
    return foldableLines;
  }
  
  findMatchingCloseBracket(lines, startLine) {
    let depth = 0;
    let foundOpen = false;
    
    for (let i = startLine; i < lines.length; i++) {
      const line = lines[i];
      for (const char of line) {
        if (char === '{' || char === '[' || char === '(') {
          depth++;
          foundOpen = true;
        } else if (char === '}' || char === ']' || char === ')') {
          depth--;
          if (depth === 0 && foundOpen) {
            return i;
          }
        }
      }
    }
    
    return lines.length - 1;
  }
  
  toggleFold(lineIndex) {
    const editor = document.getElementById('codeEditor');
    if (!editor) return;
    
    if (this.foldedRegions.has(lineIndex)) {
      // Unfold
      this.foldedRegions.delete(lineIndex);
    } else {
      // Fold
      this.foldedRegions.add(lineIndex);
    }
    
    this.updateLineNumbers();
    this.applyFolding();
  }
  
  applyFolding() {
    const editor = document.getElementById('codeEditor');
    const highlightCode = document.getElementById('highlightCode');
    if (!editor || !highlightCode) return;
    
    const lines = editor.value.split('\n');
    const visibleLines = [];
    const hiddenRanges = [];
    
    // Calculate which lines to hide
    this.foldedRegions.forEach(startLine => {
      const endLine = this.findMatchingCloseBracket(lines, startLine);
      hiddenRanges.push({ start: startLine + 1, end: endLine });
    });
    
    // Sort ranges by start line
    hiddenRanges.sort((a, b) => a.start - b.start);
    
    // Build visible content
    let skipUntil = -1;
    lines.forEach((line, i) => {
      if (i < skipUntil) return;
      
      // Check if this line should be hidden
      const range = hiddenRanges.find(r => i >= r.start && i <= r.end);
      if (range && i === range.start) {
        // Add fold indicator to the previous line
        visibleLines[visibleLines.length - 1] += ' /* ... */';
        skipUntil = range.end + 1;
        return;
      }
      
      if (i >= skipUntil) {
        visibleLines.push(line);
      }
    });
    
    // Update display (only syntax highlight layer - actual textarea stays intact for editing)
    const displayContent = visibleLines.join('\n');
    highlightCode.textContent = displayContent + '\n';
    
    if (window.Prism) {
      Prism.highlightElement(highlightCode);
    }
    
    // Add visual indicator for folded regions in line numbers
    this.updateFoldDisplay();
  }
  
  updateFoldDisplay() {
    const lineNumbers = document.getElementById('lineNumbers');
    if (!lineNumbers) return;
    
    // Add 'folded' class to folded regions
    this.foldedRegions.forEach(lineIndex => {
      const lineEl = lineNumbers.children[lineIndex];
      if (lineEl) {
        lineEl.classList.add('has-fold');
      }
    });
  }
  
  // ===============================================
  // Bracket Matching
  // ===============================================
  
  initBracketMatching() {
    const editor = document.getElementById('codeEditor');
    if (!editor) return;
    
    // Track cursor position for bracket matching
    editor.addEventListener('keyup', () => this.highlightMatchingBrackets());
    editor.addEventListener('click', () => this.highlightMatchingBrackets());
    
    // Create bracket highlight overlay
    this.createBracketHighlightOverlay();
  }
  
  createBracketHighlightOverlay() {
    const wrapper = document.querySelector('.code-editor-wrapper');
    if (!wrapper || document.getElementById('bracketHighlightOverlay')) return;
    
    const overlay = document.createElement('div');
    overlay.id = 'bracketHighlightOverlay';
    overlay.className = 'bracket-highlight-overlay';
    wrapper.appendChild(overlay);
  }
  
  highlightMatchingBrackets() {
    const editor = document.getElementById('codeEditor');
    const overlay = document.getElementById('bracketHighlightOverlay');
    if (!editor || !overlay) return;
    
    const brackets = { '(': ')', '[': ']', '{': '}' };
    const closeBrackets = { ')': '(', ']': '[', '}': '{' };
    const allBrackets = { ...brackets, ...closeBrackets };
    
    const cursor = editor.selectionStart;
    const text = editor.value;
    
    // Clear previous highlights
    overlay.innerHTML = '';
    
    // Check character at cursor and before cursor
    const charAtCursor = text[cursor];
    const charBeforeCursor = text[cursor - 1];
    
    let bracketPos = -1;
    let bracket = null;
    
    if (allBrackets[charAtCursor]) {
      bracketPos = cursor;
      bracket = charAtCursor;
    } else if (allBrackets[charBeforeCursor]) {
      bracketPos = cursor - 1;
      bracket = charBeforeCursor;
    }
    
    if (bracketPos === -1 || !bracket) return;
    
    // Find matching bracket
    let matchPos = -1;
    if (brackets[bracket]) {
      // Opening bracket - search forward
      matchPos = this.findMatchingBracketForward(text, bracketPos, bracket, brackets[bracket]);
    } else if (closeBrackets[bracket]) {
      // Closing bracket - search backward
      matchPos = this.findMatchingBracketBackward(text, bracketPos, bracket, closeBrackets[bracket]);
    }
    
    if (matchPos !== -1) {
      // Highlight both brackets
      this.addBracketHighlight(editor, bracketPos);
      this.addBracketHighlight(editor, matchPos);
    } else {
      // No match found - highlight with error color
      this.addBracketHighlight(editor, bracketPos, true);
    }
  }
  
  findMatchingBracketForward(text, pos, openBracket, closeBracket) {
    let depth = 1;
    for (let i = pos + 1; i < text.length; i++) {
      if (text[i] === openBracket) depth++;
      else if (text[i] === closeBracket) {
        depth--;
        if (depth === 0) return i;
      }
    }
    return -1;
  }
  
  findMatchingBracketBackward(text, pos, closeBracket, openBracket) {
    let depth = 1;
    for (let i = pos - 1; i >= 0; i--) {
      if (text[i] === closeBracket) depth++;
      else if (text[i] === openBracket) {
        depth--;
        if (depth === 0) return i;
      }
    }
    return -1;
  }
  
  addBracketHighlight(editor, pos, isError = false) {
    const overlay = document.getElementById('bracketHighlightOverlay');
    if (!overlay) return;
    
    // Calculate position
    const text = editor.value.substring(0, pos);
    const lines = text.split('\n');
    const line = lines.length - 1;
    const col = lines[lines.length - 1].length;
    
    // Get editor metrics
    const style = getComputedStyle(editor);
    const lineHeight = parseFloat(style.lineHeight);
    const fontSize = parseFloat(style.fontSize);
    
    // Create highlight element
    const highlight = document.createElement('span');
    highlight.className = `bracket-highlight ${isError ? 'error' : 'match'}`;
    highlight.textContent = editor.value[pos];
    
    // Position based on character offset
    const charWidth = fontSize * 0.6; // Approximate for monospace
    const paddingLeft = parseFloat(style.paddingLeft);
    const paddingTop = parseFloat(style.paddingTop);
    
    highlight.style.left = `${paddingLeft + col * charWidth}px`;
    highlight.style.top = `${paddingTop + line * lineHeight}px`;
    highlight.style.width = `${charWidth}px`;
    highlight.style.height = `${lineHeight}px`;
    
    overlay.appendChild(highlight);
  }
  
  // ===============================================
  // Session Persistence
  // ===============================================
  
  initSessionPersistence() {
    // Restore session on load
    this.restoreSession();
    
    // Save session periodically and on beforeunload
    setInterval(() => this.saveSession(), 30000); // Every 30 seconds
    
    window.addEventListener('beforeunload', () => {
      this.saveSession();
    });
  }
  
  saveSession() {
    const session = {
      openTabs: [],
      activeTab: null,
      currentPath: this.currentPath,
      terminalCollapsed: this.terminalCollapsed,
      sidebarView: this.currentView,
      splitEditorActive: this.splitEditorActive,
      pane2File: this.pane2File
    };
    
    // Get open tabs from DOM
    const tabs = document.querySelectorAll('.tabs-scroll .tab-item[data-path]');
    tabs.forEach(tab => {
      const path = tab.dataset.path;
      if (path && path !== 'welcome') {
        session.openTabs.push(path);
        if (tab.classList.contains('active')) {
          session.activeTab = path;
        }
      }
    });
    
    // Save to localStorage
    try {
      localStorage.setItem('aria_session', JSON.stringify(session));
    } catch (e) {
      console.warn('Failed to save session:', e);
    }
  }
  
  restoreSession() {
    try {
      const saved = localStorage.getItem('aria_session');
      if (!saved) return;
      
      const session = JSON.parse(saved);
      
      // Restore current path
      if (session.currentPath) {
        this.currentPath = session.currentPath;
        this.loadFiles(session.currentPath);
      }
      
      // Restore sidebar view
      if (session.sidebarView) {
        this.switchView(session.sidebarView);
      }
      
      // Restore terminal state
      if (session.terminalCollapsed) {
        this.toggleTerminal();
      }
      
      // Restore open tabs
      if (session.openTabs && session.openTabs.length > 0) {
        // Open each tab (but don't focus yet)
        session.openTabs.forEach(async (path, index) => {
          try {
            await this.openFile(path);
            
            // If this is the last tab and we have an active tab, switch to it
            if (index === session.openTabs.length - 1 && session.activeTab) {
              this.openFile(session.activeTab);
            }
          } catch (e) {
            console.warn('Failed to restore tab:', path, e);
          }
        });
      }
      
      // Restore split editor
      if (session.splitEditorActive && session.pane2File) {
        setTimeout(() => {
          this.toggleSplitEditor();
          if (session.pane2File) {
            this.openFileInPane2(session.pane2File);
          }
        }, 500);
      }
      
      console.log('[ARIA] Session restored');
    } catch (e) {
      console.warn('Failed to restore session:', e);
    }
  }
  
  clearSession() {
    localStorage.removeItem('aria_session');
    console.log('[ARIA] Session cleared');
  }
  
  markUnsaved(unsaved) {
    this.hasUnsavedChanges = unsaved;
    const editor = document.getElementById('codeEditor');
    const path = editor?.dataset.path;
    
    if (path) {
      const tab = document.querySelector(`.tab-item[data-path="${path}"]`);
      if (tab) {
        tab.classList.toggle('unsaved', unsaved);
      }
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
      
      // Update status
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
  
  async openFile(path) {
    try {
      const response = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
      const data = await response.json();
      
      // Switch to editor tab
      this.showEditorTab(data.name, path);
      
      const editor = document.getElementById('codeEditor');
      if (editor) {
        editor.value = data.content;
        editor.dataset.path = path;
      }
      
      const lang = this.getLanguage(path);
      document.getElementById('fileLanguage').textContent = lang;
      
      this.updateLineNumbers();
      this.updateCursorPosition();
      this.updateSyntaxHighlighting(data.content, path);
      
      // Track in memory
      if (window.AriaMemory) {
        window.AriaMemory.trackFileOpen(path);
        window.AriaMemory.setCurrentContext({ currentFile: path });
      }
      
    } catch (error) {
      this.showToast('Failed to open file', 'error');
    }
  }
  
  showEditorTab(name, path) {
    // Hide welcome, show editor
    document.getElementById('welcomeTab')?.classList.remove('active');
    document.getElementById('codeEditorTab')?.classList.add('active');
    
    // Update tabs
    const tabs = document.querySelector('.tabs-scroll');
    if (tabs) {
      // Check if tab exists
      let tab = tabs.querySelector(`[data-path="${path}"]`);
      if (!tab) {
        tab = document.createElement('div');
        tab.className = 'tab-item';
        tab.dataset.path = path;
        tab.dataset.tab = 'editor';
        tab.innerHTML = `
          <span>${name}</span>
          <button class="tab-close">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        `;
        
        tab.addEventListener('click', () => this.openFile(path));
        tab.querySelector('.tab-close').addEventListener('click', (e) => {
          e.stopPropagation();
          this.closeTab(path);
        });
        
        tabs.appendChild(tab);
      }
      
      // Set active
      tabs.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
    }
  }
  
  showWelcomeTab() {
    document.getElementById('codeEditorTab')?.classList.remove('active');
    document.getElementById('welcomeTab')?.classList.add('active');
    
    document.querySelectorAll('.tab-item').forEach(t => {
      t.classList.toggle('active', t.dataset.tab === 'welcome');
    });
  }
  
  closeTab(path) {
    const tabs = document.querySelector('.tabs-scroll');
    const tab = tabs?.querySelector(`[data-path="${path}"]`);
    
    if (tab) {
      const wasActive = tab.classList.contains('active');
      tab.remove();
      
      if (wasActive) {
        this.showWelcomeTab();
      }
    }
    
    this.openFiles.delete(path);
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
    
    // Update minimap
    this.updateMinimap(editor.value);
  }
  
  updateMinimap(content) {
    const canvas = document.getElementById('minimapCanvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const minimapContainer = document.getElementById('minimap');
    if (!minimapContainer) return;
    
    // Set canvas size
    const width = minimapContainer.clientWidth;
    const height = minimapContainer.clientHeight;
    canvas.width = width * window.devicePixelRatio;
    canvas.height = height * window.devicePixelRatio;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    
    // Clear
    ctx.clearRect(0, 0, width, height);
    
    const lines = (content || '').split('\n');
    const lineHeight = 2;
    const charWidth = 0.5;
    const padding = 4;
    
    // Draw each line
    lines.forEach((line, i) => {
      const y = i * lineHeight;
      if (y > height) return;
      
      // Color based on content type
      let color = 'rgba(148, 163, 184, 0.3)'; // Default text color
      
      const trimmed = line.trim();
      if (trimmed.startsWith('//') || trimmed.startsWith('#') || trimmed.startsWith('/*')) {
        color = 'rgba(106, 115, 125, 0.4)'; // Comments
      } else if (trimmed.match(/^(function|const|let|var|class|import|export|def|async|await)/)) {
        color = 'rgba(124, 58, 237, 0.5)'; // Keywords - purple
      } else if (trimmed.match(/^(if|else|for|while|return|try|catch|switch|case)/)) {
        color = 'rgba(168, 85, 247, 0.5)'; // Control flow - light purple
      } else if (trimmed.includes('=>') || trimmed.includes('function')) {
        color = 'rgba(6, 182, 212, 0.5)'; // Functions - cyan
      } else if (trimmed.match(/["'`]/)) {
        color = 'rgba(16, 185, 129, 0.5)'; // Strings - green
      }
      
      // Draw line representation
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
      const visibleLines = Math.floor(editor.clientHeight / 21); // Approximate line height
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
  
  updateCursorPosition() {
    const editor = document.getElementById('codeEditor');
    if (!editor) return;
    
    const pos = editor.selectionStart;
    const text = editor.value.substring(0, pos);
    const lines = text.split('\n');
    const line = lines.length;
    const col = lines[lines.length - 1].length + 1;
    
    document.getElementById('cursorPosition').textContent = `Ln ${line}, Col ${col}`;
    
    // Selection info
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const selectionInfo = document.getElementById('selectionInfo');
    if (selectionInfo) {
      if (start !== end) {
        const selected = editor.value.substring(start, end);
        selectionInfo.textContent = `(${selected.length} selected)`;
      } else {
        selectionInfo.textContent = '';
      }
    }
  }
  
  getLanguage(path) {
    const ext = path.split('.').pop().toLowerCase();
    const languages = {
      js: 'JavaScript',
      ts: 'TypeScript',
      jsx: 'React JSX',
      tsx: 'React TSX',
      py: 'Python',
      go: 'Go',
      json: 'JSON',
      md: 'Markdown',
      html: 'HTML',
      css: 'CSS',
      scss: 'SCSS',
      yaml: 'YAML',
      yml: 'YAML',
      sh: 'Shell',
      bash: 'Bash'
    };
    return languages[ext] || 'Plain Text';
  }
  
  getPrismLanguage(path) {
    const ext = path.split('.').pop().toLowerCase();
    const prismLanguages = {
      js: 'javascript',
      mjs: 'javascript',
      cjs: 'javascript',
      ts: 'typescript',
      jsx: 'jsx',
      tsx: 'tsx',
      py: 'python',
      go: 'go',
      rs: 'rust',
      json: 'json',
      md: 'markdown',
      html: 'markup',
      htm: 'markup',
      xml: 'markup',
      svg: 'markup',
      css: 'css',
      scss: 'css',
      sass: 'css',
      yaml: 'yaml',
      yml: 'yaml',
      sh: 'bash',
      bash: 'bash',
      zsh: 'bash',
      sql: 'sql',
      toml: 'toml',
      dockerfile: 'docker',
      makefile: 'makefile'
    };
    return prismLanguages[ext] || 'plaintext';
  }
  
  updateSyntaxHighlighting(content, path) {
    const highlightCode = document.getElementById('highlightCode');
    const highlightPre = document.getElementById('codeHighlight');
    const editor = document.getElementById('codeEditor');
    
    if (!highlightCode || !highlightPre) return;
    
    const lang = this.getPrismLanguage(path || editor?.dataset?.path || '');
    
    // Update the language class
    highlightCode.className = `language-${lang}`;
    
    // Escape HTML and add content
    const escapedContent = this.escapeHtml(content || editor?.value || '');
    highlightCode.innerHTML = escapedContent;
    
    // Run Prism highlighting
    if (window.Prism) {
      Prism.highlightElement(highlightCode);
    }
    
    // Sync scroll position
    if (editor && highlightPre) {
      highlightPre.scrollTop = editor.scrollTop;
      highlightPre.scrollLeft = editor.scrollLeft;
    }
    
    // Update code lens suggestions
    this.updateCodeLens(content || editor?.value || '', path || editor?.dataset?.path);
  }
  
  updateCodeLens(content, path) {
    const container = document.getElementById('codeLensContainer');
    if (!container) return;
    
    // Clear existing lens items
    container.innerHTML = '';
    
    // Don't analyze if no content or path
    if (!content || !path) return;
    
    const lines = content.split('\n');
    const ext = path.split('.').pop().toLowerCase();
    
    // Only analyze JavaScript/TypeScript files for now
    if (!['js', 'ts', 'jsx', 'tsx'].includes(ext)) return;
    
    // Find functions and classes for code lens
    const lensItems = [];
    
    lines.forEach((line, i) => {
      // Detect function definitions
      const funcMatch = line.match(/^(\s*)(async\s+)?function\s+(\w+)/);
      const arrowMatch = line.match(/^(\s*)(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(/);
      const classMatch = line.match(/^(\s*)class\s+(\w+)/);
      const methodMatch = line.match(/^(\s*)(?:async\s+)?(\w+)\s*\([^)]*\)\s*{/);
      
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
    
    // Only show first 10 code lens items to avoid clutter
    lensItems.slice(0, 10).forEach(item => {
      const lens = document.createElement('div');
      lens.className = 'code-lens-item';
      lens.style.top = `${item.line * 21}px`; // Approximate line height
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
    
    // Extract relevant code (the function or class)
    const lines = editor.value.split('\n');
    let startLine = line;
    let endLine = line;
    let braceCount = 0;
    let started = false;
    
    for (let i = line; i < lines.length; i++) {
      const lineContent = lines[i];
      for (const char of lineContent) {
        if (char === '{') {
          braceCount++;
          started = true;
        }
        if (char === '}') {
          braceCount--;
        }
      }
      endLine = i;
      if (started && braceCount === 0) break;
    }
    
    const codeSnippet = lines.slice(startLine, endLine + 1).join('\n');
    
    // Open AI sidebar with appropriate prompt
    this.showAISidebar();
    const aiInput = document.getElementById('aiInput');
    
    if (action.includes('Explain')) {
      aiInput.value = `Explain this function "${name}":\n\`\`\`\n${codeSnippet}\n\`\`\``;
    } else if (action.includes('Optimize')) {
      aiInput.value = `Suggest optimizations for this function "${name}":\n\`\`\`\n${codeSnippet}\n\`\`\``;
    } else if (action.includes('Tests')) {
      aiInput.value = `Generate unit tests for this function "${name}":\n\`\`\`\n${codeSnippet}\n\`\`\``;
    } else if (action.includes('Document')) {
      aiInput.value = `Generate documentation for "${name}":\n\`\`\`\n${codeSnippet}\n\`\`\``;
    } else if (action.includes('Review')) {
      aiInput.value = `Review this code for issues:\n\`\`\`\n${codeSnippet}\n\`\`\``;
    }
    
    aiInput.focus();
  }
  
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
  
  async saveFile() {
    const editor = document.getElementById('codeEditor');
    const path = editor?.dataset.path;
    
    if (!path) {
      this.showToast('No file to save', 'warning');
      return;
    }
    
    try {
      await fetch('/api/file', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path, content: editor.value })
      });
      
      this.showToast('File saved', 'success');
      
      if (window.AriaMemory) {
        window.AriaMemory.trackFileEdit(path, { type: 'save' });
      }
    } catch (error) {
      this.showToast('Failed to save file', 'error');
    }
  }
  
  async createFile(name) {
    if (!name) return;
    
    const filePath = `${this.currentPath}/${name}`;
    try {
      await fetch('/api/file', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: filePath, content: '' })
      });
      this.showToast(`File "${name}" created`, 'success');
      this.loadDirectory(this.currentPath);
    } catch (error) {
      this.showToast('Failed to create file', 'error');
    }
  }
  
  async createFolder(name) {
    if (!name) return;
    
    const folderPath = `${this.currentPath}/${name}`;
    try {
      await fetch('/api/mkdir', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: folderPath })
      });
      this.showToast(`Folder "${name}" created`, 'success');
      this.loadDirectory(this.currentPath);
    } catch (error) {
      this.showToast('Failed to create folder', 'error');
    }
  }
  
  // ===============================================
  // Terminal
  // ===============================================
  
  initTerminal() {
    const theme = document.documentElement.getAttribute('data-theme') || 'dark';
    
    this.terminal = new Terminal({
      fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
      fontSize: 13,
      lineHeight: 1.4,
      cursorBlink: true,
      cursorStyle: 'bar',
      allowTransparency: true,
      theme: {
        background: theme === 'dark' ? '#0a0b0f' : '#f8fafc',
        foreground: theme === 'dark' ? '#f1f5f9' : '#0f172a',
        cursor: '#7c3aed',
        selectionBackground: 'rgba(124, 58, 237, 0.3)',
      }
    });
    
    this.fitAddon = new FitAddon.FitAddon();
    const webLinksAddon = new WebLinksAddon.WebLinksAddon();
    
    this.terminal.loadAddon(this.fitAddon);
    this.terminal.loadAddon(webLinksAddon);
    
    const container = document.getElementById('terminal');
    if (container) {
      this.terminal.open(container);
      this.fitAddon.fit();
    }
    
    this.connectTerminal();
    
    this.terminal.onData((data) => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'input', data }));
      }
    });
    
    window.addEventListener('resize', () => {
      this.fitAddon?.fit();
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({
          type: 'resize',
          cols: this.terminal.cols,
          rows: this.terminal.rows
        }));
      }
    });
    
    // Terminal actions
    document.getElementById('toggleTerminalBtn')?.addEventListener('click', () => {
      this.toggleTerminal();
    });
    
    document.getElementById('maximizeTerminalBtn')?.addEventListener('click', () => {
      // Toggle maximize
    });
    
    // Terminal resizer
    this.initTerminalResizer();
  }
  
  initTerminalResizer() {
    const resizer = document.getElementById('terminalResizer');
    const terminal = document.getElementById('terminalWrapper');
    if (!resizer || !terminal) return;
    
    let isDragging = false;
    let startY = 0;
    let startHeight = 0;
    
    resizer.addEventListener('mousedown', (e) => {
      isDragging = true;
      startY = e.clientY;
      startHeight = terminal.offsetHeight;
      resizer.classList.add('dragging');
      document.body.style.cursor = 'row-resize';
      document.body.style.userSelect = 'none';
      e.preventDefault();
    });
    
    document.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      
      const delta = startY - e.clientY;
      const newHeight = Math.max(100, Math.min(window.innerHeight - 200, startHeight + delta));
      terminal.style.height = `${newHeight}px`;
      
      // Refit the terminal
      if (this.fitAddon) {
        this.fitAddon.fit();
      }
    });
    
    document.addEventListener('mouseup', () => {
      if (isDragging) {
        isDragging = false;
        resizer.classList.remove('dragging');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        
        // Send resize to server
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
          this.ws.send(JSON.stringify({
            type: 'resize',
            cols: this.terminal.cols,
            rows: this.terminal.rows
          }));
        }
      }
    });
  }
  
  connectTerminal() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    this.ws = new WebSocket(`${protocol}//192.168.1.160:3000/terminal`);
    
    this.ws.onopen = () => {
      this.updateConnectionStatus(true);
      this.terminal.write('\x1b[38;5;141m   _    ____  ___    _   \x1b[0m\r\n');
      this.terminal.write('\x1b[38;5;141m  / \\  |  _ \\|_ _|  / \\  \x1b[0m\r\n');
      this.terminal.write('\x1b[38;5;141m / _ \\ | |_) || |  / _ \\ \x1b[0m\r\n');
      this.terminal.write('\x1b[38;5;141m/ ___ \\|  _ < | | / ___ \\\x1b[0m\r\n');
      this.terminal.write('\x1b[38;5;141m/_/  \\_\\_| \\_\\___/_/   \\_\\\x1b[0m\r\n\r\n');
      this.terminal.write('\x1b[38;5;81mSynthetic Intelligence IDE\x1b[0m\r\n');
      this.terminal.write('\x1b[38;5;245mTerminal ready.\x1b[0m\r\n\r\n');
      
      this.ws.send(JSON.stringify({
        type: 'resize',
        cols: this.terminal.cols,
        rows: this.terminal.rows
      }));
    };
    
    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'output') {
          this.terminal.write(msg.data);
        }
      } catch (e) {
        console.error('Error parsing message:', e);
      }
    };
    
    this.ws.onclose = () => {
      this.updateConnectionStatus(false);
      this.terminal.write('\r\n\x1b[38;5;196mDisconnected. Reconnecting...\x1b[0m\r\n');
      setTimeout(() => this.connectTerminal(), 3000);
    };
    
    this.ws.onerror = () => {
      this.updateConnectionStatus(false);
    };
  }
  
  toggleTerminal() {
    const wrapper = document.getElementById('terminalWrapper');
    if (wrapper) {
      wrapper.classList.toggle('collapsed');
      this.terminalCollapsed = wrapper.classList.contains('collapsed');
      setTimeout(() => this.fitAddon?.fit(), 300);
    }
  }
  
  updateConnectionStatus(connected) {
    const status = document.getElementById('connectionStatus');
    if (status) {
      if (connected) {
        status.classList.add('connected');
        status.classList.remove('disconnected');
        status.innerHTML = '<span class="status-dot"></span>Connected';
      } else {
        status.classList.remove('connected');
        status.classList.add('disconnected');
        status.innerHTML = '<span class="status-dot"></span>Disconnected';
      }
    }
  }
  
  // ===============================================
  // Command Palette
  // ===============================================
  
  initCommandPalette() {
    this.commands = this.buildCommands();
    
    const palette = document.getElementById('commandPalette');
    const input = document.getElementById('commandInput');
    
    if (!palette || !input) return;
    
    input.addEventListener('input', () => this.filterCommands());
    input.addEventListener('keydown', (e) => this.handleCommandKeydown(e));
    
    palette.addEventListener('click', (e) => {
      if (e.target === palette) {
        this.hideCommandPalette();
      }
    });
    
    // Category buttons
    document.querySelectorAll('.category-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.filterCommands(btn.dataset.category);
      });
    });
    
    this.renderCommands();
  }
  
  buildCommands() {
    return [
      { id: 'file:new', title: 'New File', description: 'Create a new file', category: 'file', icon: 'file-plus', shortcut: 'Ctrl+N', action: () => this.showInputModal('New File', 'Enter filename:', (name) => this.createFile(name)) },
      { id: 'file:open', title: 'Open File', description: 'Open a file', category: 'file', icon: 'file', action: () => this.switchView('explorer') },
      { id: 'file:save', title: 'Save File', description: 'Save current file', category: 'file', icon: 'save', shortcut: 'Ctrl+S', action: () => this.saveFile() },
      { id: 'view:explorer', title: 'Show Explorer', description: 'Show file explorer', category: 'view', icon: 'folder', shortcut: 'Ctrl+Shift+E', action: () => this.switchView('explorer') },
      { id: 'view:search', title: 'Show Search', description: 'Show global search', category: 'view', icon: 'search', shortcut: 'Ctrl+Shift+F', action: () => this.switchView('search') },
      { id: 'view:git', title: 'Show Source Control', description: 'Show git panel', category: 'git', icon: 'git-branch', shortcut: 'Ctrl+Shift+G', action: () => this.switchView('git') },
      { id: 'ai:chat', title: 'Open AI Chat', description: 'Open AI assistant', category: 'ai', icon: 'cpu', shortcut: 'Ctrl+/', action: () => this.toggleAISidebar() },
      { id: 'ai:explain', title: 'AI: Explain Code', description: 'Ask AI to explain current code', category: 'ai', icon: 'help-circle', action: () => this.aiExplainCode() },
      { id: 'ai:refactor', title: 'AI: Refactor Code', description: 'Ask AI to refactor current code', category: 'ai', icon: 'refresh-cw', action: () => this.aiRefactorCode() },
      { id: 'git:commit', title: 'Git: Commit', description: 'Commit staged changes', category: 'git', icon: 'check', action: () => this.gitCommit() },
      { id: 'git:pull', title: 'Git: Pull', description: 'Pull from remote', category: 'git', icon: 'download', action: () => this.runCommand('git pull') },
      { id: 'git:push', title: 'Git: Push', description: 'Push to remote', category: 'git', icon: 'upload', action: () => this.runCommand('git push') },
      { id: 'workflow:run', title: 'Run Workflow', description: 'Run a workflow', category: 'workflow', icon: 'play', action: () => this.switchView('workflows') },
      { id: 'terminal:toggle', title: 'Toggle Terminal', description: 'Show/hide terminal', category: 'view', icon: 'terminal', shortcut: 'Ctrl+`', action: () => this.toggleTerminal() },
      { id: 'theme:toggle', title: 'Toggle Theme', description: 'Switch between light and dark', category: 'view', icon: 'moon', action: () => this.toggleTheme() },
    ];
  }
  
  showCommandPalette() {
    const palette = document.getElementById('commandPalette');
    const input = document.getElementById('commandInput');
    
    if (palette) {
      palette.classList.add('visible');
      this.commandPaletteVisible = true;
      input?.focus();
      this.renderCommands();
    }
  }
  
  hideCommandPalette() {
    const palette = document.getElementById('commandPalette');
    if (palette) {
      palette.classList.remove('visible');
      this.commandPaletteVisible = false;
      document.getElementById('commandInput').value = '';
    }
  }
  
  filterCommands(category = 'all') {
    const query = document.getElementById('commandInput')?.value.toLowerCase() || '';
    let filtered = this.commands;
    
    if (category !== 'all') {
      filtered = filtered.filter(c => c.category === category);
    }
    
    if (query) {
      filtered = filtered.filter(c => 
        c.title.toLowerCase().includes(query) ||
        c.description.toLowerCase().includes(query)
      );
    }
    
    this.renderCommands(filtered);
  }
  
  renderCommands(commands = this.commands) {
    const results = document.getElementById('commandResults');
    if (!results) return;
    
    results.innerHTML = commands.map((cmd, i) => `
      <div class="command-item${i === this.commandIndex ? ' selected' : ''}" data-id="${cmd.id}">
        <div class="command-item-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/>
          </svg>
        </div>
        <div class="command-item-content">
          <div class="command-item-title">${cmd.title}</div>
          <div class="command-item-description">${cmd.description}</div>
        </div>
        ${cmd.shortcut ? `<div class="command-item-shortcut">${cmd.shortcut.split('+').map(k => `<kbd>${k}</kbd>`).join('')}</div>` : ''}
      </div>
    `).join('');
    
    results.querySelectorAll('.command-item').forEach(item => {
      item.addEventListener('click', () => {
        const cmd = this.commands.find(c => c.id === item.dataset.id);
        if (cmd) {
          this.executeCommand(cmd);
        }
      });
    });
  }
  
  handleCommandKeydown(e) {
    const items = document.querySelectorAll('.command-item');
    
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      this.commandIndex = Math.min(this.commandIndex + 1, items.length - 1);
      this.updateCommandSelection();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      this.commandIndex = Math.max(this.commandIndex - 1, 0);
      this.updateCommandSelection();
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const selectedItem = items[this.commandIndex];
      if (selectedItem) {
        const cmd = this.commands.find(c => c.id === selectedItem.dataset.id);
        if (cmd) {
          this.executeCommand(cmd);
        }
      }
    } else if (e.key === 'Escape') {
      this.hideCommandPalette();
    }
  }
  
  updateCommandSelection() {
    document.querySelectorAll('.command-item').forEach((item, i) => {
      item.classList.toggle('selected', i === this.commandIndex);
    });
  }
  
  executeCommand(cmd) {
    this.hideCommandPalette();
    cmd.action();
    
    if (window.AriaMemory) {
      window.AriaMemory.trackCommand(cmd.id);
    }
  }
  
  // ===============================================
  // AI Sidebar
  // ===============================================
  
  initAISidebar() {
    const sidebar = document.getElementById('aiSidebar');
    const input = document.getElementById('aiInput');
    const sendBtn = document.getElementById('aiSend');
    
    // Close button
    document.getElementById('aiSidebarClose')?.addEventListener('click', () => {
      this.hideAISidebar();
    });
    
    // Send message
    sendBtn?.addEventListener('click', () => this.sendAIMessage());
    
    input?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendAIMessage();
      }
    });
    
    // Auto-resize input
    input?.addEventListener('input', () => {
      input.style.height = 'auto';
      input.style.height = Math.min(input.scrollHeight, 120) + 'px';
    });
    
    // Suggestion chips
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const prompt = chip.dataset.prompt;
        if (input) {
          input.value = prompt;
          this.sendAIMessage();
        }
      });
    });
    
    // Context buttons
    document.querySelectorAll('.context-item').forEach(item => {
      item.addEventListener('click', () => {
        document.querySelectorAll('.context-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
      });
    });
    
    // Voice input
    document.getElementById('aiVoiceInput')?.addEventListener('click', () => {
      this.startVoiceInput();
    });
  }
  
  toggleAISidebar() {
    if (this.aiSidebarVisible) {
      this.hideAISidebar();
    } else {
      this.showAISidebar();
    }
  }
  
  showAISidebar() {
    const sidebar = document.getElementById('aiSidebar');
    if (sidebar) {
      sidebar.classList.add('visible');
      this.aiSidebarVisible = true;
      document.getElementById('aiInput')?.focus();
      document.getElementById('aiChatBtn')?.classList.add('active');
    }
  }
  
  hideAISidebar() {
    const sidebar = document.getElementById('aiSidebar');
    if (sidebar) {
      sidebar.classList.remove('visible');
      this.aiSidebarVisible = false;
      document.getElementById('aiChatBtn')?.classList.remove('active');
    }
  }
  
  async sendAIMessage() {
    const input = document.getElementById('aiInput');
    const messages = document.getElementById('aiMessages');
    const message = input?.value.trim();
    
    if (!message) return;
    
    // Clear welcome
    const welcome = messages?.querySelector('.ai-welcome');
    if (welcome) welcome.remove();
    
    // Add user message
    this.addAIMessage(message, 'user');
    input.value = '';
    input.style.height = 'auto';
    
    // Store in memory
    if (window.AriaMemory) {
      window.AriaMemory.addConversation(message, 'user');
    }
    
    // Update token count display
    this.updateTokenCount(message);
    
    // Show typing indicator
    const typingId = this.addAITypingIndicator();
    
    // Get current context for AI
    const context = this.getAIContext();
    
    try {
      // Call actual backend AI API
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          context,
          agentId: this.currentAIAgent || null
        })
      });
      
      if (!response.ok) {
        throw new Error('AI request failed');
      }
      
      const data = await response.json();
      
      this.removeAITypingIndicator(typingId);
      
      const aiResponse = data.content || data.response || this.generateAIResponse(message);
      this.addAIMessage(aiResponse, 'assistant', data.agent);
      
      if (window.AriaMemory) {
        window.AriaMemory.addConversation(aiResponse, 'assistant');
      }
    } catch (error) {
      console.error('AI chat error:', error);
      this.removeAITypingIndicator(typingId);
      
      // Fallback to local response generation
      const fallbackResponse = this.generateAIResponse(message);
      this.addAIMessage(fallbackResponse, 'assistant');
      
      if (window.AriaMemory) {
        window.AriaMemory.addConversation(fallbackResponse, 'assistant');
      }
    }
  }
  
  getAIContext() {
    const editor = document.getElementById('codeEditor');
    const currentFile = editor?.dataset?.path || null;
    const selection = editor ? editor.value.substring(editor.selectionStart, editor.selectionEnd) : '';
    const fileContent = editor?.value || '';
    
    return {
      currentFile,
      selection: selection.length > 0 ? selection : null,
      fileContent: fileContent.substring(0, 5000), // Limit context size
      language: this.getLanguage(currentFile || ''),
      recentFiles: window.AriaMemory?.getRecentFiles(5) || [],
      conversationHistory: window.AriaMemory?.getConversationHistory(10) || []
    };
  }
  
  updateTokenCount(message) {
    // Approximate token count (roughly 4 chars per token)
    const tokens = Math.ceil(message.length / 4);
    const tokenDisplay = document.getElementById('tokenCount');
    if (tokenDisplay) {
      tokenDisplay.textContent = `~${tokens} tokens`;
    }
  }
  
  addAIMessage(content, role, agentName = null) {
    const messages = document.getElementById('aiMessages');
    if (!messages) return;
    
    const div = document.createElement('div');
    div.className = `ai-message ${role}`;
    
    const timestamp = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    
    if (role === 'assistant' && agentName) {
      div.innerHTML = `
        <div class="message-agent">${agentName}</div>
        <div class="message-content">${this.formatAIMessage(content)}</div>
        <div class="message-time">${timestamp}</div>
      `;
    } else {
      div.innerHTML = `
        <div class="message-content">${this.formatAIMessage(content)}</div>
        <div class="message-time">${timestamp}</div>
      `;
    }
    
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
    
    // Add copy button for assistant messages
    if (role === 'assistant') {
      const copyBtn = document.createElement('button');
      copyBtn.className = 'message-copy-btn';
      copyBtn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`;
      copyBtn.title = 'Copy to clipboard';
      copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(content);
        this.showToast('Copied to clipboard', 'success');
      });
      div.appendChild(copyBtn);
    }
  }
  
  formatAIMessage(content) {
    // Enhanced markdown-like formatting
    return content
      // Code blocks with syntax highlighting
      .replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
        const language = lang || 'plaintext';
        return `<pre class="code-block"><code class="language-${language}">${this.escapeHtml(code.trim())}</code></pre>`;
      })
      // Inline code
      .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
      // Bold
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      // Italic
      .replace(/\*([^*]+)\*/g, '<em>$1</em>')
      // Lists
      .replace(/^- (.+)$/gm, '<li>$1</li>')
      .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
      // Numbered lists
      .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
      // Links
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
      // Line breaks
      .replace(/\n/g, '<br>');
  }
  
  addAITypingIndicator() {
    const messages = document.getElementById('aiMessages');
    const id = 'typing-' + Date.now();
    
    const div = document.createElement('div');
    div.className = 'ai-message assistant';
    div.id = id;
    div.innerHTML = `
      <div class="typing-indicator">
        <span></span><span></span><span></span>
      </div>
    `;
    messages?.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
    
    return id;
  }
  
  removeAITypingIndicator(id) {
    document.getElementById(id)?.remove();
  }
  
  generateAIResponse(message) {
    // Simple response generation (would be replaced with actual AI)
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('explain') || lowerMessage.includes('what')) {
      return "I'd be happy to help explain! Based on your current context, I can see you're working with JavaScript code. The key concepts here involve asynchronous programming patterns. Would you like me to go into more detail about any specific part?";
    }
    
    if (lowerMessage.includes('refactor')) {
      return "I can suggest some refactoring improvements:\n\n1. Extract repeated logic into reusable functions\n2. Use more descriptive variable names\n3. Consider using async/await for cleaner async code\n4. Add error handling where missing\n\nWould you like me to implement any of these suggestions?";
    }
    
    if (lowerMessage.includes('bug') || lowerMessage.includes('error')) {
      return "Let me analyze the code for potential issues. I'll check for:\n\n- Null/undefined references\n- Type mismatches\n- Missing error handling\n- Logic errors\n\nCan you share the specific error message you're seeing?";
    }
    
    if (lowerMessage.includes('test')) {
      return "I can help you write tests! Based on the current file, here are the functions that should be tested:\n\n1. Main business logic functions\n2. Edge cases and error scenarios\n3. Integration with external services\n\nShall I generate test cases for any of these?";
    }
    
    return "I understand you're asking about: " + message + "\n\nI'm here to help with code review, refactoring, debugging, testing, and documentation. What specific aspect would you like me to focus on?";
  }
  
  startVoiceInput() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = false;
      recognition.interimResults = false;
      
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        const input = document.getElementById('aiInput');
        if (input) {
          input.value = transcript;
        }
      };
      
      recognition.start();
      this.showToast('Listening...', 'info');
    } else {
      this.showToast('Voice input not supported', 'warning');
    }
  }
  
  aiExplainCode() {
    const editor = document.getElementById('codeEditor');
    const selection = editor?.value.substring(editor.selectionStart, editor.selectionEnd);
    
    if (selection) {
      this.showAISidebar();
      document.getElementById('aiInput').value = `Explain this code:\n\`\`\`\n${selection}\n\`\`\``;
      this.sendAIMessage();
    } else {
      this.showAISidebar();
      document.getElementById('aiInput').value = 'Explain the current file';
      this.sendAIMessage();
    }
  }
  
  aiRefactorCode() {
    this.showAISidebar();
    document.getElementById('aiInput').value = 'Suggest refactoring improvements for this code';
    this.sendAIMessage();
  }
  
  // ===============================================
  // Context Menu
  // ===============================================
  
  initContextMenu() {
    const menu = document.getElementById('contextMenu');
    
    document.addEventListener('click', () => {
      menu?.classList.remove('visible');
    });
    
    menu?.querySelectorAll('.context-menu-item').forEach(item => {
      item.addEventListener('click', () => {
        this.handleContextAction(item.dataset.action);
        menu.classList.remove('visible');
      });
    });
  }
  
  showContextMenu(x, y) {
    const menu = document.getElementById('contextMenu');
    if (!menu) return;
    
    menu.style.left = `${x}px`;
    menu.style.top = `${y}px`;
    menu.classList.add('visible');
    
    // Adjust if off-screen
    const rect = menu.getBoundingClientRect();
    if (rect.right > window.innerWidth) {
      menu.style.left = `${x - rect.width}px`;
    }
    if (rect.bottom > window.innerHeight) {
      menu.style.top = `${y - rect.height}px`;
    }
  }
  
  handleContextAction(action) {
    const file = this.contextMenuTarget;
    if (!file && !['newFile', 'newFolder'].includes(action)) return;
    
    switch (action) {
      case 'open':
        if (file.isDirectory) {
          this.loadDirectory(file.path);
        } else {
          this.openFile(file.path);
        }
        break;
      case 'openSplit':
        this.openFile(file.path);
        break;
      case 'aiExplain':
        this.openFile(file.path).then(() => this.aiExplainCode());
        break;
      case 'aiRefactor':
        this.openFile(file.path).then(() => this.aiRefactorCode());
        break;
      case 'rename':
        this.showInputModal('Rename', 'Enter new name:', (name) => this.renameFile(file, name), file.name);
        break;
      case 'copy':
        this.clipboardFile = { ...file, operation: 'copy' };
        this.showToast(`"${file.name}" copied`, 'info');
        break;
      case 'cut':
        this.clipboardFile = { ...file, operation: 'cut' };
        this.showToast(`"${file.name}" cut`, 'info');
        break;
      case 'paste':
        if (this.clipboardFile) {
          this.pasteFile();
        } else {
          this.showToast('Nothing to paste', 'warning');
        }
        break;
      case 'delete':
        if (confirm(`Delete "${file.name}"?`)) {
          this.deleteFile(file);
        }
        break;
    }
  }
  
  async pasteFile() {
    if (!this.clipboardFile) return;
    
    const source = this.clipboardFile.path;
    const destDir = this.selectedFile?.isDirectory ? this.selectedFile.path : this.currentPath;
    const destPath = `${destDir}/${this.clipboardFile.name}`;
    
    try {
      if (this.clipboardFile.operation === 'copy') {
        // Copy file
        const response = await fetch('/api/file/copy', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ source, dest: destPath })
        });
        
        if (!response.ok) {
          // Fallback: read and write for copy
          const readRes = await fetch(`/api/file?path=${encodeURIComponent(source)}`);
          const data = await readRes.json();
          await fetch('/api/file', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: destPath, content: data.content })
          });
        }
        
        this.showToast(`"${this.clipboardFile.name}" pasted`, 'success');
      } else if (this.clipboardFile.operation === 'cut') {
        // Move file (rename)
        await fetch('/api/rename', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ oldPath: source, newPath: destPath })
        });
        this.showToast(`"${this.clipboardFile.name}" moved`, 'success');
        this.clipboardFile = null; // Clear after cut
      }
      
      this.loadDirectory(this.currentPath);
    } catch (error) {
      this.showToast('Paste failed', 'error');
    }
  }
  
  async renameFile(file, newName) {
    if (!newName || newName === file.name) return;
    
    const newPath = file.path.replace(file.name, newName);
    try {
      await fetch('/api/rename', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ oldPath: file.path, newPath })
      });
      this.showToast(`Renamed to "${newName}"`, 'success');
      this.loadDirectory(this.currentPath);
    } catch (error) {
      this.showToast('Failed to rename', 'error');
    }
  }
  
  async deleteFile(file) {
    try {
      await fetch(`/api/file?path=${encodeURIComponent(file.path)}`, { method: 'DELETE' });
      this.showToast(`"${file.name}" deleted`, 'success');
      this.loadDirectory(this.currentPath);
    } catch (error) {
      this.showToast('Failed to delete', 'error');
    }
  }
  
  // ===============================================
  // Modals
  // ===============================================
  
  initModals() {
    // Input modal
    const inputOverlay = document.getElementById('inputModalOverlay');
    const inputClose = document.getElementById('inputModalClose');
    const inputCancel = document.getElementById('inputModalCancel');
    
    inputClose?.addEventListener('click', () => this.hideInputModal());
    inputCancel?.addEventListener('click', () => this.hideInputModal());
    inputOverlay?.addEventListener('click', (e) => {
      if (e.target === inputOverlay) this.hideInputModal();
    });
    
    // Multi-agent modal
    const multiOverlay = document.getElementById('multiAgentModalOverlay');
    const multiClose = document.getElementById('multiAgentModalClose');
    const multiCancel = document.getElementById('multiAgentCancel');
    const multiStart = document.getElementById('multiAgentStart');
    
    multiClose?.addEventListener('click', () => this.hideMultiAgentModal());
    multiCancel?.addEventListener('click', () => this.hideMultiAgentModal());
    multiOverlay?.addEventListener('click', (e) => {
      if (e.target === multiOverlay) this.hideMultiAgentModal();
    });
    
    multiStart?.addEventListener('click', () => this.startOrchestration());
    
    // Multi-agent button
    document.getElementById('multiAgentBtn')?.addEventListener('click', () => {
      this.showMultiAgentModal();
    });
  }
  
  showInputModal(title, placeholder, onConfirm, defaultValue = '') {
    const overlay = document.getElementById('inputModalOverlay');
    const input = document.getElementById('inputModalInput');
    const confirmBtn = document.getElementById('inputModalConfirm');
    
    document.getElementById('inputModalTitle').textContent = title;
    input.placeholder = placeholder;
    input.value = defaultValue;
    
    overlay?.classList.add('visible');
    input?.focus();
    input?.select();
    
    // Remove any existing listeners by cloning elements
    const newConfirmBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
    
    const newInput = input.cloneNode(true);
    newInput.value = defaultValue;
    input.parentNode.replaceChild(newInput, input);
    newInput.focus();
    newInput.select();
    
    const handleConfirm = () => {
      const value = newInput.value;
      this.hideInputModal();
      onConfirm(value);
    };
    
    newConfirmBtn.addEventListener('click', handleConfirm);
    
    newInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        handleConfirm();
      } else if (e.key === 'Escape') {
        this.hideInputModal();
      }
    });
  }
  
  hideInputModal() {
    document.getElementById('inputModalOverlay')?.classList.remove('visible');
  }
  
  showMultiAgentModal() {
    const overlay = document.getElementById('multiAgentModalOverlay');
    const selection = document.getElementById('agentSelection');
    
    if (selection && window.AriaOrchestration) {
      const agents = window.AriaOrchestration.getAllAgents();
      selection.innerHTML = agents.map(agent => `
        <label class="agent-checkbox" data-id="${agent.id}">
          <input type="checkbox" value="${agent.id}">
          <div class="agent-checkbox-icon" style="background: ${agent.color}">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"/>
            </svg>
          </div>
          <span class="agent-checkbox-name">${agent.name}</span>
        </label>
      `).join('');
      
      selection.querySelectorAll('.agent-checkbox').forEach(checkbox => {
        checkbox.addEventListener('click', (e) => {
          if (e.target.tagName !== 'INPUT') {
            const input = checkbox.querySelector('input');
            input.checked = !input.checked;
          }
          checkbox.classList.toggle('selected', checkbox.querySelector('input').checked);
        });
      });
    }
    
    overlay?.classList.add('visible');
  }
  
  hideMultiAgentModal() {
    document.getElementById('multiAgentModalOverlay')?.classList.remove('visible');
  }
  
  // ===============================================
  // Find Widget
  // ===============================================
  
  initFindWidget() {
    const findWidget = document.getElementById('findWidget');
    if (!findWidget) return;
    
    // Toggle expand/replace
    const expandBtn = document.getElementById('findExpandBtn');
    const replacePart = document.getElementById('replacePart');
    expandBtn?.addEventListener('click', () => {
      replacePart.classList.toggle('visible');
      // Rotate icon
      const icon = expandBtn.querySelector('svg');
      if (replacePart.classList.contains('visible')) {
        icon.style.transform = 'rotate(90deg)';
      } else {
        icon.style.transform = 'rotate(0deg)';
      }
    });
    
    // Close button
    document.getElementById('findCloseBtn')?.addEventListener('click', () => {
      this.hideFindWidget();
    });
    
    // Find input
    const findInput = document.getElementById('findInput');
    findInput?.addEventListener('input', () => {
      this.findMatches(findInput.value);
    });
    
    findInput?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        if (e.shiftKey) {
          this.findPrevMatch();
        } else {
          this.findNextMatch();
        }
      } else if (e.key === 'Escape') {
        this.hideFindWidget();
        document.getElementById('codeEditor')?.focus();
      }
    });
    
    // Navigation buttons
    document.getElementById('findNextBtn')?.addEventListener('click', () => this.findNextMatch());
    document.getElementById('findPrevBtn')?.addEventListener('click', () => this.findPrevMatch());
    
    // Options
    document.getElementById('findCaseBtn')?.addEventListener('click', (e) => {
      e.currentTarget.classList.toggle('active');
      this.searchState.options.caseSensitive = e.currentTarget.classList.contains('active');
      this.findMatches(findInput.value);
    });
    
    document.getElementById('findWholeWordBtn')?.addEventListener('click', (e) => {
      e.currentTarget.classList.toggle('active');
      this.searchState.options.wholeWord = e.currentTarget.classList.contains('active');
      this.findMatches(findInput.value);
    });
    
    document.getElementById('findRegexBtn')?.addEventListener('click', (e) => {
      e.currentTarget.classList.toggle('active');
      this.searchState.options.useRegex = e.currentTarget.classList.contains('active');
      this.findMatches(findInput.value);
    });
    
    // Replace
    const replaceInput = document.getElementById('replaceInput');
    replaceInput?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        this.replaceMatch();
      }
    });
    
    document.getElementById('replaceBtn')?.addEventListener('click', () => this.replaceMatch());
    document.getElementById('replaceAllBtn')?.addEventListener('click', () => this.replaceAllMatches());
  }
  
  showFindWidget() {
    const widget = document.getElementById('findWidget');
    if (widget) {
      widget.classList.add('visible');
      this.findWidgetVisible = true;
      const input = document.getElementById('findInput');
      input?.focus();
      if (input?.value) {
        input.select();
        this.findMatches(input.value);
      }
    }
  }
  
  hideFindWidget() {
    const widget = document.getElementById('findWidget');
    if (widget) {
      widget.classList.remove('visible');
      this.findWidgetVisible = false;
      this.clearSearchHighlights();
    }
  }
  
  findMatches(query) {
    this.searchState.query = query;
    this.searchState.matches = [];
    this.searchState.currentMatchIndex = -1;
    
    const editor = document.getElementById('codeEditor');
    if (!editor || !query) {
      this.updateFindStatus();
      this.clearSearchHighlights();
      return;
    }
    
    const content = editor.value;
    let flags = 'g';
    if (!this.searchState.options.caseSensitive) flags += 'i';
    
    try {
      let regex;
      if (this.searchState.options.useRegex) {
        regex = new RegExp(query, flags);
      } else {
        // Escape regex characters
        const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        if (this.searchState.options.wholeWord) {
          regex = new RegExp(`\\b${escaped}\\b`, flags);
        } else {
          regex = new RegExp(escaped, flags);
        }
      }
      
      let match;
      while ((match = regex.exec(content)) !== null) {
        this.searchState.matches.push({
          start: match.index,
          end: match.index + match[0].length,
          text: match[0]
        });
      }
      
      if (this.searchState.matches.length > 0) {
        this.searchState.currentMatchIndex = 0;
        this.highlightMatches();
        this.scrollToMatch(0);
      } else {
        this.clearSearchHighlights();
      }
      
      this.updateFindStatus();
      
    } catch (e) {
      console.error('Invalid regex', e);
      document.getElementById('findMatches').textContent = 'Invalid regex';
    }
  }
  
  findNextMatch() {
    if (this.searchState.matches.length === 0) return;
    
    this.searchState.currentMatchIndex = (this.searchState.currentMatchIndex + 1) % this.searchState.matches.length;
    this.highlightMatches(); // Update current selection style
    this.scrollToMatch(this.searchState.currentMatchIndex);
    this.updateFindStatus();
  }
  
  findPrevMatch() {
    if (this.searchState.matches.length === 0) return;
    
    this.searchState.currentMatchIndex = (this.searchState.currentMatchIndex - 1 + this.searchState.matches.length) % this.searchState.matches.length;
    this.highlightMatches();
    this.scrollToMatch(this.searchState.currentMatchIndex);
    this.updateFindStatus();
  }
  
  replaceMatch() {
    if (this.searchState.matches.length === 0 || this.searchState.currentMatchIndex === -1) return;
    
    const editor = document.getElementById('codeEditor');
    const replaceText = document.getElementById('replaceInput').value;
    const match = this.searchState.matches[this.searchState.currentMatchIndex];
    
    // Save undo state
    this.undoStack.push({
      value: editor.value,
      selectionStart: editor.selectionStart,
      selectionEnd: editor.selectionEnd
    });
    
    editor.value = editor.value.substring(0, match.start) + replaceText + editor.value.substring(match.end);
    
    // Update editor
    this.updateLineNumbers();
    this.updateSyntaxHighlighting(editor.value);
    
    // Re-run search
    this.findMatches(this.searchState.query);
  }
  
  replaceAllMatches() {
    if (this.searchState.matches.length === 0) return;
    
    const editor = document.getElementById('codeEditor');
    const replaceText = document.getElementById('replaceInput').value;
    const query = this.searchState.query;
    
    // Save undo state
    this.undoStack.push({
      value: editor.value,
      selectionStart: editor.selectionStart,
      selectionEnd: editor.selectionEnd
    });
    
    let content = editor.value;
    let flags = 'g';
    if (!this.searchState.options.caseSensitive) flags += 'i';
    
    let regex;
    if (this.searchState.options.useRegex) {
      regex = new RegExp(query, flags);
    } else {
      const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      if (this.searchState.options.wholeWord) {
        regex = new RegExp(`\\b${escaped}\\b`, flags);
      } else {
        regex = new RegExp(escaped, flags);
      }
    }
    
    editor.value = content.replace(regex, replaceText);
    
    this.updateLineNumbers();
    this.updateSyntaxHighlighting(editor.value);
    this.findMatches(query);
  }
  
  updateFindStatus() {
    const el = document.getElementById('findMatches');
    const count = this.searchState.matches.length;
    if (count === 0) {
      el.textContent = 'No results';
    } else {
      el.textContent = `${this.searchState.currentMatchIndex + 1} of ${count}`;
    }
  }
  
  highlightMatches() {
    if (this.searchState.currentMatchIndex !== -1) {
      const editor = document.getElementById('codeEditor');
      const match = this.searchState.matches[this.searchState.currentMatchIndex];
      
      editor.selectionStart = match.start;
      editor.selectionEnd = match.end;
      editor.focus();
    }
  }
  
  scrollToMatch(index) {
    const editor = document.getElementById('codeEditor');
    editor.blur();
    editor.focus();
  }
  
  clearSearchHighlights() {
    this.searchState.matches = [];
    this.searchState.currentMatchIndex = -1;
  }
  
  async startOrchestration() {
    const selection = document.getElementById('agentSelection');
    const taskInput = document.getElementById('orchestrationTask');
    
    const selectedAgents = Array.from(selection?.querySelectorAll('input:checked') || [])
      .map(input => input.value);
    
    const task = taskInput?.value.trim();
    
    if (selectedAgents.length === 0) {
      this.showToast('Please select at least one agent', 'warning');
      return;
    }
    
    if (!task) {
      this.showToast('Please enter a task description', 'warning');
      return;
    }
    
    this.hideMultiAgentModal();
    this.showToast('Starting orchestration...', 'info');
    
    if (window.AriaOrchestration) {
      try {
        const result = await window.AriaOrchestration.orchestrate(selectedAgents, task);
        this.showToast('Orchestration completed!', 'success');
        console.log('Orchestration result:', result);
      } catch (error) {
        this.showToast('Orchestration failed', 'error');
      }
    }
  }
  
  // ===============================================
  // Keyboard Shortcuts
  // ===============================================
  
  initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Command Palette: Ctrl+Shift+P
      if (e.ctrlKey && e.shiftKey && e.key === 'P') {
        e.preventDefault();
        this.showCommandPalette();
      }
      
      // Quick Open Files: Ctrl+P
      if (e.ctrlKey && !e.shiftKey && e.key === 'p') {
        e.preventDefault();
        this.showRecentFiles();
      }
      
      // AI Chat: Ctrl+/
      if (e.ctrlKey && e.key === '/') {
        e.preventDefault();
        this.toggleAISidebar();
      }
      
      // Keyboard Shortcuts Help: Ctrl+?
      if (e.ctrlKey && e.key === '?') {
        e.preventDefault();
        this.showShortcutsModal();
      }
      
      // Save: Ctrl+S
      if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        this.saveFile();
      }
      
      // Toggle Terminal: Ctrl+`
      if (e.ctrlKey && e.key === '`') {
        e.preventDefault();
        this.toggleTerminal();
      }
      
      // Toggle Sidebar: Ctrl+B
      if (e.ctrlKey && e.key === 'b') {
        e.preventDefault();
        document.getElementById('sidebar')?.classList.toggle('collapsed');
      }
      
      // Explorer: Ctrl+Shift+E
      if (e.ctrlKey && e.shiftKey && e.key === 'E') {
        e.preventDefault();
        this.switchView('explorer');
      }
      
      // Search: Ctrl+Shift+F
      if (e.ctrlKey && e.shiftKey && e.key === 'F') {
        e.preventDefault();
        this.switchView('search');
        document.getElementById('globalSearchInput')?.focus();
      }
      
      // Git: Ctrl+Shift+G
      if (e.ctrlKey && e.shiftKey && e.key === 'G') {
        e.preventDefault();
        this.switchView('git');
      }
      
      // Escape
      if (e.key === 'Escape') {
        if (this.commandPaletteVisible) {
          this.hideCommandPalette();
        } else if (this.aiSidebarVisible) {
          this.hideAISidebar();
        } else if (this.recentFilesVisible) {
          this.hideRecentFiles();
        } else {
          this.hideShortcutsModal();
        }
      }
    });
    
    // Init shortcuts modal close button
    document.getElementById('shortcutsModalClose')?.addEventListener('click', () => {
      this.hideShortcutsModal();
    });
    
    document.getElementById('shortcutsModalOverlay')?.addEventListener('click', (e) => {
      if (e.target.id === 'shortcutsModalOverlay') {
        this.hideShortcutsModal();
      }
    });
  }
  
  // Recent Files Panel
  showRecentFiles() {
    const panel = document.getElementById('recentFilesPanel');
    const list = document.getElementById('recentFilesList');
    const search = document.getElementById('recentFilesSearch');
    
    if (!panel || !list) return;
    
    // Get recent files from memory
    let recentFiles = [];
    if (window.AriaMemory) {
      recentFiles = window.AriaMemory.getRecentFiles(20);
    }
    
    // Add currently open files
    const openFilePaths = Array.from(this.openFiles.keys());
    
    // Render files
    this.renderRecentFiles(recentFiles);
    
    panel.classList.add('visible');
    this.recentFilesVisible = true;
    
    if (search) {
      search.value = '';
      search.focus();
      
      // Search filter
      search.addEventListener('input', () => {
        const query = search.value.toLowerCase();
        const filtered = recentFiles.filter(f => 
          f.path.toLowerCase().includes(query)
        );
        this.renderRecentFiles(filtered);
      });
      
      // Keyboard navigation
      search.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          const firstItem = list.querySelector('.recent-file-item');
          if (firstItem) {
            this.openFile(firstItem.dataset.path);
            this.hideRecentFiles();
          }
        }
      });
    }
  }
  
  renderRecentFiles(files) {
    const list = document.getElementById('recentFilesList');
    if (!list) return;
    
    if (files.length === 0) {
      list.innerHTML = '<div class="no-recent-files">No recent files</div>';
      return;
    }
    
    list.innerHTML = files.map(f => {
      const fileName = f.path.split('/').pop();
      const dirPath = f.path.replace('/' + fileName, '');
      const shortPath = dirPath.replace(/^\/home\/dev/, '~');
      
      return `
        <div class="recent-file-item" data-path="${f.path}">
          <div class="recent-file-icon">
            ${this.getFileIcon({ name: fileName, isDirectory: false }).svg}
          </div>
          <div class="recent-file-info">
            <span class="recent-file-name">${fileName}</span>
            <span class="recent-file-path">${shortPath}</span>
          </div>
          <div class="recent-file-time">${this.formatTimeAgo(f.lastOpened)}</div>
        </div>
      `;
    }).join('');
    
    // Add click handlers
    list.querySelectorAll('.recent-file-item').forEach(item => {
      item.addEventListener('click', () => {
        this.openFile(item.dataset.path);
        this.hideRecentFiles();
      });
    });
  }
  
  formatTimeAgo(timestamp) {
    const now = Date.now();
    const diff = now - timestamp;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  }
  
  hideRecentFiles() {
    document.getElementById('recentFilesPanel')?.classList.remove('visible');
    this.recentFilesVisible = false;
  }
  
  // Shortcuts Modal
  showShortcutsModal() {
    document.getElementById('shortcutsModalOverlay')?.classList.add('visible');
  }
  
  hideShortcutsModal() {
    document.getElementById('shortcutsModalOverlay')?.classList.remove('visible');
  }
  
  // Drag and Drop File Support
  initDragAndDrop() {
    const app = document.getElementById('app');
    
    // Create overlay if it doesn't exist
    let overlay = document.querySelector('.drag-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.className = 'drag-overlay';
      overlay.innerHTML = `
        <div class="drag-overlay-content">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          <h3>Drop files here</h3>
          <p>to add them to your workspace</p>
        </div>
      `;
      document.body.appendChild(overlay);
      
      // Click to dismiss in case it gets stuck
      overlay.addEventListener('click', () => {
        overlay.classList.remove('visible');
        this.isDragging = false;
      });
    }
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      document.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
      });
    });
    
    // Highlight drop zone
    document.addEventListener('dragenter', (e) => {
      // Only show if dragging files
      if (e.dataTransfer.types && Array.from(e.dataTransfer.types).includes('Files')) {
        if (!this.isDragging) {
          this.isDragging = true;
          overlay.classList.add('visible');
        }
      }
    });
    
    overlay.addEventListener('dragleave', (e) => {
      // Only remove if leaving the window/overlay
      if (e.relatedTarget === null) {
        this.isDragging = false;
        overlay.classList.remove('visible');
      }
    });
    
    // Handle drop
    document.addEventListener('drop', (e) => {
      this.isDragging = false;
      overlay.classList.remove('visible');
      
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        this.handleFiles(files);
      }
    });
  }
  
  async handleFiles(files) {
    if (!files || files.length === 0) return;
    
    this.showToast(`Uploading ${files.length} file(s)...`, 'info');
    
    for (const file of Array.from(files)) {
      try {
        const content = await this.readFileContent(file);
        const filePath = `${this.currentPath}/${file.name}`;
        
        await fetch('/api/file', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ path: filePath, content })
        });
      } catch (error) {
        console.error('Failed to upload file:', file.name, error);
        this.showToast(`Failed to upload ${file.name}`, 'error');
      }
    }
    
    this.showToast(`Uploaded ${files.length} file(s)`, 'success');
    this.loadDirectory(this.currentPath);
  }
  
  readFileContent(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = (e) => reject(e);
      reader.readAsText(file);
    });
  }
  
  readFileContent(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsText(file);
    });
  }
  
  // ===============================================
  // Resizer
  // ===============================================
  
  initResizer() {
    const resizer = document.getElementById('resizer');
    const sidebar = document.getElementById('sidebar');
    
    if (!resizer || !sidebar) return;
    
    resizer.addEventListener('mousedown', () => {
      this.isDragging = true;
      resizer.classList.add('dragging');
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    });
    
    document.addEventListener('mousemove', (e) => {
      if (!this.isDragging) return;
      
      const newWidth = e.clientX - 48; // Account for activity bar
      if (newWidth >= 200 && newWidth <= 500) {
        sidebar.style.width = `${newWidth}px`;
      }
    });
    
    document.addEventListener('mouseup', () => {
      if (this.isDragging) {
        this.isDragging = false;
        resizer.classList.remove('dragging');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        this.fitAddon?.fit();
      }
    });
    
    // Terminal height resizer
    this.initTerminalResizer();
  }
  
  initTerminalResizer() {
    const terminalWrapper = document.getElementById('terminalWrapper');
    const terminalHeader = terminalWrapper?.querySelector('.terminal-header');
    
    if (!terminalWrapper || !terminalHeader) return;
    
    let isResizingTerminal = false;
    let startY = 0;
    let startHeight = 0;
    
    // Make terminal header draggable for resizing
    terminalHeader.addEventListener('mousedown', (e) => {
      // Only resize if clicking on the header background (not buttons)
      if (e.target.closest('button')) return;
      
      isResizingTerminal = true;
      startY = e.clientY;
      startHeight = terminalWrapper.offsetHeight;
      document.body.style.cursor = 'ns-resize';
      document.body.style.userSelect = 'none';
      terminalHeader.classList.add('resizing');
    });
    
    document.addEventListener('mousemove', (e) => {
      if (!isResizingTerminal) return;
      
      const delta = startY - e.clientY;
      const newHeight = Math.min(Math.max(startHeight + delta, 100), window.innerHeight * 0.8);
      terminalWrapper.style.height = `${newHeight}px`;
    });
    
    document.addEventListener('mouseup', () => {
      if (isResizingTerminal) {
        isResizingTerminal = false;
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        terminalHeader.classList.remove('resizing');
        this.fitAddon?.fit();
      }
    });
  }
  
  // ===============================================
  // Status Bar & System Monitor
  // ===============================================
  
  initStatusBar() {
    setInterval(() => {
      const now = new Date();
      const time = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
      const statusTime = document.getElementById('statusTime');
      if (statusTime) statusTime.textContent = time;
    }, 1000);
  }
  
  async loadSystemInfo() {
    try {
      const response = await fetch('/api/system');
      const info = await response.json();
      this.currentPath = info.cwd;
      
      if (window.AriaMemory) {
        window.AriaMemory.setCurrentProject(info.cwd);
      }
    } catch (error) {
      console.error('Failed to load system info:', error);
    }
  }
  
  startSystemMonitor() {
    this.updateSystemStats();
    setInterval(() => this.updateSystemStats(), 5000);
  }
  
  async updateSystemStats() {
    try {
      const response = await fetch('/api/system/realtime');
      const data = await response.json();
      
      // Status bar
      document.getElementById('statusCpu').innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="4" y="4" width="16" height="16" rx="2"/>
          <rect x="9" y="9" width="6" height="6"/>
        </svg>
        ${data.cpuUsage}%
      `;
      
      document.getElementById('statusMemory').innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <line x1="3" y1="9" x2="21" y2="9"/>
        </svg>
        ${data.memory.percentage}%
      `;
      
      // Sidebar metrics
      document.getElementById('sidebarCpu').textContent = `${data.cpuUsage}%`;
      document.getElementById('sidebarMemory').textContent = `${data.memory.percentage}%`;
      
      const cpuBar = document.getElementById('sidebarCpuBar');
      const memBar = document.getElementById('sidebarMemoryBar');
      if (cpuBar) cpuBar.style.width = `${data.cpuUsage}%`;
      if (memBar) memBar.style.width = `${data.memory.percentage}%`;
      
    } catch (error) {
      // Silently fail
    }
  }
  
  async loadSystemDetails() {
    try {
      const response = await fetch('/api/system');
      const info = await response.json();
      
      const details = document.getElementById('systemDetails');
      if (details) {
        details.innerHTML = `
          <div class="system-detail-item">
            <span class="detail-label">Platform</span>
            <span class="detail-value">${info.platform}</span>
          </div>
          <div class="system-detail-item">
            <span class="detail-label">Architecture</span>
            <span class="detail-value">${info.arch}</span>
          </div>
          <div class="system-detail-item">
            <span class="detail-label">Node Version</span>
            <span class="detail-value">${info.nodeVersion}</span>
          </div>
          <div class="system-detail-item">
            <span class="detail-label">Uptime</span>
            <span class="detail-value">${info.uptime.formatted}</span>
          </div>
        `;
      }
      
      document.getElementById('sidebarDisk').textContent = `${info.disk.percentage}%`;
      const diskBar = document.getElementById('sidebarDiskBar');
      if (diskBar) diskBar.style.width = `${info.disk.percentage}%`;
      
    } catch (error) {
      console.error('Failed to load system details:', error);
    }
  }
  
  // ===============================================
  // Git
  // ===============================================
  
  async loadGitInfo() {
    try {
      const response = await fetch(`/api/git/status?path=${encodeURIComponent(this.currentPath)}`);
      const info = await response.json();
      
      if (info.branch) {
        document.getElementById('currentBranch').textContent = info.branch;
        document.getElementById('statusBranch').innerHTML = `
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="18" cy="18" r="3"/>
            <circle cx="6" cy="6" r="3"/>
            <path d="M13 6h3a2 2 0 0 1 2 2v7"/>
            <line x1="6" y1="9" x2="6" y2="21"/>
          </svg>
          ${info.branch}
        `;
        
        const badge = document.getElementById('gitBadge');
        if (badge) badge.textContent = info.changes || '0';
      }
    } catch (error) {
      document.getElementById('currentBranch').textContent = 'Not a git repo';
    }
  }
  
  async gitCommit() {
    const message = document.getElementById('commitMessage')?.value.trim();
    if (!message) {
      this.showToast('Please enter a commit message', 'warning');
      return;
    }
    
    try {
      await this.runCommand('git add .');
      await this.runCommand(`git commit -m "${message}"`);
      document.getElementById('commitMessage').value = '';
      this.showToast('Committed successfully', 'success');
      this.loadGitInfo();
    } catch (error) {
      this.showToast('Commit failed', 'error');
    }
  }
  
  async runCommand(command) {
    const response = await fetch('/api/automation/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command, cwd: this.currentPath })
    });
    return await response.json();
  }
  
  // ===============================================
  // Docker
  // ===============================================
  
  async loadDockerInfo() {
    try {
      const containersRes = await fetch('/api/docker/containers');
      const containersData = await containersRes.json();
      
      const containersList = document.getElementById('dockerContainersList');
      if (containersList) {
        if (containersData.containers.length === 0) {
          containersList.innerHTML = '<div class="loading-spinner"><span>No running containers</span></div>';
        } else {
          containersList.innerHTML = containersData.containers.map(c => `
            <div class="docker-item running">
              <div class="docker-item-name">${c.name}</div>
              <div class="docker-item-meta">${c.image}</div>
            </div>
          `).join('');
        }
      }
      
      const imagesRes = await fetch('/api/docker/images');
      const imagesData = await imagesRes.json();
      
      const imagesList = document.getElementById('dockerImagesList');
      if (imagesList) {
        if (imagesData.images.length === 0) {
          imagesList.innerHTML = '<div class="loading-spinner"><span>No images</span></div>';
        } else {
          imagesList.innerHTML = imagesData.images.slice(0, 5).map(i => `
            <div class="docker-item">
              <div class="docker-item-name">${i.repository}:${i.tag}</div>
              <div class="docker-item-meta">${i.size}</div>
            </div>
          `).join('');
        }
      }
    } catch (error) {
      const containersList = document.getElementById('dockerContainersList');
      if (containersList) {
        containersList.innerHTML = '<div class="loading-spinner"><span>Docker not available</span></div>';
      }
    }
  }
  
  // ===============================================
  // Agents & Workflows
  // ===============================================
  
  loadAgents() {
    if (!window.AriaOrchestration) return;
    
    const agents = window.AriaOrchestration.getAllAgents();
    const list = document.getElementById('agentsList');
    
    if (list) {
      list.innerHTML = agents.map(agent => `
        <div class="agent-card" data-id="${agent.id}">
          <div class="agent-card-header">
            <div class="agent-icon" style="background: ${agent.color}">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"/>
              </svg>
            </div>
            <span class="agent-name">${agent.name}</span>
          </div>
          <p class="agent-description">${agent.description}</p>
        </div>
      `).join('');
      
      list.querySelectorAll('.agent-card').forEach(card => {
        card.addEventListener('click', () => {
          list.querySelectorAll('.agent-card').forEach(c => c.classList.remove('active'));
          card.classList.add('active');
          
          const agentId = card.dataset.id;
          this.selectAgent(agentId);
        });
      });
    }
  }
  
  selectAgent(agentId) {
    if (!window.AriaOrchestration) return;
    
    const agent = window.AriaOrchestration.getAgent(agentId);
    if (agent) {
      this.showAISidebar();
      document.getElementById('aiStatusText').textContent = `${agent.name} ready`;
    }
  }
  
  loadWorkflows() {
    if (!window.AriaOrchestration) return;
    
    const workflows = window.AriaOrchestration.getAllWorkflows();
    const list = document.getElementById('workflowsList');
    
    if (list) {
      list.innerHTML = workflows.map(workflow => `
        <div class="workflow-card" data-id="${workflow.id}">
          <div class="workflow-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
          </div>
          <div class="workflow-info">
            <div class="workflow-name">${workflow.name}</div>
            <div class="workflow-meta">${workflow.steps.length} steps</div>
          </div>
          <button class="workflow-toggle ${workflow.enabled ? 'enabled' : ''}"></button>
        </div>
      `).join('');
      
      list.querySelectorAll('.workflow-card').forEach(card => {
        card.addEventListener('click', () => {
          const workflowId = card.dataset.id;
          this.runWorkflow(workflowId);
        });
        
        card.querySelector('.workflow-toggle')?.addEventListener('click', (e) => {
          e.stopPropagation();
          const workflowId = card.dataset.id;
          window.AriaOrchestration?.toggleWorkflow(workflowId);
          this.loadWorkflows();
        });
      });
    }
    
    // Update header badge
    const activeWorkflows = document.getElementById('activeWorkflows');
    if (activeWorkflows) {
      activeWorkflows.textContent = workflows.filter(w => w.enabled).length;
    }
  }
  
  async runWorkflow(workflowId) {
    if (!window.AriaOrchestration) return;
    
    this.showToast('Running workflow...', 'info');
    
    try {
      const results = await window.AriaOrchestration.runWorkflow(workflowId);
      this.showToast('Workflow completed', 'success');
      console.log('Workflow results:', results);
    } catch (error) {
      this.showToast('Workflow failed', 'error');
    }
  }
  
  // ===============================================
  // Insights
  // ===============================================
  
  toggleInsights() {
    const panel = document.getElementById('insightsPanel');
    panel?.classList.toggle('visible');
    
    if (panel?.classList.contains('visible')) {
      this.loadInsights();
    }
  }
  
  async loadInsights() {
    const content = document.getElementById('insightsContent');
    if (!content) return;
    
    content.innerHTML = '<div class="loading-spinner"><div class="spinner"></div><span>Analyzing project...</span></div>';
    
    if (window.AriaOrchestration) {
      const insights = await window.AriaOrchestration.analyzeProject(this.currentPath);
      
      content.innerHTML = `
        <div class="insights-section">
          <h4>Project Structure</h4>
          <div class="insight-stat">
            <span>Total Files</span>
            <span>${insights.structure.totalFiles || 0}</span>
          </div>
          <div class="insight-stat">
            <span>Total Folders</span>
            <span>${insights.structure.totalFolders || 0}</span>
          </div>
        </div>
        
        <div class="insights-section">
          <h4>Suggestions</h4>
          ${insights.suggestions.length > 0 
            ? insights.suggestions.map(s => `
              <div class="insight-suggestion ${s.priority}">
                <strong>${s.priority.toUpperCase()}</strong>: ${s.message}
              </div>
            `).join('')
            : '<p>No suggestions at this time.</p>'
          }
        </div>
      `;
    }
    
    document.getElementById('insightsClose')?.addEventListener('click', () => {
      this.toggleInsights();
    });
  }
  
  // ===============================================
  // Toast Notifications
  // ===============================================
  
  showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
      success: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>',
      error: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
      warning: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
      info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
    };
    
    toast.innerHTML = `
      <span class="toast-icon">${icons[type]}</span>
      <span class="toast-content">${message}</span>
      <button class="toast-close">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    `;
    
    toast.querySelector('.toast-close')?.addEventListener('click', () => {
      toast.classList.add('removing');
      setTimeout(() => toast.remove(), 300);
    });
    
    container.appendChild(toast);
    
    setTimeout(() => {
      toast.classList.add('removing');
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.app = new ARIAUI();
});
