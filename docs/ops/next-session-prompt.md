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
- GitHub Issues are now the active work layer; canonical docs stay in repo.
  Start with issues #4 (key rotation), #5 (Onyx docs connector monitoring),
  and #6 (docs/backlog migration).
- Onyx Documentation connector is CC pair 11 / connector 15. Its
  `refresh_freq` was reduced to 86400 seconds on 2026-05-06.
- LiteLLM has RAG routes `qwen-rag-fast`, `qwen-rag-balanced`,
  `qwen-rag-vision`, and local fallback `qwen-rag-local`. Probe with
  `deployment/helper/litellm_quota_check.py --timeout 90`.

Hard constraints:
- Do not restart `onyx-db`.
- Do not print secrets or modify `.env.local` unless explicitly asked.
- Do not change embedding dimensions or switch active search_settings id 10.
- Keep platform details out of science files.
- Preserve unrelated user changes.

Next highest-value work:
1. Rotate provider/tool API keys listed in issue #4 and the 2026-05-06
   secret-history audits, then update only ignored private env/config. Do not
   commit key values.
2. Monitor the next Onyx Documentation connector run from issue #5. Confirm it
   does not retry every 30 minutes, does not hit heartbeat timeout, and does not
   produce repeated DashScope 429s.
3. Start issue #6 by migrating only active open backlog rows to GitHub Issues,
   then shrink `docs/ops/platform-backlog.md` instead of adding new reports.
4. Fix the `onyx-mcp-server` full Jest failures around `send-chat-message`
   nock expectations, then remove the need for `--no-verify` pushes.
5. Rebuild `onyx-python-webdeps:3.11` reproducibly once Docker buildx and PyPI
   DNS are healthy.
6. Verify real DeerFlow MCP tool calls after the `extensions_config.json` route
   update. The gateway was restarted on 2026-05-06 and basic connectivity to
   `onyx-mcp-proxy:80` passed, but an authenticated end-to-end tool call should
   still be exercised.
7. Add monitoring for `onyx-background` errors, Redis queue depth, and Alembic
   version drift.
8. Decide whether OpenSearch retrieval is worth the memory cost or whether a
   measured Vespa-only fallback should reclaim RAM.

Before closing:
- Run `git status -sb`.
- Run `docker compose config --quiet` from `deployment/onyx`.
- Check `curl -fsS http://127.0.0.1:3000/api/health`.
- Report what was changed, what was pushed, and any remaining test gaps.
```
