---
name: git-worktree-guard
description: Use git safely for project context and change hygiene: inspect status and recent history, preserve unrelated changes, avoid destructive commands, stage only relevant files when committing, and summarize diffs accurately.
---

# Git Worktree Guard

Use this at the start of coding, docs, cleanup, review, or implementation work.

## Read First

Use git history to understand recent project direction before making any changes:

```bash
git status --short
git log --oneline --decorate -n 20
git show --stat --oneline HEAD
```

For focused context, inspect recent changes to relevant files:

```bash
git log --oneline -- path/to/file
git show --stat --oneline <commit>
git show -- path/to/file
```

Use history as context, not as unquestioned truth. Current source-of-truth files in `AGENTS.md` still win.

## Rules

- Always inspect `git status --short` before making edits.
- Assume unrelated dirty files belong to the user or another agent; do not revert, overwrite, or format them.
- Never run destructive commands (`git reset --hard`, `git checkout -- <path>`, `git clean`) unless the user explicitly requests that exact operation.
- Do not commit unless the user asks.
- When committing, stage only files relevant to the requested work; avoid `git add .` unless the user explicitly wants all current changes included.
- Be careful with renamed docs and archives; preserve intent and history.
- Mention unrelated dirty files that were left untouched in every summary.


## Workflow

1. Run `git status --short` and `git log --oneline -n 20` to orient.
2. Inspect specific files relevant to the task with `git log --oneline -- <path>` and `git show -- <path>`.
3. Make the requested changes.
4. Before summarizing, run `git diff --stat` and `git diff -- <changed paths>` to verify what changed.
5. If the user requests a commit: stage only relevant files, draft a concise commit message describing the completed change, and list any unrelated dirty files left untouched.
6. Report changes and any important untracked files that should be committed for durability (e.g., `AGENTS.md`, `agent-skills/`).

## Output & Approval Gates

- List every file you touched with a one-line description of what changed.
- State what verification you performed (diff review, log inspection).
- Flag any important untracked files that should be committed for durability.
- Do not commit, push, or rebase without explicit user instruction per operation.
