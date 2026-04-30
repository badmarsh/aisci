# Onyx Assessment - 2026-04-26

Current status note: persona and document-set alignment was updated on 2026-04-27. Prefer `docs/ops/onyx-rag-optimization-2026-04-27.md` for the current Onyx persona/tool state; this file preserves the original assessment context.

## Purpose

This Onyx instance is a local/private HEP physics validation workspace. Its role is to ingest Robert's paper and related literature, run RAG over curated physics sources, use Scite/Consensus for literature checks, and provide evidence-grounded support for symbolic checks, fits, plots, and referee-style reports.

## Original 2026-04-26 Diagnosis

- Stack is up: API server, background workers, Unstructured, LiteLLM, Postgres, OpenSearch, Vespa, Redis, MinIO, nginx, and related services are running.
- `/api/health` returns OK.
- Docling is removed from the active compose stack. Local Unstructured is back and healthy at `http://localhost:9560`.
- API container name is normal: `onyx-api_server-1`. The earlier hash-prefixed API container name was a Docker Compose replacement artifact.
- Compose labels still reference an older deployment path under `/home/ubuntu/onyx_data/...`; standardize on `/home/ubuntu/aisci/deployment/onyx` and recreate containers cleanly later.
- Ollama currently has no pulled models, while configs expose local Ollama models. Do not expose local models until they exist.
- `Physics Validation Mode` exists but has no tools and no document sets attached.
- `Science Deep-Dive Mode` has internal search, URL opening, Scite, Consensus, and the current Physics document set.
- The Physics document set currently contains only the boson probability function paper. `Tsallis_statistics` and `Gretenka - podklady` are active but not attached to that set.
- Search settings are inconsistent: the active DB/index settings use `nomic-ai/nomic-embed-text-v1` with 768 dimensions, multipass, and contextual RAG, while the live `.env` still had 384-dim MiniLM settings before cleanup.
- Background logs include repeated process-monitor false positives and stale OpenSearch `document_missing_exception` noise for Tsallis.

## Original Best Next Moves

1. Make `Physics Validation Mode` the primary Onyx persona.
2. Attach the Physics document set and tools: internal search, file reading, Python/code interpreter, URL opening, Scite, and Consensus.
3. Keep web search disabled by default for strict validation; enable it only for literature scouting.
4. Split knowledge into document sets:
   - Robert Boson Draft
   - HEP Phenomenology References
   - Validation Methods
   - Scratch/Admin
5. Keep local Unstructured as the production parser.
6. Treat Docling as an experimental parser only after the current workflow is stable.
7. Freeze embedding configuration to match the active `nomic-ai/nomic-embed-text-v1` 768-dim index and reindex once.
8. Reindex or reset the Tsallis connector to clear stale OpenSearch noise.
9. Recreate containers from `/home/ubuntu/aisci/deployment/onyx` so labels stop pointing at the old path.
10. Build a 20-30 question retrieval evaluation set before tuning `HYBRID_ALPHA`, rerank count, or contextual RAG.

## Applied After Assessment

- Local ignored Onyx `.env` was aligned to `nomic-ai/nomic-embed-text-v1` with 768 dimensions.
- Active parser path remains local Unstructured at `http://unstructured:8000`.
- `Physics Validation Mode` was promoted to the primary science persona and given local physics document sets plus internal search, file reader, Python/code interpreter, URL opening, Scite, and Consensus.
- `Science Deep-Dive Mode` was aligned for local-plus-external source curation.
- `Robert Boson Draft` and `HEP Phenomenology References` were seeded from existing connectors and attached to the science personas.
- No automatic reindex was started.

## Sources Checked

- Onyx docs: https://docs.onyx.app/deployment/overview
- Onyx deployment, indexing, agents, connectors/document sets, actions/MCP, Ollama setup, GitHub README, and relevant community discussion.
