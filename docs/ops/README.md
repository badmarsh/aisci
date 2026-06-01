# Ops Documentation Index

Operational documentation for the AiSci platform: the Onyx RAG stack, DeerFlow
orchestration, Docker deployment, MCP bridges, models, and secrets handling.
Scientific claims and fit conclusions do **not** belong here — those live in
`research/robert/` (see the root `docs/README.md` for the project-wide map).

GitHub Issues and Pull Requests are the active execution queue. These files are
the durable current-state reference; link issues from them when work is open.

## Canonical Sources (read these first)

| Topic | Canonical file |
|---|---|
| Open work / operational state | [`platform-backlog.md`](platform-backlog.md) |
| Deployment shape, services, repo layout | [`deployment-reference.md`](deployment-reference.md) |
| Onyx runtime config (embeddings, LiteLLM, Craft, MCP) | [`onyx-configure.md`](onyx-configure.md) |
| Onyx personas & document sets (live registry) | [`onyx-persona-ids.md`](onyx-persona-ids.md) |
| MCP/API endpoint status & auth | [`mcp-endpoints.md`](mcp-endpoints.md) |
| Failure modes & fixes | [`troubleshooting.md`](troubleshooting.md) |

When two files disagree, the file listed above for that topic wins; update or
delete the stale copy in the other file.

## All Files by Purpose

### Platform state & deployment
- [`platform-backlog.md`](platform-backlog.md) — prioritized operational
  backlog and audit log. Source of truth for what is open vs done.
- [`deployment-reference.md`](deployment-reference.md) — live services, host
  URLs, actual repository layout, operational commands, maintenance notes.
- [`critical-components.md`](critical-components.md) — operational component map
  (physics scripts, MCP services, persona, GPU, directory structure).

### Onyx runtime & RAG
- [`onyx-configure.md`](onyx-configure.md) — canonical Onyx runtime reference:
  embedding model, LiteLLM RAG routes, multimodal PDF indexing, secrets/env,
  MCP routes, Celery Beat, verification commands.
- [`onyx-persona-ids.md`](onyx-persona-ids.md) — authoritative live persona /
  document-set / tool-ID registry. Keep in sync with the running instance.
- [`onyx-rag-optimization-2026-04-27.md`](onyx-rag-optimization-2026-04-27.md) —
  RAG-vs-canon source-routing boundary and retrieval-stack decisions. **Dated
  reference**: its persona-state section predates the v4 transition — defer to
  `onyx-persona-ids.md` for current persona IDs.
- [`rag-evaluation-set.md`](rag-evaluation-set.md) — canonical RAG retrieval
  test questions and baseline run results.

### MCP & endpoints
- [`mcp-endpoints.md`](mcp-endpoints.md) — tested/untested MCP & API endpoints,
  proxy routes, and OAuth auth model.

### Troubleshooting & audits
- [`troubleshooting.md`](troubleshooting.md) — runbook for known Onyx, DeerFlow,
  MCP, and sandbox failure modes plus regression gates.
- [`agent-skills-audit-report.md`](agent-skills-audit-report.md) — point-in-time
  `SKILL.md` compliance audit (2026-05-06).
- [`gemini-audit-prompt.md`](gemini-audit-prompt.md) — reusable prompt for a
  full infrastructure/documentation audit.

### Handoff & secrets
- [`next-session-prompt.md`](next-session-prompt.md) — ready-to-paste session
  bootstrap prompts (Platform/Ops and Science Workflow).
- [`secrets-and-deployment-notes.template.md`](secrets-and-deployment-notes.template.md)
  — secret-free template. Real secrets/private notes live in the gitignored
  `docs/ops/private/`.

## Conventions

- Keep secrets out of every tracked file here. Variable names, paths, and commit
  SHAs are fine; literal keys/tokens are not.
- Do not create new backlog/status markdown files by default — open or update a
  GitHub Issue and point it at the canonical file that should change.
- Date dated references in the title or a `_Last updated:_` line so future
  readers can judge staleness at a glance.
