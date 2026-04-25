# 🗂️ AiSci Workspace — Consolidated Action Plan

> **Project:** AI-assisted scientific research | CERN HEP physics + RAG + multi-agent workflows
> **Team:** Robert (physicist, CERN) + IT consultant  
> **Last updated:** 2026-04-25 (Phase 2 readiness confirmed ✅)

---

## 🏗️ PHASE 1 — Infrastructure Stabilization *(in progress)*

### 1.1 Git & Version Control ✅
- [x] Initialize git repo in `~/aisci`
- [x] Create private remote `badmarsh/aisci` via `gh`
- [x] Initial commit with all project files
- [x] Push to `origin/main`
- [ ] Add `.gitignore` entries for large model caches, `.env` secrets
- [ ] Set up branch protection on `main` (require PR for changes)

### 1.2 Onyx Deployment *(partially done)*
- [x] `docker-compose.yml` with full stack: Vespa, OpenSearch, Postgres, Redis, LiteLLM, Ollama, Unstructured, Docling, MinIO, MCP proxy, Code-Interpreter
- [x] GPU reservations for inference/indexing model servers (RTX 3090)
- [x] Nginx templates copied to `deployment/data/nginx/` → fixes `run-nginx.sh` missing error
- [x] Nginx container running again ✅
- [x] Docling: fixed port mismatch (5000 → 5001), switched to GPU image `docling-serve:latest`
- [~] Docling container running (unhealthy — CPU image, low priority; old GPU image not available in current WSL session)
- [~] api_server name collision still present (886b1eb8df8f_onyx-api_server-1) — healthy and working, defer clean restart
- [x] `http://localhost:3000` loads Onyx UI ✅
- [x] `http://localhost:4000` LiteLLM proxy healthy ✅
- [x] `http://localhost:8095` MCP proxy running ✅

### 1.3 Deer-Flow v2 Deployment *(running, config management pending)*
- [x] Deer-flow containers running: `deer-flow-nginx`, `deer-flow-gateway`, `deer-flow-frontend`, `deer-flow-langgraph`
- [x] Accessible at port `2026`
- [x] `~/aisci/deployment/deer-flow/` contains reference config and `.env.example`
- [ ] **TODO:** Copy live `~/deer-flow/config.yaml` → `~/aisci/deployment/deer-flow/config.yaml.active` (gitignored)
- [ ] **TODO:** Copy live `~/deer-flow/.env` → `~/aisci/deployment/deer-flow/.env` (gitignored, for reproducibility)
- [ ] **TODO:** Document MCP tools enabled in deer-flow (`extensions_config.json`)
- [ ] **TODO:** Verify deer-flow UI at `http://localhost:2026`

---

## 🔬 PHASE 2 — Onyx "Smartest RAG" Configuration *(highest priority)*

### 2.1 Docling as Primary Document Parser
- [ ] Set `UNSTRUCTURED_API_URL=http://docling:5001` in `.env` (replace unstructured-api for math-heavy PDFs)
- [ ] Test PDF ingestion: upload Robert's boson probability paper via Onyx UI
- [ ] Verify LaTeX equations and tables are parsed correctly by Docling
- [ ] Compare Docling vs Unstructured output quality on physics PDFs

### 2.2 Ollama GPU Models — Embedding, Reranking, Visual RAG
Currently running in `onyx-ollama-1`. Verify these models are pulled:
- [ ] `nomic-embed-text:latest` — local embedding (replaces HuggingFace sentence-transformers)
- [ ] `BAAI/bge-reranker-v2-m3` — cross-encoder reranking (set in env ✅)  
- [ ] `qwen2-vl:latest` → rename: **check if `qwen2.5-vl` is available** — visual RAG for figures/plots
- [ ] `gemma2:27b` or `qwen2.5:32b` — primary chat/reasoning
  ```bash
  docker exec onyx-ollama-1 ollama list
  docker exec onyx-ollama-1 ollama pull nomic-embed-text
  docker exec onyx-ollama-1 ollama pull qwen2.5-vl:7b
  ```

### 2.3 Contextual RAG ✅ CONFIRMED WORKING
- [x] Contextual RAG enabled: `search_settings id=4` has `enable_contextual_rag=t` with `google/gemini-2.5-flash` via OpenRouter
- [x] Embedding model: `nomic-ai/nomic-embed-text-v1` (PRESENT, active)
- [x] Hybrid search: BM25 + dense — `HYBRID_ALPHA=0.3` ✅
- [x] Reranking: `RERANK_COUNT=40` ✅
- [x] OpenSearch index `danswer_chunk_nomic_ai_nomic_embed_text_v1__danswer_alt_index`: **16 docs** (contextual RAG index)
- [x] Index attempts 30–36 all SUCCESS against settings_id=4 — NO hanging on OpenRouter ✅

### 2.4 Visual RAG for Physics Plots
- [ ] Confirm `IMAGE_ANALYSIS_ENABLED=true` + `IMAGE_MODEL_NAME=qwen2-vl:latest` in `.env` ✅
- [ ] Test visual RAG: upload paper PDF → ask about Figure 5 (pT cut sensitivity plot)
- [ ] Configure Onyx to extract and index figure captions separately

