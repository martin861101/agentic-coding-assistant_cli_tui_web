// Automation, search, and workflow API routes
import express from 'express';
import { exec } from 'child_process';
import path from 'path';

const router = express.Router();

export function createAutomationRoutes(BASE_DIR) {
  // Run automation command
  router.post('/automation/run', async (req, res) => {
    try {
      const { command, cwd } = req.body;
      const workDir = cwd || BASE_DIR;
      
      exec(command, { cwd: workDir, timeout: 30000 }, (error, stdout, stderr) => {
        res.json({
          success: !error,
          stdout,
          stderr,
          error: error?.message
        });
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  // Get automation scripts
  router.get('/automation/scripts', async (req, res) => {
    res.json({
      scripts: [
        { id: 'npm-install', name: 'NPM Install', command: 'npm install', icon: 'package' },
        { id: 'npm-build', name: 'NPM Build', command: 'npm run build', icon: 'build' },
        { id: 'npm-test', name: 'NPM Test', command: 'npm test', icon: 'test' },
        { id: 'npm-dev', name: 'NPM Dev Server', command: 'npm run dev', icon: 'play' },
        { id: 'git-pull', name: 'Git Pull', command: 'git pull', icon: 'git' },
        { id: 'git-status', name: 'Git Status', command: 'git status', icon: 'git' },
        { id: 'docker-ps', name: 'Docker PS', command: 'docker ps', icon: 'docker' },
        { id: 'disk-usage', name: 'Disk Usage', command: 'du -sh *', icon: 'disk' },
        { id: 'find-large', name: 'Find Large Files', command: 'find . -size +10M -type f 2>/dev/null | head -20', icon: 'search' },
        { id: 'count-lines', name: 'Count Code Lines', command: 'find . -name "*.js" -o -name "*.ts" -o -name "*.go" -o -name "*.py" | xargs wc -l 2>/dev/null | tail -1', icon: 'code' }
      ]
    });
  });

  // Search API
  router.get('/search', async (req, res) => {
    try {
      const { query, path: searchPath, type } = req.query;
      const basePath = searchPath || BASE_DIR;
      
      let cmd;
      if (type === 'content') {
        cmd = `grep -r -l -i "${query}" --include="*.{js,ts,go,py,json,md,html,css}" . 2>/dev/null | head -50`;
      } else {
        cmd = `find . -iname "*${query}*" -type f 2>/dev/null | head -50`;
      }
      
      exec(cmd, { cwd: basePath }, (error, stdout) => {
        const results = stdout.trim().split('\n').filter(l => l).map(f => ({
          path: path.join(basePath, f.replace(/^\.\//, '')),
          name: path.basename(f)
        }));
        res.json({ results });
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  // Workflows API
  router.get('/workflows', (req, res) => {
    const workflows = [
      {
        id: 'wf_precommit',
        name: 'Pre-Commit Check',
        steps: [
          { type: 'command', name: 'Lint', command: 'npm run lint' },
          { type: 'command', name: 'Test', command: 'npm test' }
        ],
        enabled: true
      },
      {
        id: 'wf_build',
        name: 'Build & Deploy',
        steps: [
          { type: 'command', name: 'Build', command: 'npm run build' },
          { type: 'notification', name: 'Notify', message: 'Build complete' }
        ],
        enabled: true
      },
      {
        id: 'wf_review',
        name: 'Full Code Review',
        steps: [
          { type: 'agent', name: 'Review', agentId: 'code-review' },
          { type: 'agent', name: 'Security', agentId: 'security' }
        ],
        enabled: false
      }
    ];
    
    res.json({ workflows });
  });

  router.post('/workflows/run', async (req, res) => {
    try {
      const { workflowId } = req.body;
      
      res.json({
        success: true,
        workflowId,
        message: 'Workflow started',
        timestamp: Date.now()
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  // Memory API
  router.get('/memory/stats', (req, res) => {
    res.json({
      active: true,
      sessionDuration: Date.now(),
      features: ['preferences', 'file-tracking', 'code-patterns', 'conversations']
    });
  });

  return router;
}

export default router;
