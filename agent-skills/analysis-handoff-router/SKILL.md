---
name: analysis-handoff-router
description: Route findings after an analysis, audit, review, or research pass by offering implementation, targeted persistence into exact project files, or a next-session implementation prompt without auto-promoting suggestions.
---

# Analysis Handoff Router

Use this after analysis produces findings or recommendations.

## Core Rule

Do not automatically write all suggestions into canonical files. Offer the user three choices:

1. Implement selected findings now, respecting exclusions.
2. Write selected findings into the exact document or documents where they belong.
3. Write a concise prompt for a fresh agent/session to implement selected findings later.

## Target Mapping

Name exact targets when offering persistence:

- Platform, deployment, MCP, Docker, model, security, tooling tasks: `docs/ops/platform-backlog.md`
- Platform rationale or operational notes: an existing relevant `docs/ops/*.md`
- Durable architecture or process decisions: `docs/decisions/YYYY-MM-DD-*.md`
- Science claim status: `research/robert/evidence-ledger.md`
- Science tasks: `research/robert/next-actions.md`
- High-level project tracking only: `ACTION_PLAN.md`

Prefer existing files. Ask before creating a new dated analysis file.

## Handoff Prompt Format

When writing a next-session prompt, include:

- Working directory.
- Files to read first.
- Findings selected for implementation.
- Exclusions.
- Safety constraints.
- Expected deliverables.

Keep the prompt short enough to paste directly into a new session.
