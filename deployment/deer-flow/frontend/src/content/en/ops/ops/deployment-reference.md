# Deployment & Infrastructure Reference

This document contains technical details for the AiSci workspace infrastructure. Researchers should refer to the main `README.md` for active research status.

## System Components

| Service | Internal URL | Purpose |
|---|---|---|
| **Onyx UI** | `http://localhost:3000` | Private RAG, document ingestion, and literature search. |
| **DeerFlow** | `http://localhost:2026` | Multi-agent orchestration and tool execution. |
| **LiteLLM Proxy** | `http://localhost:4000` | LLM routing and key management. |
| **MCP Proxy** | `http://localhost:8095` | Gateway for research tools (Consensus, Scite, etc.). |
| **Unstructured** | `http://localhost:9560` | Local PDF parsing and extraction. |

## Docker Stack Details

The workspace runs on a multi-container Docker stack managed via `docker-compose.yml` in the `deployment/` directories.

- **Onyx Stack:** Located in `deployment/onyx/`. Uses Vespa/OpenSearch for vector storage.
- **DeerFlow Stack:** Located in `deployment/deer-flow/`.
- **GPU Resources:** Inference and indexing servers are configured to use the host RTX 3090.

## Operational Commands

```bash
# Check container status
docker ps

# Check Ollama models
docker exec onyx-ollama-1 ollama list

# Check DeerFlow logs
docker logs -f deer-flow-gateway
```

## Maintenance Notes

- Live `.env` files and active configurations are gitignored.
- Secret-bearing notes belong in `docs/ops/private/`.
- For OpenSearch migration status, see `docs/ops/onyx-rag-optimization-2026-04-27.md`.
