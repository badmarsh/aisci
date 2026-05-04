---
name: mcp-integration-planner
description: Plan shared MCP or direct API integrations for research and citation tools such as Scite, Consensus, arXiv, INSPIRE-HEP, HEPData, Semantic Scholar, and OpenAlex without committing credentials.
---

# MCP Integration Planner

## Read First

- `AGENTS.md`

Use this when planning or documenting MCP/API integrations.

## Rules

- Prefer project-level shared config over IDE-specific setup.
- Keep credentials out of git.
- Document tested endpoints and caveats in `docs/ops/`.
- Use Onyx for curated source-grounded retrieval.
- Expose direct tools to coding/orchestration agents when they need task-specific evidence.

## Workflow

1. Identify the tool and use case.
2. Decide whether it belongs in Onyx, DeerFlow, direct agent tooling, or a shared local proxy.
3. Document auth needs without writing secret values.
4. Provide a test plan from inside the relevant container or host context.
5. Add user-approved actionable tasks to `docs/ops/platform-backlog.md`.
6. Add durable topology decisions to `docs/decisions/` only when stable.

## Output & Approval Gates

Ask before:

- Adding real keys.
- Restarting services.
- Exposing services beyond localhost.
- Installing new MCP servers globally.
- Changing shared proxy behavior.
