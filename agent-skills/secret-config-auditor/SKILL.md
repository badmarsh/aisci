---
name: secret-config-auditor
description: Review repository config, deployment files, docs, and runtime assumptions for committed secrets, unsafe env handling, Docker socket exposure, local auth mounts, permissive network exposure, and MCP credential leaks.
---

# Secret Config Auditor

Use this for security-sensitive config review.

## Safety Rules

- Do not print secret values.
- Redact keys, tokens, cookies, passwords, and admin credentials in all output.
- Do not rotate, delete, or rewrite credentials without explicit user approval.
- Do not inspect private ignored files unless the user asks and the task requires it.

## Check Areas

- Tracked config files with API keys or tokens.
- `.env` templates that encourage unsafe defaults.
- Docker socket mounts.
- Local CLI auth directory mounts.
- MCP config APIs that expose resolved secret values.
- Services bound beyond localhost.
- Permissive CORS or unauthenticated admin endpoints.
- Docs that include copied shell output with credentials or cookies.

## Workflow

1. Inspect tracked files only by default.
2. Use pattern searches for secret-like keys, but report only file and variable names, not values.
3. Classify each issue by impact and likely exposure.
4. Recommend remediation: env vars, gitignore, key rotation, history cleanup, binding restrictions, auth/redaction.
5. Ask before changing configs or writing sensitive operational notes.

## Output

List findings with redacted evidence, risk, and exact next action. Offer targeted persistence into `docs/ops/platform-backlog.md` or a relevant existing ops note.
