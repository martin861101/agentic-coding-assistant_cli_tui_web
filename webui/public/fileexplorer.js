// ===============================================
// ARIA - File Explorer Module
// Extracted from app.js - File browsing functionality
// ===============================================

class FileExplorerModule {
  constructor(app) {
    this.app = app;
    this.currentPath = '';
    this.selectedFile = null;
    this.clipboardFile = null;
    this.clipboardAction = null; // 'copy' or 'cut'
  }

  init() {
    // File explorer actions
    document.getElementById('newFileBtn')?.addEventListener('click', () => {
      this.app.showInputModal('New File', 'Enter filename:', (name) => this.createFile(name));
    });

    document.getElementById('newFolderBtn')?.addEventListener('click', () => {
      this.app.showInputModal('New Folder', 'Enter folder name:', (name) => this.createFolder(name));
    });

    document.getElementById('refreshBtn')?.addEventListener('click', () => {
      this.loadDirectory(this.currentPath);
    });

    document.getElementById('collapseAllBtn')?.addEventListener('click', () => {
      document.querySelectorAll('.file-item.directory.expanded').forEach(dir => {
        dir.classList.remove('expanded');
      });
    });

    // Load initial directory
    this.loadDirectory(this.currentPath);
  }

  async loadDirectory(path) {
    const fileTree = document.getElementById('fileTree');
    if (!fileTree) return;

    try {
      fileTree.innerHTML = '<div class="loading-spinner"><div class="spinner"></div><span>Loading files...</span></div>';

      const response = await fetch(`/api/files?path=${encodeURIComponent(path)}`);
      const data = await response.json();

      this.currentPath = data.path;
      this.app.currentPath = data.path;
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

      this.app.loadGitInfo();

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
      this.selectFile(item, file);
    });

