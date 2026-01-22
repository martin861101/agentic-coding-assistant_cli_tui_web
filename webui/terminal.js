// Terminal WebSocket handler
import { spawn } from 'child_process';

export function setupTerminalWebSocket(wss, BASE_DIR) {
  wss.on('connection', (ws) => {
    console.log('Terminal connection established');
    
    const shell = process.env.SHELL || '/bin/bash';
    let ptyProcess = null;
    
    try {
      import('node-pty').then((pty) => {
        ptyProcess = pty.spawn(shell, [], {
          name: 'xterm-256color',
          cols: 120,
          rows: 30,
          cwd: BASE_DIR,
          env: process.env,
        });
        
        ptyProcess.onData((data) => {
          if (ws.readyState === ws.OPEN) {
            ws.send(JSON.stringify({ type: 'output', data }));
          }
        });
        
        ptyProcess.onExit(({ exitCode }) => {
          if (ws.readyState === ws.OPEN) {
            ws.send(JSON.stringify({ type: 'exit', code: exitCode }));
          }
        });
      }).catch(() => {
        console.log('node-pty not available, using basic spawn');
        setupBasicTerminal(ws, shell, BASE_DIR);
      });
    } catch (e) {
      setupBasicTerminal(ws, shell, BASE_DIR);
    }
    
    ws.on('message', (message) => {
      try {
        const msg = JSON.parse(message.toString());
        
        if (msg.type === 'input' && ptyProcess) {
          ptyProcess.write(msg.data);
        } else if (msg.type === 'resize' && ptyProcess) {
          ptyProcess.resize(msg.cols, msg.rows);
        }
      } catch (e) {
        console.error('Error processing message:', e);
      }
    });
    
    ws.on('close', () => {
      console.log('Terminal connection closed');
      if (ptyProcess) {
        ptyProcess.kill();
      }
    });
  });
}

function setupBasicTerminal(ws, shell, BASE_DIR) {
  const proc = spawn(shell, [], {
    cwd: BASE_DIR,
    env: { ...process.env, TERM: 'xterm-256color' },
    stdio: ['pipe', 'pipe', 'pipe'],
  });
  
  proc.stdout.on('data', (data) => {
    if (ws.readyState === ws.OPEN) {
      ws.send(JSON.stringify({ type: 'output', data: data.toString() }));
    }
  });
  
  proc.stderr.on('data', (data) => {
    if (ws.readyState === ws.OPEN) {
      ws.send(JSON.stringify({ type: 'output', data: data.toString() }));
    }
  });
  
  proc.on('close', (code) => {
    if (ws.readyState === ws.OPEN) {
      ws.send(JSON.stringify({ type: 'exit', code }));
    }
  });
  
  ws.on('message', (message) => {
    try {
      const msg = JSON.parse(message.toString());
      if (msg.type === 'input') {
        proc.stdin.write(msg.data);
      }
    } catch (e) {
      console.error('Error processing message:', e);
    }
  });
  
  ws.on('close', () => {
    proc.kill();
  });
}
