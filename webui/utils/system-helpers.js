// System helper functions for monitoring and status
import os from 'os';
import { exec } from 'child_process';

export function getCPUUsage() {
  return new Promise((resolve) => {
    const cpus = os.cpus();
    let totalIdle = 0, totalTick = 0;
    
    cpus.forEach(cpu => {
      for (let type in cpu.times) {
        totalTick += cpu.times[type];
      }
      totalIdle += cpu.times.idle;
    });
    
    const idle = totalIdle / cpus.length;
    const total = totalTick / cpus.length;
    const usage = 100 - Math.round((idle / total) * 100);
    resolve(usage);
  });
}

export function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function getMemoryInfo() {
  const total = os.totalmem();
  const free = os.freemem();
  const used = total - free;
  return {
    total,
    free,
    used,
    percentage: Math.round((used / total) * 100),
    totalFormatted: formatBytes(total),
    usedFormatted: formatBytes(used),
    freeFormatted: formatBytes(free)
  };
}

export async function getDiskInfo() {
  return new Promise((resolve) => {
    exec('df -h / | tail -1', (error, stdout) => {
      if (error) {
        resolve({ total: 'N/A', used: 'N/A', available: 'N/A', percentage: 0 });
        return;
      }
      const parts = stdout.trim().split(/\s+/);
      resolve({
        filesystem: parts[0],
        total: parts[1],
        used: parts[2],
        available: parts[3],
        percentage: parseInt(parts[4]) || 0
      });
    });
  });
}

export async function getProcesses(limit = 10) {
  return new Promise((resolve) => {
    exec('ps aux --sort=-%cpu | head -n ' + (limit + 1), (error, stdout) => {
      if (error) {
        resolve([]);
        return;
      }
      const lines = stdout.trim().split('\n');
      const processes = lines.slice(1).map(line => {
        const parts = line.split(/\s+/);
        return {
          user: parts[0],
          pid: parts[1],
          cpu: parseFloat(parts[2]),
          mem: parseFloat(parts[3]),
          command: parts.slice(10).join(' ').substring(0, 50)
        };
      });
      resolve(processes);
    });
  });
}

export async function getNetworkStats() {
  return new Promise((resolve) => {
    const interfaces = os.networkInterfaces();
    const stats = [];
    for (const [name, addrs] of Object.entries(interfaces)) {
      if (name !== 'lo') {
        const ipv4 = addrs.find(a => a.family === 'IPv4');
        if (ipv4) {
          stats.push({
            name,
            address: ipv4.address,
            mac: ipv4.mac
          });
        }
      }
    }
    resolve(stats);
  });
}

export async function getUptime() {
  const uptime = os.uptime();
  const days = Math.floor(uptime / 86400);
  const hours = Math.floor((uptime % 86400) / 3600);
  const minutes = Math.floor((uptime % 3600) / 60);
  return { seconds: uptime, formatted: `${days}d ${hours}h ${minutes}m` };
}

export async function getGitInfo(dirPath) {
  return new Promise((resolve) => {
    exec('git status --porcelain && git branch --show-current && git log -1 --format="%h|%s|%cr"', 
      { cwd: dirPath }, 
      (error, stdout) => {
        if (error) {
          resolve(null);
          return;
        }
        const lines = stdout.trim().split('\n');
        const changes = lines.filter(l => l.match(/^[MADRC?]/)).length;
        const branch = lines[lines.length - 2] || 'unknown';
        const commitInfo = lines[lines.length - 1]?.split('|') || [];
        resolve({
          branch,
          changes,
          lastCommit: {
            hash: commitInfo[0],
            message: commitInfo[1],
            time: commitInfo[2]
          }
        });
      }
    );
  });
}

export async function getDockerContainers() {
  return new Promise((resolve) => {
    exec('docker ps --format "{{.ID}}|{{.Image}}|{{.Status}}|{{.Names}}"', (error, stdout) => {
      if (error) {
        resolve([]);
        return;
      }
      const containers = stdout.trim().split('\n').filter(l => l).map(line => {
        const [id, image, status, name] = line.split('|');
        return { id, image, status, name };
      });
      resolve(containers);
    });
  });
}