    item.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      this.app.contextMenuTarget = file;
      this.app.showContextMenu(e.clientX, e.clientY);
    });

    return item;
  }

  selectFile(item, file) {
    document.querySelectorAll('.file-item.selected').forEach(el => el.classList.remove('selected'));
    item.classList.add('selected');
    this.selectedFile = file;

    if (file.isDirectory) {
      this.loadDirectory(file.path);
    } else {
      this.app.openFile(file.path);
    }
  }

  getFileIcon(file) {
    if (file.isDirectory) {
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
      '.gitignore': { class: 'git', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.44 9.8 8.2 11.38.6.11.82-.26.82-.58v-2.03c-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.09-.75.08-.73.08-.73 1.21.08 1.84 1.24 1.84 1.24 1.07 1.84 2.81 1.31 3.5 1 .11-.78.42-1.31.76-1.61-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.12-.3-.54-1.52.12-3.18 0 0 1.01-.32 3.3 1.23.96-.27 1.98-.4 3-.4s2.04.14 3 .4c2.28-1.55 3.29-1.23 3.29-1.23.66 1.66.24 2.88.12 3.18.77.84 1.24 1.91 1.24 3.22 0 4.61-2.81 5.63-5.48 5.92.43.37.81 1.1.81 2.22v3.29c0 .32.21.69.82.57C20.56 21.8 24 17.3 24 12c0-6.63-5.37-12-12-12z"/></svg>' },
      'dockerfile': { class: 'docker', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M13 4h3v3h-3zM9 4h3v3H9zM5 4h3v3H5zM9 0h3v3H9zM22 9c-.5-.4-1.6-.6-2.4-.4-.2-1.4-1-2.6-2.1-3.4l-.4-.3-.3.4c-.4.6-.6 1.3-.6 2 0 .7.1 1.4.5 2-.7.4-2 .5-2.4.5H.3l-.1.5c-.2 1.5 0 3 .6 4.4.8 1.5 2 2.6 3.6 3.2 1.8.7 3.8.8 5.8.5 1.5-.2 3-.6 4.3-1.4 1.1-.7 2-1.5 2.8-2.6.7-.9 1.2-2 1.6-3.2h.1c1 0 1.6-.4 2-.8.3-.2.5-.6.6-.9l.1-.4-.4-.3z"/></svg>' },
      '.env': { class: 'env', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 6c1.4 0 2.8 1.1 2.8 2.5V11c.6 0 1.2.6 1.2 1.2v3.5c0 .7-.5 1.3-1.2 1.3H9.2c-.7 0-1.2-.6-1.2-1.2v-3.5c0-.7.5-1.3 1.2-1.3V9.5C9.2 8.1 10.6 7 12 7zm0 1.2c-.8 0-1.5.7-1.5 1.5V11h3V9.7c0-.8-.7-1.5-1.5-1.5z"/></svg>' },
      'readme.md': { class: 'readme', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L4 5v6.09c0 5.05 3.41 9.76 8 10.91 4.59-1.15 8-5.86 8-10.91V5l-8-3zm-1 15h2v2h-2v-2zm0-8h2v6h-2V9z"/></svg>' }
    };

    if (specialFiles[fileName]) {
      return specialFiles[fileName];
    }

    const icons = {
      js: { class: 'js', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h18v18H3V3m4.73 15.04c.4.85 1.19 1.55 2.54 1.55 1.5 0 2.53-.8 2.53-2.55v-5.78h-1.7V17c0 .86-.35 1.08-.9 1.08-.58 0-.82-.4-1.09-.87l-1.38.83z"/></svg>' },
      ts: { class: 'ts', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h18v18H3V3m10.71 13.47c.5.98 1.51 1.73 3.09 1.73 1.6 0 2.8-.83 2.8-2.36 0-1.41-.81-2.04-2.25-2.66z"/></svg>' },
      py: { class: 'py', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M9.585 11.692h4.328s2.432.039 2.432-2.35V5.391S16.714 3 11.936 3C7.362 3 7.647 4.983 7.647 4.983l.006 2.055h4.363v.617H5.92S3 7.283 3 11.692z"/></svg>' },
      go: { class: 'go', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M1.811 10.231c-.047 0-.058-.023-.035-.059l.246-.315c.023-.035.081-.058.128-.058h4.172z"/></svg>' },
      json: { class: 'json', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5 3h2v2H5v5a2 2 0 0 1-2 2 2 2 0 0 1 2 2v5h2v2H5c-1.07-.27-2-.9-2-2v-4a2 2 0 0 0-2-2H0v-2h1a2 2 0 0 0 2-2V5a2 2 0 0 1 2-2z"/></svg>' },
      md: { class: 'md', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.56 18H3.44A1.44 1.44 0 0 1 2 16.56V7.44A1.44 1.44 0 0 1 3.44 6h17.12A1.44 1.44 0 0 1 22 7.44v9.12A1.44 1.44 0 0 1 20.56 18z"/></svg>' },
      html: { class: 'html', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 17.56L16.07 16.43L16.62 10.33H9.38L9.2 8.3H16.8L17 6.31H7L7.56 12.32H14.45L14.22 14.9L12 15.5L9.78 14.9z"/></svg>' },
      css: { class: 'css', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5 3L4.35 6.34H17.94L17.5 8.5H3.92L3.26 11.83H16.85L16.09 15.64L10.61 17.45L5.86 15.64L6.19 14H2.85L2.06 18L9.91 21L18.96 18L20.16 11.97z"/></svg>' },
      sh: { class: 'shell', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5 3h14c1.1 0 2 .9 2 2v14c0 1.1-.9 2-2 2H5c-1.1 0-2-.9-2-2V5c0-1.1.9-2 2-2zm1 4l5 4-5 4v-2l3-2-3-2V7zm6 6h6v2h-6v-2z"/></svg>' },
      png: { class: 'image', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>' },
      jpg: { class: 'image', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>' }
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

  async createFile(name) {
    if (!name) return;

    const filePath = `${this.currentPath}/${name}`;
    try {
      await fetch('/api/file', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: filePath, content: '' })
      });
      this.app.showToast(`File "${name}" created`, 'success');
      this.loadDirectory(this.currentPath);
    } catch (error) {
      this.app.showToast('Failed to create file', 'error');
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
      this.app.showToast(`Folder "${name}" created`, 'success');
      this.loadDirectory(this.currentPath);
    } catch (error) {
      this.app.showToast('Failed to create folder', 'error');
    }
  }

  async deleteFile(path) {
    try {
      await fetch('/api/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path })
      });
      this.app.showToast('Deleted successfully', 'success');
      this.loadDirectory(this.currentPath);
    } catch (error) {
      this.app.showToast('Failed to delete', 'error');
    }
  }

  async renameFile(oldPath, newName) {
    const dir = oldPath.substring(0, oldPath.lastIndexOf('/'));
    const newPath = `${dir}/${newName}`;
    
    try {
      await fetch('/api/rename', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ oldPath, newPath })
      });
      this.app.showToast('Renamed successfully', 'success');
      this.loadDirectory(this.currentPath);
    } catch (error) {
      this.app.showToast('Failed to rename', 'error');
    }
  }

  copyFile(path) {
    this.clipboardFile = path;
    this.clipboardAction = 'copy';
    this.app.showToast('Copied to clipboard', 'info');
  }

  cutFile(path) {
    this.clipboardFile = path;
    this.clipboardAction = 'cut';
    this.app.showToast('Cut to clipboard', 'info');
  }

  async pasteFile() {
    if (!this.clipboardFile) {
      this.app.showToast('Nothing to paste', 'warning');
      return;
    }

    const fileName = this.clipboardFile.split('/').pop();
    const destPath = `${this.currentPath}/${fileName}`;

    try {
      await fetch('/api/copy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source: this.clipboardFile,
          destination: destPath,
          move: this.clipboardAction === 'cut'
        })
      });

      this.app.showToast(this.clipboardAction === 'cut' ? 'Moved successfully' : 'Copied successfully', 'success');
      
      if (this.clipboardAction === 'cut') {
        this.clipboardFile = null;
        this.clipboardAction = null;
      }

      this.loadDirectory(this.currentPath);
    } catch (error) {
      this.app.showToast('Paste failed', 'error');
    }
  }
}

// Export for use in main app
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FileExplorerModule;
} else {
  window.FileExplorerModule = FileExplorerModule;
}
