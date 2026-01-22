// ARIA WebUI Server - Main entry point
import express from 'express';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';

// Route imports
import { createFileRoutes } from './routes/files.js';
import { createSystemRoutes } from './routes/system.js';
import { createGitRoutes } from './routes/git.js';
import { createDockerRoutes } from './routes/docker.js';
import { createAgentRoutes } from './routes/agents.js';
import { createAutomationRoutes } from './routes/automation.js';
import { createAnalysisRoutes } from './routes/analysis.js';
import { setupTerminalWebSocket } from './terminal.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server, path: '/terminal' });

// Base directory
const BASE_DIR = process.env.BASE_DIR || '/home/dev';

// Middleware
app.use(cors());
app.use(express.json());

// Disable caching for development
app.use((req, res, next) => {
  res.set('Cache-Control', 'no-store, no-cache, must-revalidate, private');
  res.set('Pragma', 'no-cache');
  res.set('Expires', '0');
  next();
});

// Static files
app.use(express.static(path.join(__dirname, 'public')));

// API routes
app.use('/api', createFileRoutes(BASE_DIR));
app.use('/api', createSystemRoutes(BASE_DIR));
app.use('/api', createGitRoutes(BASE_DIR));
app.use('/api', createDockerRoutes());
app.use('/api', createAgentRoutes());
app.use('/api', createAutomationRoutes(BASE_DIR));
app.use('/api', createAnalysisRoutes(BASE_DIR));

// Terminal WebSocket
setupTerminalWebSocket(wss, BASE_DIR);

// Start server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`
\x1b[38;5;141m
    _    ____  ___    _     
   / \\  |  _ \\|_ _|  / \\    
  / _ \\ | |_) || |  / _ \\   
 / ___ \\|  _ < | | / ___ \\  
/_/   \\_\\_| \\_\\___/_/   \\_\\ 
\x1b[0m
\x1b[38;5;75m  Adaptive Real-time Intelligence Assistant\x1b[0m
\x1b[38;5;245m  ----------------------------------------\x1b[0m

  \x1b[38;5;82mServer running at:\x1b[0m \x1b[38;5;226mhttp://localhost:${PORT}\x1b[0m
  \x1b[38;5;82mBase directory:\x1b[0m    \x1b[38;5;226m${BASE_DIR}\x1b[0m

  \x1b[38;5;245mFeatures:\x1b[0m
    - Terminal emulator with PTY
    - File explorer with editor
    - System monitoring dashboard
    - Git integration
    - Docker management
    - Automation tools
    - AI Agent integration
    - Code analysis

`);
});
