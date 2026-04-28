---
name: working-docs-curator
description: Reconcile active project docs with current repo state by removing stale implemented issues, preserving durable one- or two-sentence summaries, updating canonical trackers, and archiving historical detail.
---

# Working Docs Curator

Use this when active docs are stale, duplicated, too verbose, or mixed with already-implemented work.

## Read First

- `AGENTS.md`
- `README.md`
- `ACTION_PLAN.md`
- `docs/README.md`
- `docs/ops/platform-backlog.md`
- Relevant files in `docs/ops/` and `docs/decisions/`
- Relevant `research/robert/` files for science-facing content

## Curating Rules

- Do not delete scientific evidence or claim-status history.
- Do not move platform details into science files.
- Do not move science claims into `docs/ops/`.
- Prefer editing existing active docs over creating new files.
- Keep active docs short and current.
- Move historical detail to `docs/archive/` only when it is no longer current.
- Add a legacy note when archiving.

## Workflow

1. Identify the canonical file for each topic.
2. Compare active docs against current repo state, config, and git history when useful.
3. For implemented items, update status or compress the note to a durable summary.
4. For stale or duplicated detail, keep the crucial one or two sentences in the active doc and archive the rest.
5. Update `docs/ops/platform-backlog.md` only for user-approved actionable platform work.
6. Report what changed and what still needs review.

## New Files

Ask before creating a new Markdown file. A new file is justified only if an existing canonical doc cannot hold the information clearly.
