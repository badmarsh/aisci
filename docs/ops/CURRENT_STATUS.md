# Current System Status
**Last Updated:** 2026-05-30  
**Maintainer:** Platform Operations

> Snapshot only. Durable open work is tracked in GitHub Issues; system state in `docs/ops/platform-status.md`
> and deployment shape in `docs/ops/deployment-reference.md`.

---

## 🎯 Quick Status

| System | Status | Services | Notes |
|--------|--------|----------|-------|
| **AiSci Dashboard** | ✅ Operational | Frontend (Vite) + Backend (FastAPI) | Actively developed as part of this repository. Accessible via `start_dashboard.sh`. |
| **Onyx** | ✅ Operational | 18/18 running | All fixes applied, embeddings working |
| **DeerFlow** | ✅ Running | 3/3 edge services running | UI reachable; end-to-end tool execution still needs focused test |

---

## 📊 Onyx Deployment Status

### Service Health (18/18 Running)

**Core Services:**
- ✅ onyx-api - API server (31 min uptime)
- ✅ onyx-web - Web interface (port 80, 3000)
- ✅ onyx-background - Celery workers
- ✅ onyx-inference - Embedding model server
- ✅ onyx-indexing - Document indexing
- ✅ onyx-litellm - LLM routing (port 4001)

**Data Services:**
- ✅ onyx-db - PostgreSQL 15.2
- ✅ onyx-opensearch - Search engine (YELLOW status - expected)
- ✅ onyx-redis - Cache and queues
- ✅ onyx-minio - S3-compatible storage

**AI Services:**
- ✅ onyx-ollama - Local LLM serving (RTX 3090)
- ✅ onyx-unstructured - Document parsing (port 8000)
- ✅ onyx-code-interpreter - Code execution

**Proxy Services:**
- ✅ onyx-nginx - Main web proxy
- ✅ onyx-auth-proxy - Authentication
- ✅ onyx-mcp-proxy - MCP gateway (port 8095)
- ✅ onyx-mcp-server - MCP SSE server
- ✅ onyx-image-bridge - Image processing (port 8090)

### Recent Fixes (2026-05-30)

1. **Science Persona Stack Rebuilt** ✅
   - Problem: Personas had missing/invalid model configs and wrong tool IDs (e.g. Scite mapped to coding agent)
   - Solution: Configured all 4 science personas (`physics-validator`, `evidence-auditor`, `referee-prep`, `arxiv-intake`) with correct model (`qwen-omni-flash`) and correct literature tool mappings (Scite=14, Consensus=13) in `configure_onyx.py`
   - Result: Science persona chat active, verified via successful smoke test
   - Details: `docs/ops/onyx-persona-ids.md`

2. **Polluted Document Purge** ✅
   - Problem: "Robert Corpus" and other doc sets were polluted by local test PDFs (Holocaust denial books, Uncle Fester Meth Guide)
   - Solution: Cleared blocked index attempts, deleted bad FileConnectors, and purged 4,919 chunks from OpenSearch search index
   - Result: Core search indexes completely clean, verified index parity

3. **Robert Corpus Privacy Hardened** ✅
   - Problem: unpublished manuscript data "Robert Corpus" (DS id=2) was public (`is_public=True`)
   - Solution: Patched doc set in DB and updated configuration scripts to ensure `is_public=False` (Private)
   - Result: Research data secured, fully closed from public access

4. **Embedding Model Configuration** ✅
   - Problem: Database had `qwen3-embedding:latest` causing 500 errors
   - Solution: Updated to `Alibaba-NLP/gte-Qwen2-1.5B-instruct`
   - Result: Embeddings working at 0.2s per query
   - Details: `deployment/onyx/FIXES_APPLIED.md`

5. **LLM Model Testing** ✅
   - Tested: 10 models configured in LiteLLM
   - Working: 3 models (qwen-omni-flash, llama-3.1-8b, qwen-embedder)
   - Issues: qwen-max quota exhausted, local-context-model slow first load
   - Details: `deployment/onyx/LLM_TEST_REPORT.md`

6. **Docker Logs Analysis** ✅
   - Analyzed: All 18 services
   - Found: 0 critical issues, 5 non-blocking warnings
   - Result: All errors historical or expected behavior
   - Details: `deployment/onyx/DOCKER_LOGS_ANALYSIS.md`

### Embedding Configuration

```yaml
Model: Alibaba-NLP/gte-Qwen2-1.5B-instruct
Dimensions: 1536
Index: danswer_chunk_alibaba_nlp_gte_qwen2_1_5b_instruct
Status: WORKING ✅
Performance: 0.2s per query (warm), 27s initial load
```

### LLM Models Status

**✅ Working (Production Ready):**
- `qwen-omni-flash` - Fast chat (2-3s) - **PRIMARY**
- `meta/llama-3.1-8b-instruct` - NVIDIA chat (2-3s)
- `qwen-embedder` - Local embeddings (Ollama)

**❌ Issues:**
- `qwen-max` - Quota exhausted (free tier depleted)
- `local-context-model` - Works but 24s first load
- `nvidia/nemotron-nano-9b-v2` - Returns reasoning format

