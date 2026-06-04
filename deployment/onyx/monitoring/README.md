# Onyx Monitoring Scripts

Lightweight health checks for the Onyx stack. No external dependencies — uses `docker exec` and `curl`.

## Scripts

### `check_health.sh`

Checks five things and exits non-zero if any fail:

| Check | What it does |
|---|---|
| Alembic version | Compares `alembic_version` in Postgres against expected head `ea418a384b9d` |
| Index attempt failures | Counts `status = 'failed'` rows in `index_attempt` for the last 24h |
| Redis queue depth | Reads `celery` list length; warns if >= 100 |
| OpenSearch cluster health | Calls `/_cluster/health`; warns on yellow, fails on red/error |
| LiteLLM liveness | Probes `http://localhost:4001/health/liveliness` |
| MCP liveness | Calls `deployment/helper/check_mcp_liveness.py` for Scite + Consensus; missing/expired tokens warn (not fail), proxy/upstream errors hard-fail |

**Usage:**
```bash
bash deployment/onyx/monitoring/check_health.sh
```

Exit 0 = all green. Exit 1 = one or more failures (details printed inline).

**Run before any reindex or backend image rebuild.** See `docs/ops/deployment-reference.md` for the full pre-reindex checklist.

## Cron example

To run every 6 hours and log output:
```bash
0 */6 * * * cd /home/ubuntu/aisci && bash deployment/onyx/monitoring/check_health.sh >> /tmp/onyx-health.log 2>&1
```

## Nightly RAG regression run

`deployment/helper/run_rag_tests.py` is the canonical Q1–Q5 eval runner against persona id=2. It emits a JSON artifact under `docs/ops/rag-baselines/` so retrieval and generation drift are diffable across reindexes and model-config changes.

Recommended nightly cron — chained after `check_health.sh` so the eval only runs when the stack is green:

```bash
30 3 * * * cd /home/ubuntu/aisci && \
    bash deployment/onyx/monitoring/check_health.sh >> /tmp/onyx-health.log 2>&1 && \
    python3 deployment/helper/run_rag_tests.py --persona-id 2 --label nightly \
        >> /tmp/onyx-rag-nightly.log 2>&1
```

Failure mode notes:

- `with_errors > 0` and the message is `RateLimitError` / `No deployments available` — LiteLLM provider cooldown. The runner records the error verbatim; diff later runs to see whether it persists.
- `with_retrieval = 0` and `with_answer = 0` for all five questions — likely a session-create or auth failure. Inspect the artifact's per-question `error` and `event_kinds` fields. The runner does not fall back to a different persona.
- `with_answer > 0` but `with_retrieval = 0` — model is generating without grounding. Check whether `internal_search` is still attached to the persona.

See `docs/ops/rag-baselines/README.md` for the artifact schema and curation policy.

## Related

- `deployment/helper/onyx_opensearch_cutover.py --json` — OpenSearch parity and embedding correctness gate
- `deployment/helper/litellm_quota_check.py` — LiteLLM route probe
- `Multica Issues` — monitoring backlog item (P2)
