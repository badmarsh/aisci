# 🗂️ AiSci Workspace — Consolidated Action Plan

> **Project:** AI-assisted scientific research | CERN HEP physics + RAG + multi-agent workflows
> **Team:** Robert (physicist, CERN) + IT consultant  
> **Last updated:** 2026-04-27 (docs consolidated; science task ownership moved to `research/robert/next-actions.md`)

---

## 🏗️ PHASE 1 — Infrastructure Stabilization *(in progress)*

### 1.1 Git & Version Control ✅
- [x] Initialize git repo in `~/aisci`
- [x] Create private remote `badmarsh/aisci` via `gh`
- [x] Initial commit with all project files
- [x] Push to `origin/main`
- [x] Add `.gitignore` entries for large model caches, `.env` secrets, logs, PDFs, and artifacts
- [ ] Set up branch protection on `main` (require PR for changes)

### 1.2 Onyx Deployment *(partially done)*
- [x] `docker-compose.yml` with full stack: Vespa, OpenSearch, Postgres, Redis, LiteLLM, Ollama, Unstructured, Docling, MinIO, MCP proxy, Code-Interpreter
- [x] GPU reservations for inference/indexing model servers (RTX 3090)
- [x] Nginx templates copied to `deployment/data/nginx/` → fixes `run-nginx.sh` missing error
- [x] Nginx container running again ✅
- [x] Docling removed from active production compose; local Unstructured restored as parser
- [x] Local Unstructured healthy at `http://localhost:9560`
- [x] API container name normal again: `onyx-api_server-1`
- [x] Recreate stack from `/home/ubuntu/aisci/deployment/onyx` so Compose labels stop referencing old `/home/ubuntu/onyx_data/...` path
- [x] `http://localhost:3000` loads Onyx UI ✅
- [x] `http://localhost:4000` LiteLLM proxy healthy ✅
- [x] `http://localhost:8095` MCP proxy running ✅

### 1.3 Deer-Flow v2 Deployment *(running, config management pending)*
- [x] Deer-flow containers running: `deer-flow-nginx`, `deer-flow-gateway`, `deer-flow-frontend`, `deer-flow-langgraph`
- [x] Accessible at port `2026`
- [x] `~/aisci/deployment/deer-flow/` contains reference config and `.env.example`
- [x] Live config exists at `~/aisci/deployment/deer-flow/config.yaml` (gitignored by DeerFlow rules)
- [x] Live `.env` exists at `~/aisci/deployment/deer-flow/.env` (gitignored)
- [x] MCP tools documented in `docs/ops/deerflow-assessment-2026-04-26.md`
- [x] DeerFlow gateway verified healthy at `http://localhost:2026`
- [x] Replace generic/legal agents with Robert physics workflow agents
- [x] Add/verify Scite, Consensus, arXiv, and INSPIRE-HEP integrations

---

## 🔬 PHASE 2 — OpenSearch Migration & RAG Optimization *(highest priority)*

### 2.0 OpenSearch Migration (Priority Alpha) 🔴
Vespa is currently answering queries, but the project goal is to move to OpenSearch. The migration is currently stalled with `KeyError: 'document_id'`.
- [ ] **Fix Transformer Bug:** Patch `onyx/background/celery/tasks/opensearch_migration/transformer.py` to handle missing/nested `document_id` in Vespa chunks.
- [ ] **Model Dimension Alignment:** Ensure OpenSearch index is created with 768 dimensions (Nomic-embed) instead of 384 (MiniLM).
- [ ] **Reconcile Chunk Parity:** Identify why OpenSearch has fewer chunks than Vespa for key science docs (e.g., Tsallis datasets).
- [ ] **Enable OpenSearch Retrieval:** Set `enable_opensearch_retrieval=true` in `opensearch_tenant_migration_record` after parity is confirmed.
- [ ] **Decommission Vespa:** Stop `onyx-index-1` after OpenSearch is verified stable.

### 2.1 Parser Baseline
- [x] Keep local Unstructured as the production parser
- [x] Set `UNSTRUCTURED_API_URL=http://unstructured:8000`
- [ ] Test current PDF ingestion path with Robert's boson paper after next clean restart
- [ ] Revisit Docling only as an experimental side parser after validation workflow is stable

### 2.2 Ollama GPU Models — Embedding, Reranking, Visual RAG
Currently running in `onyx-ollama-1`, but no models were found during live diagnosis. Either pull these models or remove the exposed Ollama options from visible model lists:
- [ ] `nomic-embed-text:latest` — local embedding (replaces HuggingFace sentence-transformers)
- [ ] `BAAI/bge-reranker-v2-m3` — cross-encoder reranking (set in env ✅)  
- [ ] `qwen2-vl:latest` → rename: **check if `qwen2.5-vl` is available** — visual RAG for figures/plots
- [ ] `gemma2:27b` or `qwen2.5:32b` — primary chat/reasoning
  ```bash
  docker exec onyx-ollama-1 ollama list
  docker exec onyx-ollama-1 ollama pull nomic-embed-text
  docker exec onyx-ollama-1 ollama pull qwen2.5-vl:7b
  ```

