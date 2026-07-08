# Deployment

This folder contains the Docker Compose stacks, configuration templates, and helper scripts for the local AI infrastructure.

## Stack Overview
- `onyx/` - The curated evidence and retrieval (RAG) layer. See `docs/ops/critical-components.md` for current integration status.
- `deer-flow/` - The orchestration and execution layer for the physics workflow agents.
- `helper/` - Temporary operational scripts and migration helpers.

## Rules
- Do NOT commit live secrets (`.env` files) or model cache binaries to git.
- Keep platform implementation details and ops logs out of the `research/robert/` science files.
- Track deployment blockers and tasks in Multica Issues (`multica issue list`).
- Document deployment decisions in `docs/decisions/`.