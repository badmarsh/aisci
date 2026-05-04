---
name: vendored-runtime-maintainer
description: Work safely in vendored or nested runtime trees such as deployment/deer-flow by separating upstream code, local deployment config, generated artifacts, ignored secrets, and project-specific customizations.
---

# Vendored Runtime Maintainer

Use this when inspecting or changing `deployment/deer-flow/`, nested runtime code, or upstream-derived deployment trees.

## Read First

- `AGENTS.md`
- Root `README.md`
- `docs/ops/deerflow-assessment-2026-04-26.md`
- `deployment/deer-flow/README.md`
- Relevant nested `AGENTS.md`, `CLAUDE.md`, or project docs inside the vendored tree
- `agent-skills/git-worktree-guard/SKILL.md`

## Rules

- Identify whether a file is upstream code, local deployment config, generated artifact, or project-specific customization.
- Preserve ignored live configs and secrets.
- Be careful with nested git repositories or copied upstream histories.
- Prefer documenting local overrides under root `docs/ops/`.
- Do not add model-, IDE-, or vendor-specific root rules unless the user asks.
- Avoid broad upstream refactors when the task is local deployment stabilization.

## Workflow

1. Inspect root git status and, if relevant, nested git status.
2. Determine ownership of the target files.
3. For local config issues, prefer ignored config or documented templates.
4. For upstream code changes, keep patches narrow and record why the local fork needs them.
5. For generated/demo artifacts, avoid editing unless directly requested.
6. Summarize whether the change should be upstreamed, kept local, or documented as an ops assumption.

## Output & Approval Gates

- Present a summary of the root cause and the proposed narrow patch.
- Wait for user approval before making invasive upstream edits.
