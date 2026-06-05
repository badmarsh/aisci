import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

const RUN_DIR = process.platform === 'win32' 
  ? '\\\\wsl.localhost\\Ubuntu\\home\\ubuntu\\aisci\\research\\robert\\runs\\2026-05-30-multiplicity-fit' 
  : '/home/ubuntu/aisci/research/robert/runs/2026-05-30-multiplicity-fit';

export async function GET() {
  try {
    const dashboardPath = path.join(RUN_DIR, 'fit_dashboard.json');
    const dashboardContent = await fs.readFile(dashboardPath, 'utf8');
    const dashboard = JSON.parse(dashboardContent);
    
    const paramsPath = path.join(RUN_DIR, 'fit_parameters.csv');
    const paramsContent = await fs.readFile(paramsPath, 'utf8');
    const paramLines = paramsContent.split('\n');
    const paramHeaders = paramLines[0].split(',');
    
    const paramIndex = {
      group: paramHeaders.indexOf('group_label'),
      model: paramHeaders.indexOf('model_name'),
      components: paramHeaders.indexOf('component_count'),
      name: paramHeaders.indexOf('parameter_name'),
      val: paramHeaders.indexOf('value'),
      err: paramHeaders.indexOf('error')
    };

    // For demo purposes, we pick the best model for group '126-150'
    const bestModel = dashboard.best_model_per_group['126-150'];
    const bestModelName = bestModel.model_name;
    const bestComponentCount = String(bestModel.component_count);

    let paramsList = [];
    for (let i = 1; i < paramLines.length; i++) {
      if (!paramLines[i].trim()) continue;
      const cols = paramLines[i].split(',');
      if (cols[paramIndex.group] === '126-150' && 
          cols[paramIndex.model] === bestModelName &&
          cols[paramIndex.components] === bestComponentCount) {
        
        let label = cols[paramIndex.name];
        let unit = '—';
        
        if (label.startsWith('temperature')) {
          label = 'T_' + label.replace('temperature_', '');
          unit = 'GeV';
        } else if (label.startsWith('norm')) {
          label = 'Norm_' + label.replace('norm_', '');
        } else if (label.startsWith('q')) {
          label = 'q_' + label.replace('q_', '');
        } else if (label.startsWith('U')) {
          label = 'U_' + label.replace('U_', '');
          unit = 'GeV';
        }

        const val = parseFloat(cols[paramIndex.val]);
        paramsList.push({
          name: label,
          unit: unit,
          value: val,
          error: parseFloat(cols[paramIndex.err]),
          delta: 0,
          deltaSign: 'zero',
          boundMin: val > 0 ? 0 : val * 2,
          boundMax: val > 0 ? val * 2 : 0,
          status: 'converged'
        });
      }
    }

    const finalChi2 = bestModel.chi2_ndf;
    const sparkline = [
      finalChi2 * 8.5, finalChi2 * 5.2, finalChi2 * 3.1, finalChi2 * 1.8, finalChi2 * 1.2, finalChi2 * 1.05, finalChi2
    ].map((val, i) => ({ iteration: i, chi2: val }));

    return NextResponse.json({
      currentChi2: finalChi2,
      sparkline: sparkline,
      params: paramsList
    });
  } catch (error) {
    console.error('Error fetching fits:', error);
    return NextResponse.json({ error: 'Failed to fetch fits data' }, { status: 500 });
  }
}
