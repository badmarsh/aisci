# Onyx Platform Backlog

_Last updated: 2026-05-06_

Canonical platform backlog: `docs/ops/platform-backlog.md`. This file is the
Onyx-local operator mirror for deployment-specific blockers.

## Blocked / Infrastructure Issues

- [ ] **onyx-mcp-server Docker build** — npm hangs inside Docker build context.
  - Root cause: Docker buildx missing on host; PyPI DNS also unreliable.
  - Current workaround: runtime MCP via Compose `command` wrapper works.
  - Source: parent `.gitmodules` points at
    `https://github.com/badmarsh/onyx-mcp-server.git` so the SSE/token-fallback
    commits are reachable for fresh clones.
  - Fix path: install `docker-buildx-plugin`, fix DNS, then
    `docker compose build onyx-mcp-server` and remove the command override.
  - Dockerfile and source changes are committed and ready.

- [ ] **onyx-python-webdeps:3.11 image reproducibility** — The local image was
  built by committing the running container (`docker commit`) because buildx and
  PyPI DNS were unavailable. On a fresh host this image will be missing.
  - Fix path: `DOCKER_BUILDKIT=0 docker build -t onyx-python-webdeps:3.11 \
    -f deployment/onyx/Dockerfile.python-webdeps deployment/onyx/` once
    network/buildx are available.

## Decisions Needed (Product / Ops)

- [ ] **API key rotation** — Provider API keys were present in tracked files
  before Session 2 cleanup. Rotate: Dashscope/Qwen, OpenRouter, Nvidia NIM,
  and any other keys that appeared in docker-compose.yml or litellm_config.yaml
  history. See commit audit output from Task 0 above for affected SHAs.

- [ ] **OpenSearch resource cost** — Both indexing and retrieval are now enabled.
  OpenSearch uses ~6–8 GB RAM (4 GB JVM heap + OS overhead). If Vespa-only
  retrieval is sufficient, disable opensearch-* containers and reclaim RAM.

- [ ] **LiteLLM image tag** — Currently pinned to an immutable digest of
  `main-latest`. Evaluate migration to a stable release tag (v1.72.x+) before
  next `docker compose pull`.

- [ ] **Ollama image tag** — Currently pinned to digest of `ollama:latest`.
  Pin to explicit version (e.g. `ollama/ollama:0.7.x`) for reproducibility.

- [ ] **LiteLLM model naming convention** — Names evolved organically
  (e.g. `nemotron-4-340b` → nvidia model, `qwen3.5-397b-a17b-or` vs
  `qwen3.5-397b-a17b`). Consider a `<provider>-<model>` prefix scheme
  (`or-`, `ds-`, `nv-`) for clarity in connector logs.

## Monitoring Gaps

- [ ] No log aggregation for onyx-background embedding/indexing errors.
- [ ] No Celery queue depth alerting (Redis llen thresholds).
- [ ] No alert if alembic_version drifts from expected head after upgrade.
