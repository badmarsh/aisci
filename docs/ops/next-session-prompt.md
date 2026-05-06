# Next Session Prompt

_Last updated: 2026-05-06_

Use this prompt to continue the AiSci platform repair work in a fresh coding
agent session.

```text
You are continuing the AiSci Onyx/DeerFlow platform repair.
Repo: /home/ubuntu/aisci, GitHub: badmarsh/aisci.

Read first:
- AGENTS.md
- agent-skills/git-worktree-guard/SKILL.md
- agent-skills/aisci-ops-auditor/SKILL.md
- agent-skills/secret-config-auditor/SKILL.md if touching env/config
- docs/ops/platform-backlog.md
- docs/ops/onyx-configure.md
- docs/ops/mcp-endpoints.md
- docs/ops/deployment-reference.md

Current known-good state from 2026-05-06:
- Onyx health endpoint returned 200.
- Redis AOF was verified with `aof_enabled:1`.
- alembic head is `14162713706c`.
- Active embedding is `Alibaba-NLP/gte-Qwen2-1.5B-instruct`, 1536 dims,
  search_settings id 10.
- `deployment/helper/sitecustomize.py` is required for Transformers 5 / Qwen2.
- `deployment/onyx/.env` is tracked and secret-free; `.env.local` is ignored.
- Craft should remain enabled: `ENABLE_CRAFT=true`, `IMAGE_TAG=craft-latest`.
- Onyx MCP host route is `http://127.0.0.1:8095/...`.
- DeerFlow container route is `http://onyx-mcp-proxy:80/...`.
- Onyx MCP submodule URL is `https://github.com/badmarsh/onyx-mcp-server.git`;
  do not point the parent repo at an unreachable local submodule commit.

Hard constraints:
- Do not restart `onyx-db`.
- Do not print secrets or modify `.env.local` unless explicitly asked.
- Do not change embedding dimensions or switch active search_settings id 10.
- Keep platform details out of science files.
- Preserve unrelated user changes.

Next highest-value work:
1. Rotate provider/tool API keys listed in the 2026-05-06 secret-history audit,
   then update only ignored private env/config. Do not commit key values.
2. Fix the `onyx-mcp-server` full Jest failures around `send-chat-message`
   nock expectations, then remove the need for `--no-verify` pushes.
3. Rebuild `onyx-python-webdeps:3.11` reproducibly once Docker buildx and PyPI
   DNS are healthy.
4. Verify real DeerFlow MCP tool calls after the `extensions_config.json` route
   update. The gateway was restarted on 2026-05-06 and basic connectivity to
   `onyx-mcp-proxy:80` passed, but an authenticated end-to-end tool call should
   still be exercised.
5. Add monitoring for `onyx-background` errors, Redis queue depth, and Alembic
   version drift.
6. Decide whether OpenSearch retrieval is worth the memory cost or whether a
   measured Vespa-only fallback should reclaim RAM.

Before closing:
- Run `git status -sb`.
- Run `docker compose config --quiet` from `deployment/onyx`.
- Check `curl -fsS http://127.0.0.1:3000/api/health`.
- Report what was changed, what was pushed, and any remaining test gaps.
```
