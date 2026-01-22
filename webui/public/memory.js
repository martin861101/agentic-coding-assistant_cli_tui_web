// ===============================================
// ARIA Memory System - Synthetic Intelligence Core
// Persistent context, preferences, and pattern learning
// ===============================================

class MemorySystem {
  constructor() {
    this.storageKey = 'aria_memory';
    this.sessionKey = 'aria_session';
    this.maxMemoryItems = 1000;
    this.maxContextWindow = 50;
    
    // Memory categories
    this.memory = {
      user: {
        preferences: {},
        shortcuts: [],
        frequentFiles: [],
        frequentCommands: [],
        workPatterns: {}
      },
      code: {
        recentEdits: [],
        patterns: [],
        symbols: {},
        dependencies: {}
      },
      context: {
        currentProject: null,
        recentConversations: [],
        taskHistory: [],
        errorPatterns: []
      },
      learning: {
        codeStylePreferences: {},
        namingConventions: {},
        architecturePatterns: [],
        frequentRefactors: []
      }
    };
    
    // Session-specific context (not persisted long-term)
    this.session = {
      startTime: Date.now(),
      activeFiles: [],
      searchHistory: [],
      commandHistory: [],
      aiConversation: [],
      currentContext: null,
      focusMetrics: {
        totalFocusTime: 0,
        fileTimings: {},
        breakCount: 0
      }
    };
    
    this.load();
    this.startPeriodicSave();
  }
  
  // ===============================================
  // Persistence
  // ===============================================
  
  load() {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        const parsed = JSON.parse(stored);
        this.memory = this.mergeDeep(this.memory, parsed);
        console.log('[Memory] Loaded persistent memory');
      }
      