### 2.5 "Physics Validation Mode" Persona
- [ ] Re-create persona in Onyx UI (may have been lost in restart)
- [ ] System prompt: zero-hallucination, cite chunks only, flag unverified claims
- [ ] Tools enabled: Consensus MCP, Scite MCP, SymPy agent, Code Interpreter

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
- [ ] Configure deer-flow MCP: add Consensus + Scite + arXiv
- [ ] Create deer-flow "Physics Paper Analysis" workflow template:
  1. Download paper from arXiv
  2. RAG query against Onyx knowledge base
  3. Cross-check citations via Scite
  4. Run SymPy formula verification
  5. Generate referee report

---

## 🧪 PHASE 4 — Robert's Paper Analysis *(the actual science work)*

> **Paper:** "Boson probability function for the moving system" — ATLAS 13 TeV data  
> **Issue:** Robert believes the theory/model is good but there's an issue with the data

### 4.1 Formula Verification (SymPy Agent) — PHASE 1 COMPLETE ✅
- [x] f(p) ~ δ(p²-m²)Θ(p⁰)exp(-βU^μ p_μ) — Lorentz-covariant, correct ✅
- [x] δ-function integration: gives exp(-pT·cosh(η-Y)/T) ✅
- [x] sinh substitution: pz = pT·sinh(η), pT integral = T²/cosh²(η-Y) ✅
- [x] η-cut formula: verified U→0 recovers static Cooper-Frye ✅
- [x] Velocity parameterization: v=U/√(1+U²) always < c, γv=U ✅
- **Script:** `physics/src/boson_paper_analysis.py` (new, Phase 1)
- **Script:** `physics/src/sympy_validation_agent.py` (baseline validator)

### 4.2 Data Issue Investigation — PARTIAL ✅
- [x] High-multiplicity bins (n_sel≥126) identified as anomalous:
  - U₂ = 0.0108 ± **0.8467** — uncertainty >> value → UNCONSTRAINED fit
  - kT₂ = 4.813e+02 ± **1.246e+04** GeV — UNPHYSICAL temperature
  - U₃ = 0.013 ± **1.646** — same pattern
  - Root cause: 3-component fit over-parameterized for available pT range
- [x] U=1 means v=0.707c (not "nearly luminal" but relativistic) — flag as high
- [ ] **TODO:** Confirm exact pT range and data binning from Robert
- [ ] **TODO:** Run automated fitting across all bins with `iminuit`
- [ ] **TODO:** Compare chi-squared values per bin

### 4.3 Automated Fitting Agent
- [ ] Implement full fitting pipeline for all multiplicity bins (21–150)
- [ ] Scan hyperparameter ranges, find global vs local minima
- [ ] Plot U (velocity) vs multiplicity — should increase monotonically (hydrodynamic flow)
- [ ] Plot kT (temperature) vs multiplicity
- [ ] Generate χ²/ndf table — currently missing from paper

### 4.4 Literature Comparison via RAG
- [ ] Ingest key comparison papers into Onyx:
  - Blast-Wave model papers (ALICE measurements)
  - Tsallis statistics papers for pp at 13 TeV
  - `arxiv:2512.07785` — LLM agents for ATLAS Higgs analysis
  - `arxiv:2509.06855` — SciTreeRAG for LHCb
- [ ] Ask RAG: "Does U increase with multiplicity in comparable models?"
- [ ] Ask RAG: "What χ²/ndf are typical in similar thermal fits?"

### 4.5 AI Referee Report
- [ ] Generate structured referee report identifying:
  - Missing uncertainty tables
  - No χ²/ndf reported ← key issue
  - No comparison to Blast-Wave model
  - Anomalous high-multiplicity behavior not explained
  - Missing discussion of collective flow context
- [ ] Generate LaTeX suggestions for equation numbering and cross-references

---

## 🛠️ PHASE 5 — Tooling & Workflow Recommendations

### Skills / Tools to Add
| Tool | Purpose | Where |
|---|---|---|
| `iminuit` Python | Robust HEP-standard fitting | deer-flow sandbox |
| `ROOT` / `uproot` | CERN data format (TTree, histograms) | deer-flow sandbox |
| `SymPy` | Symbolic math verification | already in physics/src |
| `matplotlib` + `scipy` | Plotting and fitting | deer-flow sandbox |
| `INSPIRE-HEP API` | Direct HEP literature search | MCP or deer-flow tool |
| `arXiv API` | Paper retrieval | MCP or deer-flow tool |

### Suggested Workflow for Robert
```
Paper PDF → Onyx (RAG index) → Physics Validation Mode persona
         ↓
   Deer-Flow research agent:
   - Pull related papers (Consensus/Scite/arXiv MCPs)
   - Run SymPy formula checker
   - Run automated fitting (Python sandbox)
   - Compare to literature
         ↓
   Generate: referee report + improved figures + chi-squared table
```

---

## 📋 Immediate Next Steps (Do These Now)

```bash
# 1. Verify Onyx is accessible
curl -s http://localhost:3000 | head -5

# 2. Restart docling with GPU image
docker compose -f ~/aisci/deployment/onyx/docker-compose.yml up -d --force-recreate docling

# 3. Check Ollama models
docker exec onyx-ollama-1 ollama list

# 4. Pull missing embedding model if needed
docker exec onyx-ollama-1 ollama pull nomic-embed-text

# 5. Check deer-flow
curl -s http://localhost:2026 | head -5

# 6. Upload Robert's paper to Onyx
# Go to http://localhost:3000 → Add Connector → File → upload the PDF
```

---

*Consolidated from: `docs/FINAL_SUMMARY.md`, `docs/CRTICAL_COMPONENTS.md`, `docs/PROJECT_RULES.md`, `docs/TROUBLESHOOTING.md`, `docs/FIRST_BRAINSTORMING.md`*
