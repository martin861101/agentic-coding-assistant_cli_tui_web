// System status API routes
import express from 'express';
import os from 'os';
import { getCPUUsage, getMemoryInfo, getDiskInfo, getUptime, getNetworkStats, getProcesses } from '../utils/system-helpers.js';

const router = express.Router();

export function createSystemRoutes(BASE_DIR) {
  router.get('/system', async (req, res) => {
    try {
      const cpuUsage = await getCPUUsage();
      const memory = getMemoryInfo();
      const disk = await getDiskInfo();
      const uptime = await getUptime();
      const network = await getNetworkStats();
      const loadAvg = os.loadavg();
      
      res.json({
        platform: os.platform(),
        hostname: os.hostname(),
        homedir: os.homedir(),
        cwd: BASE_DIR,
        arch: os.arch(),
        cpuModel: os.cpus()[0]?.model || 'Unknown',
        cpuCores: os.cpus().length,
        cpuUsage,
        memory,
        disk,
        uptime,
        network,
        loadAvg: loadAvg.map(l => l.toFixed(2)),
        nodeVersion: process.version
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  router.get('/system/processes', async (req, res) => {
    try {
      const processes = await getProcesses(15);
      res.json({ processes });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  router.get('/system/realtime', async (req, res) => {
    try {
      const cpuUsage = await getCPUUsage();
      const memory = getMemoryInfo();
      res.json({ cpuUsage, memory, timestamp: Date.now() });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  return router;
}

export default router;
