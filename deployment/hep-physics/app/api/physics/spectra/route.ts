import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

const RUN_DIR = process.platform === 'win32' 
  ? '\\\\wsl.localhost\\Ubuntu\\home\\ubuntu\\aisci\\research\\robert\\runs\\2026-05-30-multiplicity-fit' 
  : '/home/ubuntu/aisci/research/robert/runs/2026-05-30-multiplicity-fit';

export async function GET() {
  try {
    const csvPath = path.join(RUN_DIR, 'hepdata_pt_spectra.csv');
    const content = await fs.readFile(csvPath, 'utf8');
    const lines = content.split('\n');
    const header = lines[0].split(',');
    
    // Find column indices
    const ptCenterIdx = header.indexOf('pt_center_gev');
    const yieldIdx = header.indexOf('yield_value');
    const binIdx = header.indexOf('manuscript_bin');
    
    // Group by bin
    const datasets: Record<string, { pt: number, dN: number }[]> = {};
    
    for (let i = 1; i < lines.length; i++) {
      if (!lines[i].trim()) continue;
      const cols = lines[i].split(',');
      const pt = parseFloat(cols[ptCenterIdx]);
      const dN = parseFloat(cols[yieldIdx]);
      const bin = cols[binIdx];
      
      if (!bin) continue;
      
      if (!datasets[bin]) {
        datasets[bin] = [];
      }
      
      if (!isNaN(pt) && !isNaN(dN)) {
        datasets[bin].push({
          pt: pt,
          dN: dN
        });
      }
    }
    
    const formattedDatasets: Record<string, any> = {};
    
    // Next.js config uses CSS vars for these chart colors
    const colors = ["var(--chart-1)", "var(--chart-2)", "var(--chart-3)", "var(--chart-4)", "var(--chart-5)"];
    let colorIdx = 0;
    
    for (const bin of Object.keys(datasets).sort()) {
      formattedDatasets[`bin_${bin}`] = {
        label: `ALICE 13 TeV pp (Mult ${bin})`,
        ref: "HEPData ins1735345",
        color: colors[colorIdx % colors.length],
        data: datasets[bin]
      };
      colorIdx++;
    }
    
    return NextResponse.json(formattedDatasets);
  } catch (error) {
    console.error('Error fetching spectra:', error);
    return NextResponse.json({ error: 'Failed to fetch spectra data' }, { status: 500 });
  }
}
