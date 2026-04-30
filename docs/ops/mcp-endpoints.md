# MCP Endpoints — Operational Status

Record tested and untested MCP/API endpoints here.
See `docs/decisions/2026-04-27-mcp-topology.md` for topology rationale.
Keep secrets out of this file.

| Endpoint | Service | Route | Auth | Status | Notes |
|---|---|---|---|---|---|
| Scite | nginx MCP proxy | /mcp/scite | API key (not injected) | ❌ Untested | Key injection open in platform-backlog.md |
| Consensus | nginx MCP proxy | /mcp/consensus | API key (not injected) | ❌ Untested | Key injection open in platform-backlog.md |
| arXiv | Direct | public | None | ⚠️ Unverified | No MCP route documented yet |
| INSPIRE-HEP | Direct | public | None | ⚠️ Unverified | No MCP route documented yet |
| Onyx RAG API | Internal | localhost:8095 | Bearer token | ✅ Active | Document sets and personas operational |
