---
name: aisci-ops-auditor
description: Audit the technical architecture and operations of AiSci, including Onyx, DeerFlow, MCP, Docker, LiteLLM, models, paths, deployment docs, and security-sensitive config.
---

# AiSci Ops Auditor

Use this for architecture, platform, or operations analysis.

## Scope

Focus on:

- Onyx deployment and RAG configuration.
- DeerFlow orchestration, sandboxing, gateway, and MCP setup.
- Docker compose files and mounted paths.
- LiteLLM, Ollama, model names, and embedding/rerank settings.
- MCP proxy and direct research tool integrations.
- Documentation drift between `README.md`, `ACTION_PLAN.md`, `docs/ops/`, and deployment files.
- Security-sensitive exposure, but use `secret-config-auditor` for a deeper secret review.

## Read First

- `AGENTS.md`
- `README.md`
- `ACTION_PLAN.md`
- `docs/README.md`
- `docs/ops/platform-backlog.md`
- Relevant `docs/ops/*.md`
- `docs/decisions/*.md`
- Relevant files under `deployment/onyx/` and `deployment/deer-flow/`

## Output

Produce findings with:

- Severity or priority.
- Evidence file path and line where possible.
- Impact.
- Suggested next action.
- Whether the action is safe to implement now or needs approval.

Then use `analysis-handoff-router` behavior: offer implementation, targeted persistence, or a next-session prompt.