### 2.3 Contextual RAG ✅ CONFIRMED WORKING (2026-04-26 verified)
- [x] Contextual RAG enabled: `search_settings id=4` has `enable_contextual_rag=t` with `google/gemini-2.5-flash` via OpenRouter
- [x] `search_settings id=3` is `PAST` (not active) — no action needed
- [x] Embedding model: `nomic-ai/nomic-embed-text-v1` (PRESENT, active, settings_id=2 primary + id=4 alt)
- [x] Hybrid search: BM25 + dense — `HYBRID_ALPHA=0.3` ✅
- [x] Reranking: `RERANK_COUNT=40` ✅
- [x] OpenSearch main index: **29 docs** (Tsallis=4, boson paper=24, image=1)
- [x] OpenSearch alt index (contextual): **16 docs** (Tsallis=4, boson paper=12)
- [x] Continuous Tsallis index attempts (id=62–76) all SUCCESS against settings_id=4 ✅
- [x] No OpenRouter hanging observed ✅

### 2.4 Visual RAG for Physics Plots
- [ ] Confirm `IMAGE_ANALYSIS_ENABLED=true` + `IMAGE_MODEL_NAME=qwen2-vl:latest` in `.env` ✅
- [ ] Test visual RAG: upload paper PDF → ask about Figure 5 (pT cut sensitivity plot)
- [ ] Configure Onyx to extract and index figure captions separately

### 2.5 "Physics Validation Mode" Persona
- [ ] Make this the real primary Onyx persona
- [ ] Attach Physics document sets: Robert draft, HEP references, validation methods
- [ ] Attach tools: internal search, read file, code interpreter/Python, open URL, Scite, Consensus
- [ ] System prompt: zero-hallucination, cite chunks only, flag unverified claims
- [ ] Keep web search disabled by default for strict validation; enable only for literature scouting

---

## 🔌 PHASE 3 — MCP Research Services Integration

### 3.1 Consensus MCP *(proxy configured at :8095/consensus/)*
- [ ] Add Consensus API key to `nginx_mcp_proxy.conf`
- [ ] Test: search for papers on Bose-Einstein distributions in pp collisions
- [ ] Integrate into deer-flow as a research tool
- [ ] Integrate into Onyx as a connector or tool call

### 3.2 Scite MCP *(proxy configured at :8095/scite/)*
- [ ] Add Scite API key to `nginx_mcp_proxy.conf`
- [ ] Test: validate citations in Robert's paper
- [ ] Use Scite to check if cited papers support or contradict the claims

### 3.3 Additional Relevant MCP Servers to Evaluate
| MCP Server | Use Case | Priority |
|---|---|---|
| `arxiv-mcp` | Search/fetch arXiv papers directly | High |
| `semantic-scholar` | Citation graphs, related work | High |
| `wolfram-alpha` | Symbolic math verification | Medium |
| `inspire-hep` | CERN HEP literature database | High |
| `python-repl` (deer-flow built-in) | Run physics simulations | High |

### 3.4 Deer-Flow Research Workflow
- [x] Configure deer-flow MCP: add Consensus + Scite + arXiv
- [x] Create deer-flow "Physics Paper Analysis" workflow template:
  1. Download paper from arXiv
  2. RAG query against Onyx knowledge base
  3. Cross-check citations via Scite
  4. Run SymPy formula verification
  5. Generate referee report

---

## 🧪 PHASE 4 — Robert's Paper Analysis *(science tracker only)*

> **Paper:** "Boson probability function for the moving system" — ATLAS 13 TeV data  
> **Current science task queue:** `research/robert/next-actions.md`

This section intentionally stays high level. Detailed science claims, gates, plans, and outputs live in:

- `research/robert/evidence-ledger.md` - canonical claim status.
- `research/robert/science-questions.md` - question backlog.
- `research/robert/validation-plan.md` - validation method.
- `research/robert/fit-plan.md` - fitting specification.
- `research/robert/runs/` - dated run artifacts.

### 4.1 Current Science Status
- [x] Phase 1 local sanity checks completed under explicit assumptions.
- [ ] Robert's full pT data table is still blocking automated fitting.
- [ ] Manuscript must clarify full Bose-Einstein versus Boltzmann/Juttner approximation.
- [ ] Fit quality, covariance, correlations, and baseline comparisons are still required before physical conclusions.

---

## 🛠️ PHASE 5 — Tooling References

Keep implementation-specific tooling decisions in `research/robert/fit-plan.md` and platform integration tasks in `docs/ops/platform-backlog.md`. The near-term required tools are `iminuit`, `scipy`, `matplotlib`, and literature search over arXiv/INSPIRE plus citation context checks.

---

## 📋 Current Pointers (Updated 2026-04-27)

### ✅ Recent Checkpoints
- Repo checkpoint commit pushed: `b3376af` (2026-04-28)
- Repo-wide documentation layout started: `docs/ops`, `docs/decisions`, `docs/archive`, `research/robert`
- Contextual RAG verified: settings_id=4, `enable_contextual_rag=t`, no hanging ✅
- File connector (cc_pair=2): boson paper indexed — 24 chunks in main, 12 in contextual alt index ✅
- Onyx UI: both queries return correct results with File sources cited ✅
- `boson_paper_analysis.py`: Phase 1 sanity checks re-run, clean ✅

### 🔴 Next Actions Required
- Science queue: `research/robert/next-actions.md`
- Platform queue: `docs/ops/platform-backlog.md`

```bash
# Check Ollama models status
docker exec onyx-ollama-1 ollama list

# Check deer-flow
curl -s http://localhost:2026 | head -5

# Run Phase 1 analysis
cd ~/aisci/physics && python3 src/boson_paper_analysis.py
```

---

*Consolidated from historical docs now organized under `docs/archive/` and `docs/ops/`.*