**⏭️ Skipped (Need Special Input):**
- Vision models (need images)
- Reranker (needs document pairs)

### Performance Metrics

```
GPU: RTX 3090 (21.5GB available / 24GB total)
Embedding: 0.2s per query (warm)
Chat: 2-3s per request (fast models)
Background queues: All empty (no backlog)
OpenSearch: 9 active shards, 1,988 documents
```

---

## 🦌 DeerFlow Deployment Status

### Service Health (RUNNING)

```bash
Status: ✅ RUNNING
Verified: 2026-05-30
Host URL: http://localhost:2026
Services: deer-flow-nginx, deer-flow-gateway, deer-flow-frontend
Network: deer-flow-gateway joins both deer-flow-dev_deer-flow-dev and onyx_default
```

### Known Issues (from HANDOFF.md 2026-05-20)

1. **Model Configuration** - Was using gemini-2.5-flash
2. **MCP Transport** - Scite/Consensus HTTP transport issues
3. **Sandbox Mounting** - Fixed per handoff
4. **File Permissions** - Fixed per handoff

### Action Required

- [ ] Test authenticated DeerFlow UI/API workflow execution
- [ ] Test DeerFlow-Onyx MCP/tool integration from the DeerFlow client
- [ ] Keep Scite/Consensus OAuth tokens out of docs and logs

---

## 🔗 Port Mappings (Canonical)

### Onyx Services
```
Web Interface:    http://localhost:80 (also :3000)
LiteLLM API:      http://localhost:4001
MCP Proxy:        http://localhost:8095
Unstructured:     http://localhost:8000
Image Bridge:     http://localhost:8090
Ollama:           http://localhost:11434
```

### DeerFlow Services
```
Web Interface:    http://localhost:2026
API:              http://localhost:2026/api
```

### AiSci Dashboard Services
```
Web Interface:    http://localhost:5173
Backend API:      http://localhost:8001
```

**Note:** All ports bound to `127.0.0.1` for security (not `0.0.0.0`)

---

## 📚 Documentation Index

### Current Status & Fixes
- **This file:** `docs/ops/CURRENT_STATUS.md`
- **Drift analysis:** `docs/ops/DRIFT_ANALYSIS.md`
- **Complete fixes:** `deployment/onyx/COMPLETE_SUMMARY.md`
- **Fixes applied:** `deployment/onyx/FIXES_APPLIED.md`

### Detailed Reports
- **LLM testing:** `deployment/onyx/LLM_TEST_REPORT.md`
- **Docker logs:** `deployment/onyx/DOCKER_LOGS_ANALYSIS.md`
- **Deployment analysis:** `deployment/onyx/DEPLOYMENT_ANALYSIS.md`

### Operational Docs
- **Platform status:** `docs/ops/platform-status.md`
- **Deployment reference:** `docs/ops/deployment-reference.md`
- **Action plan:** `ACTION_PLAN.md`

### Handoffs
- **Current handoff:** `HANDOFF.md` (updated 2026-05-30)
- **DeerFlow audit:** `HANDOFF.md` (original 2026-05-20)

---

## ⚠️ Known Issues

### P0 - Critical
1. **API Key Rotation Required** - Keys exposed in git history (see GitHub Issues)

### P1 - Important
1. **DeerFlow MCP/tool execution not yet re-tested end to end** - Runtime is up, but authenticated tool execution still needs a focused check
2. **qwen-max Quota Exhausted** - Free tier depleted, using qwen-omni-flash instead
3. **local-context-model Slow** - 24s first load (then 2-3s cached)

### P2 - Minor
1. **OpenSearch YELLOW** - Expected for single-node (3 unassigned replicas)
2. **ChunkCountNotFoundError** - Expected timing issue with auto-retry
3. **HuggingFace Unauthenticated** - Optional HF_TOKEN for faster downloads

---

## 🔄 Recent Changes

### 2026-05-30
- ✅ Fixed inference model database configuration
- ✅ Tested all 10 LLM models
- ✅ Analyzed all Docker logs
- ✅ Updated HANDOFF.md with current status
- ✅ Fixed port numbers in deployment-reference.md
- ✅ Created this status document

### 2026-05-20
- ✅ Onyx v4 beta transition completed
- ✅ DeerFlow audit completed (see HANDOFF.md)
- ⚠️ DeerFlow issues identified

---

## 🎯 Next Actions

### Immediate (This Session)
1. [ ] Test DeerFlow-Onyx MCP/tool integration from an authenticated DeerFlow session
2. [ ] Rotate exposed API keys

### Soon (Next Session)
1. [ ] Add a short authenticated DeerFlow smoke-test command or checklist
2. [ ] Enable paid tier for qwen-max or remove it from the active route set

### Eventually
1. [ ] Add HF_TOKEN for faster model downloads
2. [ ] Document DeerFlow startup procedure in the existing deployment reference

---

**Maintained by:** Platform Operations  
**Update Frequency:** After significant changes  
**Last Verified:** 2026-05-30 04:57 UTC
