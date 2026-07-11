import { NextResponse } from 'next/server';
import fs from 'fs/promises';

export async function GET() {
  try {
    const filePath = '/home/ubuntu/aisci/research/robert/evidence-ledger.md';
    let content = '';
    try {
      content = await fs.readFile(filePath, 'utf-8');
    } catch (err) {
      console.warn("Could not read evidence ledger, returning empty array", err);
      return NextResponse.json([]);
    }
    
    const lines = content.split('\n');
    let inTable = false;
    const claims = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (line.startsWith('| Claim |')) {
        inTable = true;
        i++; // skip separator
        continue;
      }
      
      if (inTable) {
        if (!line.startsWith('|')) break;
        
        const cols = line.split('|').map(c => c.trim());
        if (cols.length >= 6) {
          const claim = cols[1].replace(/\*\*/g, '').replace(/`/g, '');
          const rawStatus = cols[4].toLowerCase();
          
          let status = 'open';
          if (rawStatus.includes('sanity')) status = 'sanity';
          else if (rawStatus.includes('support') || rawStatus.includes('confirm')) status = 'supported';
          else if (rawStatus.includes('refut')) status = 'refuted';
          
          const chiMatch = cols[3].match(/chi2\/ndf\s*(?:=|:)?\s*([\d.]+)/i) || cols[1].match(/chi2\/ndf\s*(?:=|:)?\s*([\d.]+)/i);
          const chi2ndf = chiMatch ? parseFloat(chiMatch[1]) : null;
          
          claims.push({
            id: `CLM-${String(claims.length + 1).padStart(3, '0')}`,
            claim: claim.substring(0, 150) + (claim.length > 150 ? '...' : ''),
            status,
            updated: new Date().toISOString().replace('T', ' ').substring(0, 16) + ' UTC',
            source: 'evidence-ledger.md',
            chi2ndf
          });
        }
      }
    }
    
    return NextResponse.json(claims);
  } catch (error) {
    console.error('Error parsing evidence ledger:', error);
    return NextResponse.json({ error: 'Failed to read evidence ledger' }, { status: 500 });
  }
}
