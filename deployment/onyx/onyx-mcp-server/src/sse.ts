/**
 * Onyx MCP SSE Server
 * Entry point for the Onyx MCP Server using SSE transport
 */
import express from 'express';
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';
import { OnyxMcpServer } from './server.js';

const app = express();
const server = new OnyxMcpServer();
const messageEndpoint = process.env.MCP_MESSAGE_ENDPOINT || '/messages';

let transport: SSEServerTransport | null = null;

app.get('/sse', async (req, res) => {
  console.error('New SSE connection');
  transport = new SSEServerTransport(messageEndpoint, res);
  await server.run(transport);
});

app.post(['/messages', '/onyx/messages'], async (req, res) => {
  console.error('New message');
  if (transport) {
    await transport.handlePostMessage(req, res);
  } else {
    res.status(400).send('No active SSE session');
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.error(`Onyx MCP SSE Server running on port ${PORT}`);
  console.error(`SSE endpoint: http://localhost:${PORT}/sse`);
  console.error(`Message endpoint: http://localhost:${PORT}/messages`);
});
