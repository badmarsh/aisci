# Current System Status
**Last Updated:** 2026-07-12
**Maintainer:** Platform Operations

> Snapshot only. Durable open work is tracked in GitHub Issues; system state in `docs/ops/platform-status.md`
> and deployment shape in `docs/ops/deployment-reference.md`.

---

## 🎯 Quick Status

| System | Status | Services | Notes |
|--------|--------|----------|-------|
| **AiSci Dashboard** | ✅ Operational | Frontend (Vite) + Backend (FastAPI) | Re-architected as a project-based research control plane. Accessible via `start_dashboard.sh`. |
| **Onyx** | ✅ Operational | 18/18 running | All fixes applied, embeddings working |

---

## 📊 Dashboard Status (Project Control Plane)

**Core Architecture (July 2026 Refactor):**
- **Project Registry:** Backend and Frontend now use `projectId` for all operations.
- **Robert's Manuscript:** Migrated from global paths to `robert-boson-manuscript` project.
- **Pipeline Abstraction:** Pipelines (Ingest, Fit, LaTeX) are dynamically registered per project.
- **UX Migration:** Multi-project portfolio view implemented at `/`, sidebar and routing are fully `projectId`-aware.
- **Science Workflows:** Science evidence review loop uses `projectId`.

## 📊 Onyx Deployment Status

### Service Health (18/18 Running)

**Core Services:**
- ✅ onyx-api - API server
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

### Embedding Configuration

```yaml
Model: Alibaba-NLP/gte-Qwen2-1.5B-instruct
Dimensions: 1536
Index: danswer_chunk_alibaba_nlp_gte_qwen2_1_5b_instruct
Status: WORKING ✅
```

### LLM Models Status

**✅ Working (Production Ready):**
- `qwen-omni-flash` - Fast chat (2-3s) - **PRIMARY**
- `meta/llama-3.1-8b-instruct` - NVIDIA chat (2-3s)
- `qwen-embedder` - Local embeddings (Ollama)

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

---

## ⚠️ Known Issues

### P0 - Critical
1. **API Key Rotation Required** - Keys exposed in git history (see GitHub Issues)

### P1 - Important
2. **qwen-max Quota Exhausted** - Free tier depleted, using qwen-omni-flash instead
3. **local-context-model Slow** - 24s first load (then 2-3s cached)

### P2 - Minor
1. **OpenSearch YELLOW** - Expected for single-node (3 unassigned replicas)
2. **ChunkCountNotFoundError** - Expected timing issue with auto-retry
3. **HuggingFace Unauthenticated** - Optional HF_TOKEN for faster downloads

---

## 🔄 Recent Changes

### 2026-07-12
- ✅ Dashboard refactored to Project-Based Research Control Plane
- ✅ Replaced global pathing with registered `ProjectSpec` mappings
- ✅ Upgraded Dashboard UX (Portfolio view, sidebars) to handle multiple active projects
- ✅ Extracted pipelines into `pipelines.py`

### 2026-05-30
- ✅ Fixed inference model database configuration
- ✅ Tested all 10 LLM models
- ✅ Analyzed all Docker logs
- ✅ Updated HANDOFF.md with current status
- ✅ Fixed port numbers in deployment-reference.md
- ✅ Created this status document

---

## 🎯 Next Actions

### Immediate (This Session)
1. [ ] Rotate exposed API keys

### Soon (Next Session)
1. [ ] Enable paid tier for qwen-max or remove it from the active route set

### Eventually
1. [ ] Add HF_TOKEN for faster model downloads

---

**Maintained by:** Platform Operations  
**Update Frequency:** After significant changes  
**Last Verified:** 2026-07-12