      const session = sessionStorage.getItem(this.sessionKey);
      if (session) {
        const parsed = JSON.parse(session);
        this.session = this.mergeDeep(this.session, parsed);
        console.log('[Memory] Resumed session');
      }
    } catch (e) {
      console.error('[Memory] Failed to load:', e);
    }
  }
  
  save() {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.memory));
      sessionStorage.setItem(this.sessionKey, JSON.stringify(this.session));
    } catch (e) {
      console.error('[Memory] Failed to save:', e);
      this.cleanup();
    }
  }
  
  startPeriodicSave() {
    setInterval(() => this.save(), 30000); // Save every 30 seconds
    window.addEventListener('beforeunload', () => this.save());
  }
  
  cleanup() {
    // Remove oldest items when storage is full
    if (this.memory.code.recentEdits.length > this.maxMemoryItems) {
      this.memory.code.recentEdits = this.memory.code.recentEdits.slice(-this.maxMemoryItems);
    }
    if (this.memory.context.recentConversations.length > 100) {
      this.memory.context.recentConversations = this.memory.context.recentConversations.slice(-100);
    }
    this.save();
  }
  
  // ===============================================
  // User Preferences
  // ===============================================
  
  setPreference(key, value) {
    this.memory.user.preferences[key] = value;
    this.save();
  }
  
  getPreference(key, defaultValue = null) {
    return this.memory.user.preferences[key] ?? defaultValue;
  }
  
  getAllPreferences() {
    return { ...this.memory.user.preferences };
  }
  
  // ===============================================
  // File Tracking
  // ===============================================
  
  trackFileOpen(filePath) {
    const now = Date.now();
    
    // Update frequent files
    const existing = this.memory.user.frequentFiles.find(f => f.path === filePath);
    if (existing) {
      existing.count++;
      existing.lastOpened = now;
    } else {
      this.memory.user.frequentFiles.push({
        path: filePath,
        count: 1,
        firstOpened: now,
        lastOpened: now
      });
    }
    
    // Sort by frequency
    this.memory.user.frequentFiles.sort((a, b) => b.count - a.count);
    
    // Keep top 50
    if (this.memory.user.frequentFiles.length > 50) {
      this.memory.user.frequentFiles = this.memory.user.frequentFiles.slice(0, 50);
    }
    
    // Session tracking
    if (!this.session.activeFiles.includes(filePath)) {
      this.session.activeFiles.push(filePath);
    }
    
    // Focus timing
    if (this.session.currentContext?.currentFile) {
      const prevFile = this.session.currentContext.currentFile;
      const duration = now - (this.session.focusMetrics.lastFileSwitch || now);
      this.session.focusMetrics.fileTimings[prevFile] = 
        (this.session.focusMetrics.fileTimings[prevFile] || 0) + duration;
    }
    this.session.focusMetrics.lastFileSwitch = now;
    
    this.save();
  }
  
  trackFileEdit(filePath, changes) {
    this.memory.code.recentEdits.push({
      path: filePath,
      timestamp: Date.now(),
      changeType: changes.type || 'edit',
      linesChanged: changes.lines || 1
    });
    
    // Learn patterns
    if (changes.content) {
      this.learnCodePatterns(filePath, changes.content);
    }
  }
  
  getFrequentFiles(limit = 10) {
    return this.memory.user.frequentFiles.slice(0, limit);
  }
  
  getRecentFiles(limit = 10) {
    return [...this.memory.user.frequentFiles]
      .sort((a, b) => b.lastOpened - a.lastOpened)
      .slice(0, limit);
  }
  
  // ===============================================
  // Command & Search History
  // ===============================================
  
  trackCommand(command, context = null) {
    this.session.commandHistory.push({
      command,
      context,
      timestamp: Date.now()
    });
    
    // Update frequent commands
    const existing = this.memory.user.frequentCommands.find(c => c.command === command);
    if (existing) {
      existing.count++;
      existing.lastUsed = Date.now();
    } else {
      this.memory.user.frequentCommands.push({
        command,
        count: 1,
        lastUsed: Date.now()
      });
    }
    
    this.memory.user.frequentCommands.sort((a, b) => b.count - a.count);
    this.save();
  }
  
  trackSearch(query, type = 'file') {
    this.session.searchHistory.push({
      query,
      type,
      timestamp: Date.now()
    });
  }
  
  getCommandSuggestions(partial = '') {
    const commands = this.memory.user.frequentCommands
      .filter(c => c.command.toLowerCase().includes(partial.toLowerCase()))
      .slice(0, 10);
    return commands;
  }
  
  // ===============================================
  // AI Conversation Memory
  // ===============================================
  
  addConversation(message, role = 'user') {
    const entry = {
      role,
      content: message,
      timestamp: Date.now(),
      context: this.getCurrentContext()
    };
    
    this.session.aiConversation.push(entry);
    
    // Also store in long-term memory for learning
    if (role === 'user') {
      this.memory.context.recentConversations.push({
        query: message,
        timestamp: Date.now(),
        project: this.memory.context.currentProject
      });
    }
    
    this.save();
  }
  
  getConversationHistory(limit = 20) {
    return this.session.aiConversation.slice(-limit);
  }
  
  getRelevantContext(query) {
    // Find relevant past conversations
    const relevant = this.memory.context.recentConversations
      .filter(c => this.calculateRelevance(c.query, query) > 0.3)
      .slice(-5);
    
    return {
      recentConversations: this.session.aiConversation.slice(-10),
      relevantPast: relevant,
      currentFile: this.session.currentContext?.currentFile,
      recentFiles: this.session.activeFiles.slice(-5),
      project: this.memory.context.currentProject
    };
  }
  
  // ===============================================
  // Code Pattern Learning
  // ===============================================
  
  learnCodePatterns(filePath, content) {
    const ext = filePath.split('.').pop().toLowerCase();
    
    // Learn naming conventions
    const functionNames = content.match(/function\s+(\w+)|const\s+(\w+)\s*=/g) || [];
    const classNames = content.match(/class\s+(\w+)/g) || [];
    
    if (!this.memory.learning.namingConventions[ext]) {
      this.memory.learning.namingConventions[ext] = {
        functions: [],
        classes: [],
        variables: []
      };
    }
    
    // Detect naming style (camelCase, snake_case, PascalCase)
    functionNames.forEach(fn => {
      const style = this.detectNamingStyle(fn);
      if (style) {
        const conv = this.memory.learning.namingConventions[ext];
        if (!conv.functions.includes(style)) {
          conv.functions.push(style);
        }
      }
    });
    
    // Learn import patterns
    const imports = content.match(/import\s+.+from\s+['"](.+)['"]/g) || [];
    if (imports.length > 0) {
      if (!this.memory.code.dependencies[filePath]) {
        this.memory.code.dependencies[filePath] = [];
      }
      imports.forEach(imp => {
        const match = imp.match(/from\s+['"](.+)['"]/);
        if (match) {
          this.memory.code.dependencies[filePath].push(match[1]);
        }
      });
    }
  }
  
  detectNamingStyle(name) {
    if (name.includes('_')) return 'snake_case';
    if (/^[A-Z]/.test(name)) return 'PascalCase';
    if (/^[a-z]/.test(name) && /[A-Z]/.test(name)) return 'camelCase';
    return null;
  }
  
  getCodeSuggestions(context) {
    const ext = context.fileType || 'js';
    const conventions = this.memory.learning.namingConventions[ext] || {};
    
    return {
      namingStyle: conventions.functions?.[0] || 'camelCase',
      commonImports: this.getCommonImports(ext),
      patterns: this.memory.learning.architecturePatterns
    };
  }
  
  getCommonImports(ext) {
    const allImports = {};
    Object.entries(this.memory.code.dependencies).forEach(([file, deps]) => {
      if (file.endsWith(`.${ext}`)) {
        deps.forEach(dep => {
          allImports[dep] = (allImports[dep] || 0) + 1;
        });
      }
    });
    
    return Object.entries(allImports)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([dep]) => dep);
  }
  
  // ===============================================
  // Work Patterns
  // ===============================================
  
  trackWorkPattern(type, data) {
    const hour = new Date().getHours();
    const day = new Date().getDay();
    
    if (!this.memory.user.workPatterns[type]) {
      this.memory.user.workPatterns[type] = {};
    }
    
    const key = `${day}-${hour}`;
    if (!this.memory.user.workPatterns[type][key]) {
      this.memory.user.workPatterns[type][key] = 0;
    }
    this.memory.user.workPatterns[type][key]++;
  }
  
  getPeakProductivityHours() {
    const patterns = this.memory.user.workPatterns.edit || {};
    const hourCounts = {};
    
    Object.entries(patterns).forEach(([key, count]) => {
      const hour = key.split('-')[1];
      hourCounts[hour] = (hourCounts[hour] || 0) + count;
    });
    
    return Object.entries(hourCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([hour]) => parseInt(hour));
  }
  
  // ===============================================
  // Context Management
  // ===============================================
  
  setCurrentContext(context) {
    this.session.currentContext = {
      ...this.session.currentContext,
      ...context,
      updatedAt: Date.now()
    };
  }
  
  getCurrentContext() {
    return this.session.currentContext || {};
  }
  
  setCurrentProject(projectPath) {
    this.memory.context.currentProject = {
      path: projectPath,
      lastOpened: Date.now()
    };
    this.save();
  }
  
  // ===============================================
  // Task History
  // ===============================================
  
  addTask(task) {
    this.memory.context.taskHistory.push({
      ...task,
      timestamp: Date.now(),
      status: 'pending'
    });
    this.save();
  }
  
  completeTask(taskId) {
    const task = this.memory.context.taskHistory.find(t => t.id === taskId);
    if (task) {
      task.status = 'completed';
      task.completedAt = Date.now();
      this.save();
    }
  }
  
  getRecentTasks(limit = 10) {
    return this.memory.context.taskHistory
      .slice(-limit)
      .reverse();
  }
  
  // ===============================================
  // Error Pattern Learning
  // ===============================================
  
  trackError(error, context) {
    this.memory.context.errorPatterns.push({
      message: error.message,
      type: error.name,
      file: context.file,
      line: context.line,
      timestamp: Date.now(),
      resolved: false
    });
    
    this.save();
  }
  
  getErrorPatterns(file = null) {
    if (file) {
      return this.memory.context.errorPatterns.filter(e => e.file === file);
    }
    return this.memory.context.errorPatterns.slice(-20);
  }
  
  // ===============================================
  // Stats & Analytics
  // ===============================================
  
  getStats() {
    return {
      totalFiles: this.memory.user.frequentFiles.length,
      totalCommands: this.memory.user.frequentCommands.reduce((sum, c) => sum + c.count, 0),
      totalConversations: this.memory.context.recentConversations.length,
      sessionDuration: Date.now() - this.session.startTime,
      filesOpenedThisSession: this.session.activeFiles.length,
      peakHours: this.getPeakProductivityHours(),
      topFiles: this.getFrequentFiles(5),
      topCommands: this.memory.user.frequentCommands.slice(0, 5)
    };
  }
  
  // ===============================================
  // Export & Import
  // ===============================================
  
  exportMemory() {
    return JSON.stringify({
      memory: this.memory,
      exportedAt: Date.now(),
      version: '1.0'
    }, null, 2);
  }
  
  importMemory(data) {
    try {
      const parsed = JSON.parse(data);
      if (parsed.memory) {
        this.memory = this.mergeDeep(this.memory, parsed.memory);
        this.save();
        return true;
      }
    } catch (e) {
      console.error('[Memory] Import failed:', e);
    }
    return false;
  }
  
  clearMemory(type = 'all') {
    if (type === 'all') {
      localStorage.removeItem(this.storageKey);
      sessionStorage.removeItem(this.sessionKey);
      location.reload();
    } else if (type === 'session') {
      sessionStorage.removeItem(this.sessionKey);
      this.session = {
        startTime: Date.now(),
        activeFiles: [],
        searchHistory: [],
        commandHistory: [],
        aiConversation: [],
        currentContext: null,
        focusMetrics: {}
      };
    }
  }
  
  // ===============================================
  // Utilities
  // ===============================================
  
  mergeDeep(target, source) {
    const result = { ...target };
    for (const key in source) {
      if (source[key] instanceof Object && !Array.isArray(source[key])) {
        result[key] = this.mergeDeep(target[key] || {}, source[key]);
      } else {
        result[key] = source[key];
      }
    }
    return result;
  }
  
  calculateRelevance(text1, text2) {
    if (!text1 || !text2) return 0;
    
    const words1 = text1.toLowerCase().split(/\s+/);
    const words2 = text2.toLowerCase().split(/\s+/);
    
    let matches = 0;
    words1.forEach(w1 => {
      if (words2.some(w2 => w2.includes(w1) || w1.includes(w2))) {
        matches++;
      }
    });
    
    return matches / Math.max(words1.length, words2.length);
  }
}

// Create global instance
window.AriaMemory = new MemorySystem();
