// Docker API routes
import express from 'express';
import { exec } from 'child_process';
import { getDockerContainers } from '../utils/system-helpers.js';

const router = express.Router();

export function createDockerRoutes() {
  router.get('/docker/containers', async (req, res) => {
    try {
      const containers = await getDockerContainers();
      res.json({ containers });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  router.get('/docker/images', async (req, res) => {
    exec('docker images --format "{{.Repository}}|{{.Tag}}|{{.Size}}|{{.ID}}"', (error, stdout) => {
      if (error) return res.json({ images: [] });
      
      const images = stdout.trim().split('\n').filter(l => l).map(line => {
        const [repository, tag, size, id] = line.split('|');
        return { repository, tag, size, id };
      });
      res.json({ images });
    });
  });

  router.post('/docker/command', async (req, res) => {
    try {
      const { action, container } = req.body;
      const safeActions = ['start', 'stop', 'restart', 'logs', 'inspect'];
      
      if (!safeActions.includes(action)) {
        return res.status(400).json({ error: 'Action not allowed' });
      }
      
      const cmd = action === 'logs' ? `docker logs --tail 100 ${container}` : `docker ${action} ${container}`;
      exec(cmd, (error, stdout, stderr) => {
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
