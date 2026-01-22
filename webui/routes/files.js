// File system API routes
import express from 'express';
import fs from 'fs/promises';
import path from 'path';

const router = express.Router();

export function createFileRoutes(BASE_DIR) {
  router.get('/files', async (req, res) => {
    try {
      const dirPath = req.query.path || BASE_DIR;
      const resolvedPath = path.resolve(dirPath);
      
      const entries = await fs.readdir(resolvedPath, { withFileTypes: true });
      const files = await Promise.all(
        entries.map(async (entry) => {
          const fullPath = path.join(resolvedPath, entry.name);
          let stats = null;
          try {
            stats = await fs.stat(fullPath);
          } catch (e) {}
          return {
            name: entry.name,
            path: fullPath,
            isDirectory: entry.isDirectory(),
            isFile: entry.isFile(),
            size: stats?.size || 0,
            modified: stats?.mtime || null,
          };
        })
      );
      
      files.sort((a, b) => {
        if (a.isDirectory && !b.isDirectory) return -1;
        if (!a.isDirectory && b.isDirectory) return 1;
        return a.name.localeCompare(b.name);
      });
      
      res.json({ path: resolvedPath, parent: path.dirname(resolvedPath), files });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  router.get('/file', async (req, res) => {
    try {
      const filePath = req.query.path;
      if (!filePath) return res.status(400).json({ error: 'Path is required' });
      
      const content = await fs.readFile(filePath, 'utf-8');
      const stats = await fs.stat(filePath);
      
      res.json({
        path: filePath,
        name: path.basename(filePath),
        content,
        size: stats.size,
        modified: stats.mtime,
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  router.post('/file', async (req, res) => {
    try {
      const { path: filePath, content } = req.body;
      if (!filePath) return res.status(400).json({ error: 'Path is required' });
      
      const dir = path.dirname(filePath);
      await fs.mkdir(dir, { recursive: true });
      await fs.writeFile(filePath, content, 'utf-8');
      res.json({ success: true, path: filePath });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  router.post('/mkdir', async (req, res) => {
    try {
      const { path: dirPath } = req.body;
      if (!dirPath) return res.status(400).json({ error: 'Path is required' });
      
      await fs.mkdir(dirPath, { recursive: true });
      res.json({ success: true, path: dirPath });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  router.delete('/file', async (req, res) => {
    try {
      const filePath = req.query.path;
      if (!filePath) return res.status(400).json({ error: 'Path is required' });
      
      const stats = await fs.stat(filePath);
      if (stats.isDirectory()) {
        await fs.rm(filePath, { recursive: true });
      } else {
        await fs.unlink(filePath);
      }
      res.json({ success: true });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  router.post('/rename', async (req, res) => {
    try {
      const { oldPath, newPath } = req.body;
      if (!oldPath || !newPath) return res.status(400).json({ error: 'Both paths required' });
      
      await fs.rename(oldPath, newPath);
      res.json({ success: true, path: newPath });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  router.post('/file/copy', async (req, res) => {
    try {
      const { sourcePath, destPath } = req.body;
      if (!sourcePath || !destPath) {
        return res.status(400).json({ error: 'Source and destination paths required' });
      }
      
      const sourceStats = await fs.stat(sourcePath);
      
      if (sourceStats.isDirectory()) {
        await copyDirectory(sourcePath, destPath);
      } else {
        await fs.copyFile(sourcePath, destPath);
      }
      
      res.json({ success: true, path: destPath });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  router.post('/file/move', async (req, res) => {
    try {
      const { sourcePath, destPath } = req.body;
      if (!sourcePath || !destPath) {
        return res.status(400).json({ error: 'Source and destination paths required' });
      }
      
      await fs.rename(sourcePath, destPath);
      res.json({ success: true, path: destPath });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  router.post('/upload', async (req, res) => {
    try {
      const { path: destPath, content, encoding } = req.body;
      if (!destPath) return res.status(400).json({ error: 'Path required' });
      
      const dir = path.dirname(destPath);
      await fs.mkdir(dir, { recursive: true });
      
      if (encoding === 'base64') {
        const buffer = Buffer.from(content, 'base64');
        await fs.writeFile(destPath, buffer);
      } else {
        await fs.writeFile(destPath, content, 'utf-8');
      }
      
      res.json({ success: true, path: destPath });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  return router;
}

async function copyDirectory(src, dest) {
  await fs.mkdir(dest, { recursive: true });
  const entries = await fs.readdir(src, { withFileTypes: true });
  
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    
    if (entry.isDirectory()) {
      await copyDirectory(srcPath, destPath);
    } else {
      await fs.copyFile(srcPath, destPath);
    }
  }
}

export default router;
