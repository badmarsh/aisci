# DeerFlow Assessment - 2026-04-26

## Purpose

DeerFlow should be the orchestration and execution layer for Robert's physics workflow. It should coordinate literature scouting, formula extraction, numerical checks, fitting, plotting, and referee-style reports while Onyx remains the curated evidence/RAG layer.

## Live Status

- DeerFlow is running at `http://localhost:2026`.
- Gateway health is OK.
- Active containers: `deer-flow-nginx`, `deer-flow-frontend`, `deer-flow-gateway`, `deer-flow-langgraph`.
- Container labels point to the current compose file under `/home/ubuntu/aisci/deployment/deer-flow`.
- Generated sandbox containers named like `openclaw-sbx-agent-orchestrator-*` are expected for sandbox execution.

## Main Problems

- `config.yaml` was mostly legal/business oriented instead of physics oriented.
- Default model was fragile: first model was Vertex Gemini, but runtime credentials were not present.
- Local Ollama models were listed but not available because the Onyx/Ollama side has no pulled models.
- `rag_search`, `rag_manage`, and `llm_council` pointed to missing modules inside the containers.
- `agents/SOUL.md` describes a local RAG-first searcher, but its required RAG tools are not available.
- MCP config had path drift: some paths pointed to `/home/ubuntu/deer-flow`, which does not exist inside containers.
- MCP setup lacks Scite, Consensus, arXiv, and INSPIRE-HEP integrations.
- Brave MCP expected `BRAVE_API_KEY` while the local env used `BRAVE_SEARCH_API_KEY`.
- Logs showed invalid YAML front matter in the Bootstrap skill.
- Frontend logs warned that `BETTER_AUTH_BASE_URL` was missing.
- LangGraph is running a development/in-memory server and warns about SQLite checkpointer cleanup/pruning.
- Direct `docker compose` from the docker folder fails unless deploy-script env vars are exported.
- Security risk: the stack mounts Docker socket and local CLI auth dirs, has permissive CORS, and the MCP config API exposed resolved secret values locally.

## Best Next Moves

1. Replace generic/legal agents with physics workflow agents.
2. Add a Robert physics validation custom skill.
3. Make the first/default model a known-working OpenRouter model.
4. Remove broken RAG/council tool entries until implemented.
5. Fix MCP paths to container-visible locations.
6. Wire Scite, Consensus, arXiv, and INSPIRE-HEP as explicit tools after auth is tested from inside the gateway container.
7. Use DeerFlow sandbox for reproducible computation only. Store runs under `research/robert/runs/YYYY-MM-DD-*`.
8. Keep DeerFlow reachable from localhost only until auth and secret exposure are hardened.

## Applied After Assessment

- Replaced the live DeerFlow agent roster with Robert physics workflow agents.
- Changed the first/default model to OpenRouter Gemini Flash.
- Replaced hardcoded Ollama container IPs with `host.docker.internal`.
- Removed broken `rag_search`, `rag_manage`, and `llm_council` active tool entries.
- Fixed MCP filesystem/sqlite paths and added `/workspace/aisci` as the mounted project workspace.
- Added `robert-physics-validation` custom skill.
- Fixed Bootstrap skill YAML front matter.
- Added Better Auth URL variables to the ignored frontend env.
- Disabled noisy LangSmith metadata attempts caused by a placeholder key.
- Recreated gateway/langgraph/frontend containers and restarted nginx; health is OK.

## Sources Checked

- DeerFlow repo: https://github.com/bytedance/deer-flow
- DeerFlow docs: https://deerflow.tech
- Config docs: https://github.com/bytedance/deer-flow/blob/main/backend/docs/CONFIGURATION.md
- MCP docs: https://github.com/bytedance/deer-flow/blob/main/backend/docs/MCP_SERVER.md
- Community signal: https://www.reddit.com/r/LocalLLaMA/comments/1rkdue4/deerflow_20_from_bytedance_looks_interesting_for/
