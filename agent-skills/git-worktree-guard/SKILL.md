---
name: git-worktree-guard
description: Use git safely for project context and change hygiene: inspect status and recent history, preserve unrelated changes, avoid destructive commands, stage only relevant files when committing, and summarize diffs accurately.
---

# Git Worktree Guard

Use this at the start of coding, docs, cleanup, review, or implementation work.

## Context From Git

Use git history to understand recent project direction:

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

## Worktree Safety

- Always inspect `git status --short` before edits.
- Assume unrelated dirty files belong to the user or another agent.
- Do not revert, overwrite, or format unrelated changes.
- Never run destructive commands such as `git reset --hard`, `git checkout -- <path>`, or `git clean` unless the user explicitly requests that exact operation.
- Be careful with renamed docs and archives; preserve intent and history.
- Before final summary, inspect `git diff --stat` and relevant `git diff -- <path>` for files you changed.

## Commits

Do not commit unless the user asks.

When committing:

- Stage only files relevant to the requested work.
- Avoid `git add .` unless the user explicitly wants all current changes included.
- Mention unrelated dirty files that were left untouched.
- Use concise commit messages that describe the completed change.

## Reporting

When reporting work:

- List changed files you touched.
- Mention verification performed.
- Mention any important untracked files that should be committed for durability, such as `AGENTS.md` or `agent-skills/`.
