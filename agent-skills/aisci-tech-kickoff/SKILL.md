---
name: aisci-tech-kickoff
description: Start a technical work session in /home/ubuntu/aisci by reading current project context, selecting a safe high-leverage task, and either implementing selected findings or producing an approval-gated plan. Use for single-task session kickoff only — not for full structured audits.
---

# AiSci Tech Kickoff

Use this at the start of a tech-side coding session.

## Read First

Read:

- `AGENTS.md`
- `README.md`
- `ACTION_PLAN.md`
- `docs/README.md`
- `docs/ops/platform-backlog.md`
- Latest relevant `docs/ops/*assessment*.md` and `docs/ops/*audit*.md`
- Relevant deployment files under `deployment/onyx/` or `deployment/deer-flow/`
- `docs/decisions/2026-04-26-system-boundaries.md`
  (reminder: Onyx = curated evidence, DeerFlow = orchestration,
  Repo = durable record — these are not interchangeable)

Then inspect `git status --short` and preserve unrelated changes.
Use `agent-skills/git-worktree-guard/SKILL.md` when git status or history affects the task choice.

## Workflow

1. **Agent State Check**: Run `python3 scripts/hooks/verify_agent_state.py`. If it fails, fix the environment before proceeding.
2. Pick a small, high-leverage, non-destructive first task. Prefer:

1. Safety and secrets hygiene.
2. Documentation or backlog drift that blocks later agents.
3. Small config cleanup that does not touch secrets.
4. Patch plans for risky runtime work.
5. Verification-only checks that do not mutate data.

Do not run reindexing, container recreation, image rebuilds, large model pulls, destructive cleanup, credential changes, or live secret edits without explicit user approval.

## Before Edits

Tell the user the selected task and why it is the best first move. If it is a safe documentation/backlog cleanup, implement after stating the plan. If it needs approval, write the exact approval-gated commands and patch plan instead.

## Output & Approval Gates

Report:

- Selected task and reasoning.
- Files changed.
- Verification performed.
- Next approval-gated commands, if relevant.
- After reporting findings, offer the three continuations from
  `agent-skills/analysis-handoff-router/SKILL.md`:
  implement now, persist to exact files, or write a next-session prompt.
