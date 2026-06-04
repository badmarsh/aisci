/**
 * Dexter HTTP Microservice — exposes Dexter as a REST endpoint.
 *
 * POST /research  { query: string }  →  { answer: string, duration_ms: number }
 * GET  /health                       →  { status: "ok" }
 *
 * Usage:
 *   cd dexter && bun run src/gateway/dexter-server.ts
 */

import { config } from 'dotenv';
config({ quiet: true });

import { Agent } from '../agent/index.js';

const PORT = parseInt(process.env.DEXTER_SERVER_PORT || '18790', 10);
const HOST = process.env.DEXTER_SERVER_HOST || '127.0.0.1';

interface ResearchRequest {
  query: string;
  maxIterations?: number;
}

interface ResearchResponse {
  answer: string;
  iterations: number;
  duration_ms: number;
  success: boolean;
}

async function handleResearch(req: ResearchRequest): Promise<ResearchResponse> {
  const startTime = Date.now();
  const agent = await Agent.create({
    maxIterations: req.maxIterations ?? 15,
  });

  let answer = '';
  let iterations = 0;

  for await (const event of agent.run(req.query)) {
    if (event.type === 'done') {
      answer = event.answer;
      iterations = event.iterations;
    }
  }

  return {
    answer,
    iterations,
    duration_ms: Date.now() - startTime,
    success: !!answer && !answer.startsWith('Error:'),
  };
}

const server = Bun.serve({
  hostname: HOST,
  port: PORT,
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);

    // Health check
    if (url.pathname === '/health' && request.method === 'GET') {
      return Response.json({ status: 'ok', service: 'dexter' });
    }

    // Research endpoint
    if (url.pathname === '/research' && request.method === 'POST') {
      try {
        const body = await request.json() as ResearchRequest;
        if (!body.query || typeof body.query !== 'string') {
          return Response.json({ error: 'Missing required field: query' }, { status: 400 });
        }

        const result = await handleResearch(body);
        return Response.json(result);
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        return Response.json({ error: message, success: false }, { status: 500 });
      }
    }

    return Response.json({ error: 'Not found. POST /research or GET /health' }, { status: 404 });
  },
});

console.log(`🐍 Dexter server running on http://${HOST}:${PORT}`);
console.log(`  POST /research  — submit a financial research query`);
console.log(`  GET  /health    — health check`);
