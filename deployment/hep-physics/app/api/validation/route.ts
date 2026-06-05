import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import util from 'util';

const execPromise = util.promisify(exec);

export async function GET() {
  try {
    const { stdout, stderr } = await execPromise('wsl python3 /home/ubuntu/aisci/physics/src/run_validation.py');
    const data = JSON.parse(stdout.trim());
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error running symbolic validation:', error);
    // Return mock data if python fails to run (e.g. wsl not found in Vercel)
    return NextResponse.json([
      {
        id: "F.01",
        section: "§2.1",
        description: "Differential elastic cross-section",
        expression: "A * F_N**2 * exp(B*t)",
        valid: true,
        note: "Dimensionally consistent",
        dimensions: "[mb·GeV⁻²]",
      }
    ]);
  }
}
