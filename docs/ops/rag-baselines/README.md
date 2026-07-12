# Historical Onyx RAG Baselines

> **Historical integration record.** Onyx and the RAG infrastructure described below
> are no longer part of the local control-plane deployment.

JSON artifacts produced by `deployment/helper/run_rag_tests.py`. Each artifact captures the full Q1–Q5 evaluation run against a named persona at a point in time, so that retrieval and answer-generation regressions can be diffed across reindexes, model swaps, or LiteLLM config changes.

## Filename convention

```
rag-baseline-<UTC timestamp>-persona-<id>[-<label>].json
```

The label is optional and useful when running before/after a reindex
(`--label pre-reindex` / `--label post-reindex`).

## Schema (per artifact)

| Field | Meaning |
|---|---|
| `schema_version` | Bumped only when the structure changes. |
| `ran_at_utc` | Wall-clock timestamp of the run. |
| `base_url` | Onyx URL the runner hit. |
| `persona_id` | Numeric persona id (typically `2` = `physics-validator`). |
| `label` | Optional run label. |
| `summary` | Quick counts: `total`, `with_answer`, `with_retrieval`, `with_errors`. |
| `results[]` | One record per question (Q1–Q5). |

Per-result fields worth reading on a regression diff:

- `answer_chars`, `answer_preview` — quick eyeball of generation quality.
- `top_documents[]` — retrieved chunks (id, semantic_identifier, score, blurb preview).
- `search_queries[]` — what the persona's search tool actually queried.
- `errors[]` — captured stream errors (e.g. LiteLLM `RateLimitError`, model unavailable).
- `event_kinds` — counts of stream event types; useful when the answer is empty (was retrieval attempted at all? was the LLM the failure?).
- `elapsed_ms` — total wall-clock for the question, including retrieval + generation.

## How to interpret an empty `answer`

If `answer_chars=0` and `errors` contains a `RateLimitError`/`No deployments available`, that's a transient LiteLLM cooldown — re-run after 30–60 s.

If `answer_chars=0` with no error and `event_kinds` only shows `search_tool_*` and `section_end`, the model never started generating — likely a routing or auth issue rather than a corpus issue.

If `answer_chars > 0` but `top_documents=[]`, the persona answered without retrieval — usually means `internal_search` wasn't selected for that question.

## Diffing two baselines

The artifact is plain JSON, so a fast first pass is `jq`:

```bash
jq '.results[] | {id, answer_chars, n_docs: (.top_documents|length), errors: (.errors|length)}' \
  docs/ops/rag-baselines/<old>.json
```

For a full per-question diff:

```bash
diff <(jq '.results[]' old.json) <(jq '.results[]' new.json) | head
```

## How baselines are produced

```bash
python3 deployment/helper/run_rag_tests.py --persona-id 2 --label baseline-YYYY-MM-DD
```

The runner writes here automatically (`--output-dir` defaults to this folder). Cron snippet:

```
# 03:30 local — runs after monitoring/check_health.sh
30 3 * * * cd /home/ubuntu/aisci && \
    bash deployment/onyx/monitoring/check_health.sh >> /tmp/onyx-health.log 2>&1 && \
    python3 deployment/helper/run_rag_tests.py --persona-id 2 --label nightly \
        >> /tmp/onyx-rag-nightly.log 2>&1
```

See `deployment/onyx/monitoring/README.md` for the wrapper conventions.

## Curation policy

- **Keep**: the most recent baseline per persona, plus any baseline labelled with a known operational milestone (`baseline-2026-05-31`, `post-bge-m3-reindex`, `post-litellm-realias`).
- **Drop**: intermediate or rate-limit-transient runs once a clean run lands.
- Don't keep more than ~10 baseline files at a time — the artifacts diff cleanly with `git log --follow` so history is preserved without filesystem clutter.
