# Platform Status

This file tracks concise operational state for Onyx, DeerFlow, Docker, models, and security. Actionable tasks are managed in Multica Issues.

## Security Audit Findings (updated 2026-05-31)

Keys still present in `deployment/onyx/.env` (tracked file). These are dev/personal keys; user confirmed rotation is not required for current tree exposure (Issue #7 closed). Historical exposure in git history is noted for reference.

| Provider | Current Tree Exposure | Historical Exposure (SHAs) | Variable Names | Status |
|---|---|---|---|---|
| Qwen/DashScope | Yes — `.env` line 313 (new key rotated 2026-05-31) | f64e7c9 | DASHSCOPE_API_KEY | Rotated 2026-05-31 |
| NVIDIA | Yes — `.env` line 305 | 888874d, f64e7c9 | NVIDIA_API_KEY | In use — rotation not required |
| Onyx | Yes — `.env` line 355 | f64e7c9, 3e3dd68 | ONYX_API_KEY | In use — rotation not required |
| Gemini | No | 471d897, d49a9a6 | GEMINI_API_KEY | Rotated 2026-05-30 |
| OpenRouter | No | e370048, 6ff9470, b3376af, 9e85623, 888874d, 9828157 | OPENROUTER_API_KEY | Rotated 2026-05-30 |
| Brave | No | f64e7c9, 471d897, d49a9a6, e370048, 6ff9470, 9e85623, 888874d | BRAVE_SEARCH_API_KEY | Rotated 2026-05-30 |
| ElevenLabs | No | 471d897, d49a9a6, e370048, 6ff9470, 9e85623, 888874d | ELEVENLABS_API_KEY | Rotated 2026-05-30 |
| HF | No | 471d897, d49a9a6, e370048, 6ff9470 | HF_TOKEN | Rotated 2026-05-30 |
| MCP Proxy | No | 471d897, d49a9a6, 942da26, 1286998 | MCP_PROXY_AUTH_TOKEN | Rotated 2026-05-30 |

**Note:** `deployment/onyx/.env` is tracked intentionally as a dev-defaults file. Live production keys belong in `.env.local` (gitignored). The `~/.bashrc` `DASHSCOPE_API_KEY` export was updated to the new key on 2026-05-31.

## Onyx RAG Corpus Gaps (updated 2026-05-31)

| Gap Category | Findings | Next Action | Status |
|---|---|---|---|
| Structural Gap | `docs/ops/` and `docs/decisions/` markdown files — Documentation connector (CC pair 6, connector 4) created 2026-05-30, ACTIVE, refresh_freq=86400. | Q5 confirmed retrieving from `ops_onyx-rag-optimization-2026-04-27.md` in baseline run 2026-05-31T01-08-10Z. | Closed — 2026-05-31 |
| Literature Gap | Khuntia (2019) and Rath (2020) PDFs re-uploaded 2026-05-30 via `upload_literature_pdfs.py`; index attempt 42 triggered. | Q1 confirmed retrieving Khuntia/Rath citations in baseline run 2026-05-31T01-08-10Z. | Closed — 2026-05-31 |
| Eval Gap | `run_rag_tests.py` was returning zero hits due to LiteLLM `BadRequestError` (old DashScope key + wrong model names). | Runner refactored 2026-05-31 to emit JSON artifacts under `docs/ops/rag-baselines/`; first usable baseline committed (3/5 with answer + retrieval, Q2/Q3 hit transient `nvidia-balanced` rate-limit). Cron snippet wired in `deployment/onyx/monitoring/README.md`. | Closed — 2026-05-31 |
| Curation Gap | No documented intake/refresh/dedupe path for literature PDFs. | `docs/ops/literature-corpus-policy.md` codifies the canonical add/remove/refresh flow and the dedup rules. | Closed — 2026-05-31 |
| Persona Snapshot | No reproducible export of persona id=2 (and siblings) for stack rebuilds. | `deployment/helper/export_persona_snapshot.py` writes daily snapshots under `deployment/onyx/snapshots/<date>/`; first snapshot landed 2026-05-31. | Closed — 2026-05-31 |
| OAuth Liveness | `check_health.sh` had no Scite/Consensus probe. | `deployment/helper/check_mcp_liveness.py` added; wired into `monitoring/check_health.sh` as a hard-fail-on-proxy-error / soft-warn-on-missing-token check. Tokens themselves still operator-owned. | Closed — 2026-05-31 |
| Extensions Config Drift | Live `deployment/deer-flow/extensions_config.json` had drifted from tracked example (placeholder GitHub token, `$file:/tmp/...` token paths, null placeholders). | `deployment/helper/regenerate_extensions_config_example.py` re-derives the example from the live file with secrets re-abstracted to `$ENV_VAR`. Idempotent (`--check` flag for CI). Example regenerated 2026-05-31. | Closed — 2026-05-31 |

**Targeted Re-indexing Plan for `docs/`:**
1. **Confirm connector:** Verify CC pair 6 covers `docs/ops/` and `docs/decisions/` with `*.md` filter, excludes `docs/archive/`.
2. **Document Set:** Attach CC pair 6 to `AiSci-System-Docs` doc set (meta-knowledge personas only, not physics personas).
3. **Validation:** Run RAG Q3/Q5 and verify exact command/explanation retrieval.


