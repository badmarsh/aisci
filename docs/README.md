# AiSci Documentation Map

This folder is for project-wide documentation. Keep platform implementation details separate from Robert's science workflow.

## Folders

- `ops/` - deployment notes, stack assessments, troubleshooting, and platform backlog for Onyx, DeerFlow, Docker, MCP, models, and secrets handling.
- `decisions/` - short architecture decision records. These explain why the project chose a direction.
- `archive/` - older brainstorming and historical summaries kept for context.

Science-facing work belongs under `research/`, not here. The `research/robert/` files should describe scientific questions, evidence, validation criteria, fits, reports, and reproducible runs without depending on Onyx or DeerFlow internals.

## Current Priority

For current project-wide priorities, always refer to the root [`../ACTION_PLAN.md`](../ACTION_PLAN.md).

## Work Tracking

Use GitHub Issues and Pull Requests for active implementation, review, and follow-up history. Keep durable current-state facts in the canonical repo docs:

- Platform state and runbooks: `docs/ops/`
- Architecture and process decisions: `docs/decisions/`
- Science evidence and tasks: `research/robert/`

Do not create new backlog/status markdown files by default. For accepted work, open or update an Issue and point it at the exact canonical file that should change.

## Science Evidence Standard

Scientific claims should be interpreted through `docs/decisions/2026-04-26-science-evidence-standards.md` and tracked in `research/robert/evidence-ledger.md`. Local scripts are sanity checks until full data, exact manuscript references, reproducible outputs, and literature context are attached.
