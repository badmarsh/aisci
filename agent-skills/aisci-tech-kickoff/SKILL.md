---
name: aisci-tech-kickoff
description: Start a technical work session in /home/ubuntu/aisci by reading current project context, selecting a safe high-leverage task, and either implementing selected findings or producing an approval-gated plan.
---

# AiSci Tech Kickoff

Use this at the start of a tech-side coding session.

## Required Context

Read:

- `AGENTS.md`
- `README.md`
- `ACTION_PLAN.md`
- `docs/README.md`
- `docs/ops/platform-backlog.md`
- Latest relevant `docs/ops/*assessment*.md` and `docs/ops/*audit*.md`
- Relevant deployment files under `deployment/onyx/` or `deployment/deer-flow/`

Then inspect `git status --short` and preserve unrelated changes.
Use `agent-skills/git-worktree-guard/SKILL.md` when git status or history affects the task choice.

## Task Selection

Pick a small, high-leverage, non-destructive first task. Prefer:

1. Safety and secrets hygiene.
2. Documentation or backlog drift that blocks later agents.
3. Small config cleanup that does not touch secrets.
4. Patch plans for risky runtime work.
5. Verification-only checks that do not mutate data.

Do not run reindexing, container recreation, image rebuilds, large model pulls, destructive cleanup, credential changes, or live secret edits without explicit user approval.

## Before Edits

Tell the user the selected task and why it is the best first move. If it is a safe documentation/backlog cleanup, implement after stating the plan. If it needs approval, write the exact approval-gated commands and patch plan instead.

## Output

Report:

- Selected task and reasoning.
- Files changed.
- Verification performed.
- Next approval-gated commands, if relevant.
