# Agent Skills

This folder contains vendor-neutral workflow skills for agents working in this repository.
They are plain Markdown guides, not tied to any specific model, IDE, or CLI.

Use these skills by reading only the relevant `SKILL.md` for the current task. Do not bulk-load every skill unless the user asks for a broad process review.

## Skill Structure
All skills follow the `TEMPLATE.md` schema:
1. `## Read First`: Lists `AGENTS.md` and required canonical context.
2. `## Rules`: Hard boundaries and constraints.
3. `## Workflow`: Step-by-step execution guides.
4. `## Output & Approval Gates`: When to ask for permission and how to shape output.

## Available Skills

- `aisci-tech-kickoff` - start a technical work session, choose a safe first task, and execute or plan it.
- `analysis-handoff-router` - after analysis, offer implementation, targeted persistence, or a next-session prompt.
- `git-worktree-guard` - use git status/history safely for context while preserving unrelated changes.
- `platform-backlog-manager` - manage actionable platform work in `docs/ops/platform-backlog.md`.
- `researcher-docs-manager` - maintain high-signal research docs, separate physics from infra, clean stale working docs, and archive history.
- `aisci-ops-auditor` - audit Onyx, DeerFlow, MCP, Docker, models, and deployment docs/config.
- `secret-config-auditor` - review secrets, env handling, Docker socket exposure, auth mounts, and MCP config leaks.
- `mcp-integration-planner` - plan shared MCP/API integrations for literature and citation tools.
- `onyx-rag-eval-manager` - manage retrieval evaluation discipline for Onyx RAG tuning.
- `reproducible-physics-runner` - run physics validation scripts and store reproducible artifacts correctly.
- `science-report-writer` - write referee reports and science-facing summaries from ledger-supported evidence.
- `science-source-curator` - ingest and reconcile manuscript, PDF, literature, and data-table source evidence.
- `science-ledger-manager` - manage Robert science claims, evidence states, and next actions.
- `vendored-runtime-maintainer` - work safely in vendored DeerFlow/runtime trees and separate upstream code from local config.

## Common Rules

- Follow `AGENTS.md` first.
- Preserve unrelated user changes.
- Do not print secrets.
- Prefer existing canonical files over creating new Markdown files.
- Ask before promoting analysis suggestions into accepted task, decision, or evidence trackers.
