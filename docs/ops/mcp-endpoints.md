# MCP Endpoints — Operational Status

Record tested and untested MCP/API endpoints here.
See `docs/decisions/2026-04-27-mcp-topology.md` for topology rationale.
Keep secrets out of this file.

## How Auth Works

**Scite** and **Consensus** both use OAuth 2.0. There are no static API keys to buy or save in your configuration files. You authorize via their respective web apps, which return a Bearer token:
1. Open the MCP OAuth flow (from within an MCP-aware client like Claude Desktop or Onyx's MCP chat bar)
2. Complete the sign-in in your browser
3. The token is issued to the client and passed per-request. The nginx proxy forwards it unchanged via `proxy_pass_header Authorization`.

**Key insight**: Both services work correctly as long as Onyx is on localhost — the nginx proxy at `http://127.0.0.1:8095` is reachable by any local process. The previous confusion in the backlog about "missing API keys" was incorrect; they just need the OAuth flow completed from a capable MCP client.

## Endpoint Status

| Endpoint | Service | Proxy Route | Auth Model | Status | Action |
|---|---|---|---|---|---|
| Scite | nginx MCP proxy | `http://127.0.0.1:8095/scite/` → `https://api.scite.ai/mcp` | OAuth Bearer — client must complete browser flow | ⚠️ Proxy reachable; needs OAuth flow | Initiate from client, complete browser sign-in |
| Consensus | nginx MCP proxy | `http://127.0.0.1:8095/consensus/` → `https://mcp.consensus.app/mcp/` | OAuth Bearer — client must complete browser flow | ⚠️ Proxy reachable; needs OAuth flow | Initiate from client, complete browser sign-in |
| arXiv | Direct REST | `https://export.arxiv.org/api/query` | None (public) | ✅ Public | No proxy needed |
| INSPIRE-HEP | Direct REST | `https://inspirehep.net/api/` | None (public) | ✅ Public | No proxy needed |
| Onyx MCP | Local SSE | `http://127.0.0.1:8095/onyx/sse` | Server-side ONYX_API_KEY injected into `onyx_mcp_server` | ✅ Active | 2026-05-02: `search_onyx` verified over SSE. 2026-05-04: `chat_with_onyx` generation unblocked after LiteLLM quota models removed and UI visibility fixed. DeerFlow uses `http://host.docker.internal:8095/onyx/sse` |
| Onyx RAG API | Internal | `http://localhost:3000/api/` externally, `http://api_server:8080/` inside Docker | Bearer ONYX_API_KEY | ✅ Search active | 2026-05-02: internal MCP bridge must use `http://api_server:8080` without `/api`; model servers and Ollama must be running for retrieval/generation paths |

| OpenSearch | Internal | `https://localhost:9200` | admin / OPENSEARCH_ADMIN_PASSWORD | ✅ Active — Alibaba parity green | Keep `deployment/helper/onyx_opensearch_cutover.py --json` as the regression gate after future reindexes; active index `danswer_chunk_alibaba_nlp_gte_qwen2_1_5b_instruct` matches DB chunk parity |
