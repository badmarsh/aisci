# Historical Onyx RAG Evaluation Results

> Historical record only — not active operational guidance.

> **Historical integration record.** No Onyx RAG deployment exists in the
> current checkout; these results are retained for past-context traceability.

Running log of RAG evaluation runs against the canonical question set in
`rag-evaluation-set.md`. Each entry records the date, persona under test, the
configuration snapshot, and the observed pass/fail outcome per question.

Append new runs to the top of the **Run History** table. Do not edit prior
rows — record corrections as a new run with a `notes` reference to the
prior row.

## Configuration Snapshot (as of 2026-06-02)

Sourced from `docs/ops/onyx-configure.md` and `docs/ops/onyx-persona-ids.md`.
Re-derive on every run; if these change without a re-run, this snapshot is stale.

| Field | Value |
|---|---|
| Embedding model | `Alibaba-NLP/gte-Qwen2-1.5B-instruct` (1536-dim) |
| Search settings id | 10 |
| Contextual RAG LLM | `qwen-cloud-fast` (LiteLLM) |
| OpenSearch retrieval | `ENABLE_OPENSEARCH_RETRIEVAL_FOR_ONYX=true` |
| Vision model | `qwen2.5vl:7b` via LiteLLM (set in Admin UI) |
| Active personas under test | physics-validator (id=2) |
| Doc sets in scope | Robert Corpus (id=2) |
| Eval runner | `deployment/helper/run_rag_tests.py --persona-id 2` |

## Active Personas (from `onyx-persona-ids.md`)

- **physics-validator** (id=2) — primary persona under RAG evaluation, Robert Corpus.
- **arxiv-intake** (id=3) — arXiv Auto — Quarantine; no eval questions assigned.
- **evidence-auditor** (id=5) — Robert Corpus; rebuild rows pending live confirm.
- **referee-prep** (id=6) — Robert Corpus; rebuild rows pending live confirm.

Only `physics-validator` is exercised by the current Q1–Q5 set. Add per-persona
sections below when eval questions are added for the other three.

---

## Run History

### Run 2026-06-02 — BLOCKED at infrastructure layer

- **Persona**: physics-validator (id=2)
- **Runner**: not executed
- **Result**: ❌ infra-blocked — `run_rag_tests.py` was not invoked because
  `onyx-api-server` is in a Postgres-auth crashloop.

**Evidence**

```
$ docker ps --format '{{.Names}} {{.Status}}' | grep onyx-api-server
onyx-api-server   Restarting (1) 38 seconds ago

$ curl -fsS http://localhost:3000/api/health
curl: (22) The requested URL returned error: 502

$ docker logs onyx-api-server --tail … | tail
asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "postgres"
```

`POSTGRES_HOST=onyx-db` is set on `onyx-api-server`. The container's
`POSTGRES_PASSWORD` does not match what `onyx-db` accepts for the `postgres`
role. `onyx-db` itself is `Up 8 hours` — Onyx app config drift is the most
likely cause, not the database.

**What this means for today's eval**

- No Q1–Q5 retrieval was exercised, so no new pass/fail rows can be appended.
- The baseline pre-rebuild `rag-evaluation-set.md` "Run 2026-05-30 (Attempt 2 — pending)"
  entry remains pending; this run does not advance it.
- No tuning is justified by this run. Embeddings, rerank counts, hybrid
  weights, contextual-RAG settings, parser, and doc sets remain untouched
  per `onyx-rag-eval-manager` rules.

**Suggested next steps (outside this run's scope)**

1. Reconcile `POSTGRES_PASSWORD` between `deployment/onyx/.env` (and
   `.env.local`) and the actual `onyx-db` role secret; restart
   `onyx-api-server` until `/api/health` returns 200.
2. Re-run `python3 deployment/helper/run_rag_tests.py --persona-id 2 \
   --output-dir docs/ops/rag-baselines/`.
3. Append the resulting Q1–Q5 table here and reconcile against the entries
   in `rag-evaluation-set.md`.

---

## Result-Table Template

When the next run executes, append a block like this (newest on top):

```
### Run YYYY-MM-DD — persona-id=<N>

| Q  | Result | Top doc (semantic_identifier) | Score | Notes |
|----|--------|-------------------------------|-------|-------|
| Q1 |        |                               |       |       |
| Q2 |        |                               |       |       |
| Q3 |        |                               |       |       |
| Q4 |        |                               |       |       |
| Q5 |        |                               |       |       |

Baseline artifact: docs/ops/rag-baselines/<filename>.json
Config delta vs. prior run: <none | list>
```

Q3 and Q5 are expected `STRUCTURAL GAP` until a `docs/ops/` connector is
indexed — they are not retrieval failures and should not trigger tuning.
