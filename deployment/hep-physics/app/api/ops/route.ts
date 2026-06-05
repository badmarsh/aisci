import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import util from 'util';
import fs from 'fs/promises';

const execPromise = util.promisify(exec);

async function checkHealth(url: string) {
  try {
    const res = await fetch(url, { signal: AbortSignal.timeout(2000) });
    return res.ok ? 'healthy' : 'degraded';
  } catch (e) {
    return 'down';
  }
}

export async function GET() {
  try {
    // 1. Docker Stats
    let dockerStack = [];
    try {
      const { stdout: dockerStatsStr } = await execPromise('wsl docker stats --no-stream --format "{{json .}}"');
      const lines = dockerStatsStr.trim().split('\\n').filter(Boolean);
      dockerStack = lines.map((line, i) => {
        const d = JSON.parse(line);
        return {
          id: `d${i+1}`,
          name: d.Name,
          image: "unknown", // stats doesn't provide image easily without combining with ps
          replicas: "1/1",
          status: "running",
          cpu: d.CPUPerc,
          mem: d.MemUsage.split(' / ')[0]
        };
      });
      
      // enrich with image names from docker ps
      const { stdout: dockerPsStr } = await execPromise('wsl docker ps --format "{{json .}}"');
      const psLines = dockerPsStr.trim().split('\\n').filter(Boolean);
      const nameToImage = {};
      psLines.forEach(line => {
        const d = JSON.parse(line);
        nameToImage[d.Names] = d.Image;
      });
      
      dockerStack.forEach(d => {
        if (nameToImage[d.name]) {
          d.image = nameToImage[d.name];
        }
      });
      
    } catch (e) {
      console.warn("Could not fetch docker stats", e);
    }

    // 2. Health Checks
    const onyxStatus = await checkHealth('http://localhost:5000/healthz');
    const dfStatus = await checkHealth('http://localhost:8765/healthz');

    const services = [
      {
        id: "onyx", label: "Onyx", version: "v0.4.12", host: "localhost:5000",
        uptime: "Live", status: onyxStatus, lastCheck: new Date().toISOString().substring(11, 19) + " UTC", note: onyxStatus === 'down' ? "Connection refused" : null,
      },
      {
        id: "deerflow", label: "DeerFlow", version: "v1.2.1", host: "localhost:8765",
        uptime: "Live", status: dfStatus, lastCheck: new Date().toISOString().substring(11, 19) + " UTC", note: dfStatus === 'down' ? "Connection refused" : null,
      },
      {
        id: "mcp_proxy", label: "MCP Proxy", version: "v0.2.4", host: "localhost:3000",
        uptime: "Live", status: "healthy", lastCheck: new Date().toISOString().substring(11, 19) + " UTC", note: null,
      }
    ];

    // 3. Security Scans
    let secretStatus = "clean";
    let secretFindings = [];
    try {
      const gitleaksFile = '/home/ubuntu/aisci/gitleaks-report.json';
      const stats = await fs.stat(gitleaksFile).catch(() => null);
      if (stats) {
        const content = await fs.readFile(gitleaksFile, 'utf-8');
        const findings = JSON.parse(content);
        if (findings.length > 0) {
          secretStatus = "warning";
          secretFindings = findings.map((f: any) => ({
            file: f.File || 'unknown',
            rule: f.RuleID || 'generic-leak',
            line: f.StartLine || 0
          }));
        }
      }
    } catch(e) {}

    // 4. Logs
    let logLines = [];
    try {
      const { stdout } = await execPromise('wsl docker logs portainer --tail 10 2>&1 || echo "Error getting logs"');
      logLines = stdout.split('\\n').filter(Boolean).map(l => ({
        ts: new Date().toISOString().substring(11, 23),
        level: l.toLowerCase().includes('error') ? 'ERROR' : l.toLowerCase().includes('warn') ? 'WARN' : 'INFO',
        svc: 'portainer',
        msg: l.substring(0, 100)
      }));
    } catch(e) {}

    return NextResponse.json({
      services,
      dockerStack,
      gpuEnabled: false,
      secretStatus,
      secretFindings,
      logLines
    });

  } catch (error) {
    console.error('Error in ops API:', error);
    return NextResponse.json({ error: 'Failed to fetch ops data' }, { status: 500 });
  }
}
