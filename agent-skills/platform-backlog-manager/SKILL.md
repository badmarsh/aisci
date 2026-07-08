---
name: platform-backlog-manager
description: Manage actionable platform, deployment, MCP, Docker, model, security, and tooling tasks in docs/ops/platform-backlog.md, including listing, deduping, adding, updating status, and preparing implementation prompts.
---

# Platform Backlog Manager

## Read First

- `AGENTS.md`

Use this when working with `docs/ops/platform-backlog.md`.

## Workflow

- `list`: summarize open items by priority and system.
- `add`: add user-approved actionable findings.
- `dedupe`: merge overlapping rows and preserve the best evidence.
- `update-status`: change status after implementation or verification.
- `suggest-from-analysis`: propose backlog rows from an analysis, but ask before writing.
- `make-implementation-prompt`: create a fresh-session prompt for selected rows.

## Rules

- Read `AGENTS.md` and `docs/ops/platform-backlog.md` first.
- For newly accepted active work, prefer a GitHub Issue over adding long-lived
  detail to `docs/ops/platform-backlog.md`. The backlog should hold compact
  canonical state and links/routing, not full execution history.
- Check relevant docs before adding rows, especially `docs/ops/*assessment*.md`, `docs/ops/*audit*.md`, and `ACTION_PLAN.md`.
- Avoid duplicate rows. Update existing rows when possible.
- Keep rows concise and actionable.
- Do not put science claims or fit conclusions here.
- Do not mark an item `Done` without evidence from files, commands, or user confirmation.
- Do not create a new markdown backlog or audit report when the right durable
  action is a GitHub Issue plus a targeted edit to an existing canonical doc.

## Output & Approval Gates

Use the existing table shape:

```md
| Priority | System | Issue | Why It Matters | Next Action | Status |
```

Statuses should be plain and specific, such as `Open`, `Partially done`, `Blocked`, or `Done`.

## Output & Approval Gates

When the user asks to implement backlog findings in bulk:

- Respect exclusions.
- Start with non-destructive changes.
- Pause for approval before restarting containers, reindexing, rebuilding images, pulling large models, deleting data, or touching secrets.
