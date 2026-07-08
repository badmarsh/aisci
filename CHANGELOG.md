# Changelog

This file records completed platform and infrastructure work. Science progress is tracked separately in `research/robert/evidence-ledger.md`.

For open and in-progress tasks see `docs/ops/platform-backlog.md`.

---

## Completed — April 2026

| Priority | System | Issue | Resolution |
|---|---|---|---|
| P0 | DeerFlow | Live secret values reachable through local MCP config API | Kept localhost-only; documented auth/redaction requirement before LAN/remote exposure |
| P0 | DeerFlow | Docker socket and CLI auth dirs mounted into containers | Restricted network exposure; documented operational assumptions |
| P1 | DeerFlow | Agent roster not physics-oriented | Replaced with physics validation agents in live config |
| P1 | DeerFlow | Broken `rag_search`, `rag_manage`, `llm_council` tools | Removed from active config until implemented |
| P1 | DeerFlow | MCP paths reference missing `/home/ubuntu/deer-flow` | Switched to container paths and `/workspace/aisci` |
| P1 | DeerFlow | Missing Scite/Consensus/arXiv/INSPIRE integrations | Added after auth/path testing |
| P1 | DeerFlow | Default model used Vertex without visible credentials | OpenRouter Gemini Flash is now first model |
| P1 | Onyx | Physics persona has no tools or document sets | Live `Physics Validation Mode` now has Physics, Robert Boson Draft, HEP Phenomenology References, internal search, file reader, Python, URL opener, Scite, Consensus, arXiv, INSPIRE-HEP, and HEPData attached |
| P1 | Onyx | Missing arXiv/INSPIRE-HEP/HEPData tools | Read-only custom OpenAPI tools installed and attached to `Physics Validation Mode`; ATLAS 13 TeV records seeded into `HEP Phenomenology References` |
| P1 | Onyx | Runtime model-server stack did not match active Nomic 768 index | GPUs exposed to inference/indexing/ollama servers; runtime env aligned to `nomic-ai/nomic-embed-text-v1` / 768 dims |
| P2 | DeerFlow | Better Auth base URL missing | Set local frontend auth URL vars |
| P2 | DeerFlow | LangSmith metadata 403 noise | Cleared placeholder key; disabled tracing |
| P2 | Onyx | Stale Compose labels point to old path | Stack recreated from `~/aisci/deployment/onyx` |
| P2 | Onyx | Local Unstructured API not actually used by backend | Patched Onyx backend so `UnstructuredClient` receives `server_url=http://unstructured:8000` |
| P2 | Onyx | LiteLLM and Ollama stack unhealthy (`0/7` health) | Pulled Ollama models; disabled dead aliases |
| P2 | Onyx | Tsallis connector emitting stale OpenSearch no-op noise | Documented chunk parity gap from failed OpenSearch writes (missing chunk 4) |
| P2 | Onyx | Background process monitor reporting false positives | Kept workers as-is; tightened process-classification logic for `monitor_process_memory` |
| P2 | Both | Retrieval evaluation question set missing | Draft set created; run and record observed citations, latency, and failure modes before tuning |
