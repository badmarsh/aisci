---
name: smoke-test
description: Run smoke tests for the AiSci stack (Dashboard + Ignition Engine). Checks that http://localhost:5173 and http://localhost:8001 are reachable and that the Onyx container set is healthy.
---

# Smoke Test

## Read First
- `AGENTS.md`
- `docs/ops/CURRENT_STATUS.md`

## Workflow

1. Run `scripts/check_docker.sh` — verify Docker environment
2. Run `scripts/health_check.sh` — verify ports 5173 and 8001
3. Run `scripts/frontend_check.sh` — verify Dashboard landing page returns 200
