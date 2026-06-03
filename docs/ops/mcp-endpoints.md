# MCP Endpoints — Operational Status

Record tested and untested MCP/API endpoints here.
See `docs/decisions/2026-04-27-mcp-topology.md` for topology rationale.
Keep secrets out of this file.

## How Auth Works

**Scite** and **Consensus** both use OAuth 2.0. There are no static API keys to buy or save in your configuration files. You authorize via their respective web apps, which return a Bearer token:
1. Open the MCP OAuth flow (from within an MCP-aware client like Claude Desktop or Onyx's MCP chat bar)
2. Complete the sign-in in your browser
3. The token is issued to the client and passed per-request. The nginx proxy forwards it unchanged via `proxy_pass_header Authorization`.

**Key insight**: Both services work correctly as long as the caller uses the
right network route. Host-local clients use `http://127.0.0.1:8095`. DeerFlow
containers are attached to the `onyx_default` Docker network and use
`http://onyx-mcp-proxy:80`. The previous confusion in the backlog about
"missing API keys" was incorrect; Scite and Consensus need the OAuth flow
completed from a capable MCP client.

## Endpoint Status

| Endpoint | Service | Proxy Route | Auth Model | Status | Action |
|---|---|---|---|---|---|
| Scite | nginx MCP proxy | Host: `http://127.0.0.1:8095/scite/`; DeerFlow: `http://onyx-mcp-proxy:80/scite/` → `https://api.scite.ai/mcp` | OAuth Bearer — client must complete browser flow | Proxy reachable; OAuth required | Initiate from client, complete browser sign-in |
| Consensus | nginx MCP proxy | Host: `http://127.0.0.1:8095/consensus/`; DeerFlow: `http://onyx-mcp-proxy:80/consensus/` → `https://mcp.consensus.app/mcp/` | OAuth Bearer — client must complete browser flow | Proxy reachable; OAuth required | Initiate from client, complete browser sign-in |
| arXiv | Direct REST | `https://export.arxiv.org/api/query` | None (public) | ✅ Public | No proxy needed |
| INSPIRE-HEP | Direct REST | `https://inspirehep.net/api/` | None (public) | ✅ Public | No proxy needed |
| Semantic Scholar | nginx MCP proxy | Host: `http://127.0.0.1:8095/semanticscholar/graph/v1`; DeerFlow: `http://onyx-mcp-proxy:80/semanticscholar/graph/v1` → `https://api.semanticscholar.org/graph/v1` | `x-api-key: SEMANTICSCHOLAR_API_KEY` | ✅ Key approved 2026-06-02 | Three separate APIs: Academic Graph (paper/author lookup + citation traversal), Recommendations, Datasets — see `docs/ops/semantic-scholar-asta-api.md` |
| Asta (Allen AI) | nginx MCP proxy | Host: `http://127.0.0.1:8095/asta/`; DeerFlow: `http://onyx-mcp-proxy:80/asta/` → `https://asta-tools.allen.ai/mcp/v1/` | `x-api-key: ASTA_API_KEY` | ✅ Key approved 2026-06-02 | MCP JSON-RPC protocol (not REST). Key tools: `get_paper`, `search_snippets` (full-text passage search, 200M+ papers). Use for finding equations/methods inside paper bodies — see `docs/ops/semantic-scholar-asta-api.md` |
| Onyx MCP | Local SSE | Host: `http://127.0.0.1:8095/onyx/sse`; DeerFlow: `http://onyx-mcp-proxy:80/onyx/sse` | Server-side `ONYX_API_KEY` injected into `onyx_mcp_server` | Active | 2026-05-06: DeerFlow gateway can resolve and connect to `onyx-mcp-proxy:80`; host port stays bound to `127.0.0.1` |
| Onyx RAG API | Internal | `http://localhost:3000/api/` externally, `http://api_server:8080/` inside Docker | Bearer ONYX_API_KEY | ✅ Search active | 2026-05-02: internal MCP bridge must use `http://api_server:8080` without `/api`; model servers and Ollama must be running for retrieval/generation paths |

| OpenSearch | Internal | `https://localhost:9200` | admin / OPENSEARCH_ADMIN_PASSWORD | ✅ Active — Alibaba parity green | Keep `deployment/helper/onyx_opensearch_cutover.py --json` as the regression gate after future reindexes; active index `danswer_chunk_alibaba_nlp_gte_qwen2_1_5b_instruct` matches DB chunk parity |
