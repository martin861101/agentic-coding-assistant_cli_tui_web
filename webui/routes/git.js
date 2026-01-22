// Git API routes
import express from 'express';
import { exec } from 'child_process';
import { getGitInfo } from '../utils/system-helpers.js';

const router = express.Router();

export function createGitRoutes(BASE_DIR) {
  router.get('/git/status', async (req, res) => {
    try {
      const dirPath = req.query.path || BASE_DIR;
      const info = await getGitInfo(dirPath);
      if (!info) return res.status(400).json({ error: 'Not a git repository' });
      res.json(info);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  router.get('/git/log', async (req, res) => {
    try {
      const dirPath = req.query.path || BASE_DIR;
      const limit = req.query.limit || 10;
      
      exec(`git log -${limit} --format="%h|%an|%s|%cr"`, { cwd: dirPath }, (error, stdout) => {
        if (error) return res.status(400).json({ error: 'Not a git repository' });
        
        const commits = stdout.trim().split('\n').filter(l => l).map(line => {
          const [hash, author, message, time] = line.split('|');
          return { hash, author, message, time };
        });
        res.json({ commits });
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  router.post('/git/command', async (req, res) => {
    try {
      const { command, path: dirPath } = req.body;
      const safePath = dirPath || BASE_DIR;
      
      // Only allow safe git commands
      const safeCommands = ['status', 'log', 'diff', 'branch', 'remote', 'fetch', 'pull', 'add', 'commit', 'stash'];
      const cmdParts = command.split(' ');
      if (!safeCommands.includes(cmdParts[0])) {
        return res.status(400).json({ error: 'Command not allowed' });
      }
      
      exec(`git ${command}`, { cwd: safePath }, (error, stdout, stderr) => {
        res.json({ 
          success: !error, 
          output: stdout || stderr,
          error: error?.message 
        });
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  return router;
}

export default router;
