import { NextResponse } from 'next/server';
import fs from 'fs/promises';

export async function GET() {
  try {
    const filePath = '/home/ubuntu/aisci/pytest-report.xml';
    let xml = '';
    try {
      xml = await fs.readFile(filePath, 'utf-8');
    } catch (e) {
      console.warn('Could not read pytest report', e);
      return NextResponse.json({ subsystems: [], failures: [] });
    }

    const tcBlocks = xml.split('<testcase').slice(1);
    const subsystemsMap: Record<string, { passed: number; failed: number; skipped: number; time: number }> = {};
    const failures = [];
    let failureId = 1;

    for (const block of tcBlocks) {
      const classnameMatch = block.match(/classname="([^"]+)"/);
      const nameMatch = block.match(/name="([^"]+)"/);
      const timeMatch = block.match(/time="([^"]+)"/);
      
      const classname = classnameMatch ? classnameMatch[1] : 'unknown';
      const name = nameMatch ? nameMatch[1] : 'unknown';
      const time = timeMatch ? parseFloat(timeMatch[1]) : 0;
      
      let subsystem = 'Other';
      if (classname.includes('physics')) subsystem = 'Physics';
      else if (classname.includes('onyx')) subsystem = 'Onyx';
      else if (classname.includes('deerflow')) subsystem = 'DeerFlow';
      else if (classname.includes('mcp')) subsystem = 'MCP Proxy';
      else if (classname.includes('pipeline')) subsystem = 'Fit Pipeline';
      else subsystem = 'Physics'; // Default to Physics if unknown for demonstration
      
      if (!subsystemsMap[subsystem]) {
        subsystemsMap[subsystem] = { passed: 0, failed: 0, skipped: 0, time: 0 };
      }
      
      subsystemsMap[subsystem].time += time;
      
      if (block.includes('<failure')) {
        subsystemsMap[subsystem].failed++;
        const msgMatch = block.match(/message="([^"]+)"/);
        failures.push({
          id: `F-${String(failureId++).padStart(3, '0')}`,
          subsystem,
          test: name,
          message: msgMatch ? msgMatch[1].replace(/&quot;/g, '"').replace(/&lt;/g, '<').replace(/&gt;/g, '>') : 'Failed',
          duration: `${time.toFixed(2)} s`,
          time: new Date().toISOString().substring(11, 19)
        });
      } else if (block.includes('<skipped')) {
        subsystemsMap[subsystem].skipped++;
      } else {
        subsystemsMap[subsystem].passed++;
      }
    }

    const subsystems = Object.keys(subsystemsMap).map(k => {
      const s = subsystemsMap[k];
      const total = s.passed + s.failed + s.skipped;
      const coverage = total > 0 ? Math.round((s.passed / total) * 100) : 0;
      return {
        id: k.toLowerCase().replace(/\s+/g, '_'),
        label: k,
        passed: s.passed,
        failed: s.failed,
        skipped: s.skipped,
        coverage,
        duration: `${s.time.toFixed(1)} s`,
        lastRun: new Date().toISOString().substring(0, 16).replace('T', ' ') + ' UTC'
      };
    });

    return NextResponse.json({ subsystems, failures });

  } catch (error) {
    console.error('Error parsing tests:', error);
    return NextResponse.json({ error: 'Failed to read test reports' }, { status: 500 });
  }
}
