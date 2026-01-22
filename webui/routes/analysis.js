// Code analysis and project insights API routes
import express from 'express';
import fs from 'fs/promises';
import path from 'path';
import { exec } from 'child_process';

const router = express.Router();

export function createAnalysisRoutes(BASE_DIR) {
  // Single file analysis
  router.get('/analyze', async (req, res) => {
    try {
      const filePath = req.query.path;
      if (!filePath) return res.status(400).json({ error: 'Path required' });
      
      const content = await fs.readFile(filePath, 'utf-8');
      const lines = content.split('\n');
      const ext = path.extname(filePath).toLowerCase();
      
      const analysis = {
        lines: lines.length,
        characters: content.length,
        blankLines: lines.filter(l => l.trim() === '').length,
        commentLines: 0,
        functions: 0,
        classes: 0,
        imports: 0,
        todos: [],
        language: ext.replace('.', '')
      };
      
      // Language-specific analysis
      if (['.js', '.ts', '.jsx', '.tsx'].includes(ext)) {
        analysis.commentLines = lines.filter(l => l.trim().startsWith('//') || l.trim().startsWith('/*')).length;
        analysis.functions = (content.match(/function\s+\w+|const\s+\w+\s*=\s*(?:async\s*)?\(/g) || []).length;
        analysis.classes = (content.match(/class\s+\w+/g) || []).length;
        analysis.imports = (content.match(/import\s+/g) || []).length;
      } else if (['.py'].includes(ext)) {
        analysis.commentLines = lines.filter(l => l.trim().startsWith('#')).length;
        analysis.functions = (content.match(/def\s+\w+/g) || []).length;
        analysis.classes = (content.match(/class\s+\w+/g) || []).length;
        analysis.imports = (content.match(/import\s+|from\s+\w+\s+import/g) || []).length;
      } else if (['.go'].includes(ext)) {
        analysis.commentLines = lines.filter(l => l.trim().startsWith('//')).length;
        analysis.functions = (content.match(/func\s+\w+/g) || []).length;
        analysis.classes = (content.match(/type\s+\w+\s+struct/g) || []).length;
        analysis.imports = (content.match(/import\s+/g) || []).length;
      }
      
      // Find TODOs
      lines.forEach((line, i) => {
        if (line.toLowerCase().includes('todo') || line.toLowerCase().includes('fixme')) {
          analysis.todos.push({ line: i + 1, text: line.trim() });
        }
      });
      
      res.json(analysis);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  // Project insights
  router.get('/insights', async (req, res) => {
    try {
      const projectPath = req.query.path || BASE_DIR;
      
      const structure = await analyzeProjectStructure(projectPath);
      const codeStats = await analyzeCodeStats(projectPath);
      
      res.json({
        structure,
        codeStats,
        suggestions: generateSuggestions(structure, codeStats),
        timestamp: Date.now()
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  return router;
}

async function analyzeProjectStructure(projectPath) {
  try {
    const entries = await fs.readdir(projectPath, { withFileTypes: true });
    let totalFiles = 0;
    let totalFolders = 0;
    const fileTypes = {};
    
    for (const entry of entries) {
      if (entry.name.startsWith('.')) continue;
      
      if (entry.isDirectory()) {
        totalFolders++;
      } else {
        totalFiles++;
        const ext = path.extname(entry.name).slice(1).toLowerCase() || 'other';
        fileTypes[ext] = (fileTypes[ext] || 0) + 1;
      }
    }
    
    return { totalFiles, totalFolders, fileTypes };
  } catch (e) {
    return { totalFiles: 0, totalFolders: 0, fileTypes: {} };
  }
}

async function analyzeCodeStats(projectPath) {
  return new Promise((resolve) => {
    exec(`find ${projectPath} -name "*.js" -o -name "*.ts" -o -name "*.py" -o -name "*.go" 2>/dev/null | head -100 | xargs wc -l 2>/dev/null | tail -1`, 
      (error, stdout) => {
        const lines = parseInt(stdout.trim().split(/\s+/)[0]) || 0;
        resolve({ totalLines: lines });
      }
    );
  });
}

function generateSuggestions(structure, codeStats) {
  const suggestions = [];
  
  if (structure.totalFiles > 100) {
    suggestions.push({
      priority: 'medium',
      message: 'Consider organizing files into more subdirectories',
      action: 'Review folder structure'
    });
  }
  
  if (codeStats.totalLines > 10000) {
    suggestions.push({
      priority: 'low',
      message: 'Large codebase detected - consider code splitting',
      action: 'Analyze module boundaries'
    });
  }
  
  return suggestions;
}

export default router;
