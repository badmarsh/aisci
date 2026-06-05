# Onyx Deployment Analysis
**Date:** 2026-05-30  
**Location:** `/home/ubuntu/aisci/deployment/onyx`

## Executive Summary

The Onyx deployment is **operational but experiencing critical embedding service failures** that prevent search functionality from working. All 18 services are running, but the inference model server has a configuration error causing 500 errors on embedding requests.

---

## Service Status Overview

### ✅ Running Services (18/18)
All services are up and running:

| Service | Status | Uptime | Notes |
|---------|--------|--------|-------|
| onyx-api | Running | 34 min | Experiencing embedding errors |
| onyx-auth-proxy | Running | 2 hours | Healthy |
| onyx-background | Running | 2 hours | Celery workers active |
| onyx-code-interpreter | Running | 2 hours | Healthy |
| onyx-db | Running | 34 min | PostgreSQL 15.2 |
| onyx-image-bridge | Running | 34 min | Port 8090 |
| onyx-indexing | Running | 2 hours | Healthy |
| onyx-inference | Running | 34 min | **CRITICAL ERROR** |
| onyx-litellm | Running | 34 min | 10 models configured |
| onyx-mcp-proxy | Running | 41 min | Nginx proxy healthy |
| onyx-mcp-server | Running | 2 hours | SSE server on port 3001 |
| onyx-minio | Running | 34 min | S3-compatible storage |
| onyx-nginx | Running | 34 min | Main web proxy |
| onyx-ollama | Running | 30 min | RTX 3090 GPU detected |
| onyx-opensearch | Running | 34 min | Cluster YELLOW status |
| onyx-redis | Running | 34 min | Healthy |
| onyx-unstructured | Running | 2 hours | Document processing |
| onyx-web | Running | 2 hours | Frontend server |

---

## 🚨 Critical Issues

### 1. **Inference Model Server - Invalid Model Name Format**

**Severity:** CRITICAL  
**Impact:** Search and embedding functionality completely broken

**Error:**
```
OSError: Repo id must use alphanumeric chars, '-', '_' or '.'. 
The name cannot start or end with '-' or '.' and the maximum length is 96: 
'sentence-transformers/qwen3-embedding:latest'.
```

**Root Cause:**
The inference model server is trying to load `qwen3-embedding:latest` (an Ollama-style model name with `:latest` tag), but the SentenceTransformer library expects a HuggingFace model ID format without Docker-style tags.

**Configuration Mismatch:**
- `.env` specifies: `DOCUMENT_ENCODER_MODEL=alibaba-nlp/gte-qwen2-1.5b-instruct` ✅
- Container environment shows: `DOCUMENT_ENCODER_MODEL=Alibaba-NLP/gte-Qwen2-1.5B-instruct` ✅
- But runtime is attempting to load: `qwen3-embedding:latest` ❌

**Impact on API:**
```
[API:wDjdyfap] Unexpected error running tool internal_search: 
HTTP error occurred - response is None.
```

The API server cannot perform searches because embedding generation fails with 500 errors.

---

### 2. **OpenSearch Cluster Status: YELLOW**

**Severity:** MEDIUM  
**Impact:** No replica shards, potential data loss risk

**Status:**
```
Cluster health status changed from [RED] to [YELLOW]
```

**Indices:**
- `danswer_chunk_nomic_embed` - Active
- `danswer_chunk_qwen3_embedding_latest` - Active
- `top_queries-2026.05.20-84955` - Active

**Issue:** Single-node cluster with no replicas. Data is not redundant.

---

### 3. **Background Worker - Document Indexing Errors**

**Severity:** MEDIUM  
**Impact:** Some documents failing to index properly

**Error:**
```
ChunkCountNotFoundError: Tried to update document 
FILE_CONNECTOR__b55d05ea-5a20-48fe-8fd0-ac050b958e81 
but its chunk count is not known.
```

**Context:** This appears to be a timing issue where documents are being updated before their chunk count is calculated. The error message suggests this is a known state that should resolve automatically.

---

## ⚠️ Warnings & Observations

### 4. **Build Log - Network Connectivity Issues**

**File:** `build_log.txt`  
**Issue:** Docker build failed due to DNS resolution failures

```
WARNING: Retrying after connection broken by 'NewConnectionError'
ERROR: Could not find a version that satisfies the requirement fastapi
```

**Impact:** This was a historical build failure (likely during image-bridge build). The service is currently running from a cached/pre-built image.

---

### 5. **MCP Server Restart**

**Observation:** The MCP server received SIGTERM and restarted during the monitoring period.

```
npm error signal SIGTERM
Onyx MCP SSE Server running on port 3001
```

**Status:** Successfully restarted and operational.

---

## Configuration Analysis

### Environment Configuration

**Key Settings:**
```bash
IMAGE_TAG=v4.0.0-beta.0
ENABLE_CRAFT=true
AUTH_TYPE=basic
FILE_STORE_BACKEND=s3
OPENSEARCH_FOR_ONYX_ENABLED=true
ENABLE_OPENSEARCH_RETRIEVAL_FOR_ONYX=true
```

**Embedding Model:**
```bash
DOCUMENT_ENCODER_MODEL=alibaba-nlp/gte-qwen2-1.5b-instruct
DEFAULT_CROSS_ENCODER_MODEL_NAME=alibaba-nlp/gte-multilingual-reranker-base
EMBEDDING_DIM=1536
NORMALIZE_EMBEDDINGS=True
```

**Performance Tuning:**
```bash
RERANK_COUNT=40
MAX_CHUNKS_FED_TO_CHAT=20
HYBRID_ALPHA=0.3
DOC_TIME_DECAY=0.5
NUM_INDEXING_WORKERS=4
CELERY_WORKER_DOCFETCHING_CONCURRENCY=4
```

### LiteLLM Configuration

**Models Configured (10):**
1. `qwen-max` - Qwen Plus via Dashscope
2. `qwen-omni-flash` - Qwen Omni Turbo
3. `qwen-vl-vision` - Qwen VL Plus
4. `qwen-embedder` - Ollama nomic-embed-text
5. `qwen-reranker` - Dashscope GTE reranker
6. `local-context-model` - Ollama gemma2:9b
7. `local-vision-model` - Ollama qwen2.5vl:3b
8. `nvidia/nvidia-nemotron-nano-9b-v2` - NVIDIA NIM
9. `nvidia/llama-3.1-nemotron-nano-vl-8b-v1` - NVIDIA NIM
10. `meta/llama-3.1-8b-instruct` - NVIDIA NIM

**Routing:** Latency-based routing with 1200s timeout

### GPU Configuration

**Hardware Detected:**
```
NVIDIA GeForce RTX 3090
Compute: 8.6
Total VRAM: 24.0 GiB
Available: 21.5 GiB
```

**Services Using GPU:**
- `onyx-inference` (runtime: nvidia)
- `onyx-indexing` (runtime: nvidia)
- `onyx-ollama` (CUDA enabled)

---

## Celery Background Tasks

**Active Scheduled Tasks (26):**
- `celery-beat-heartbeat` - Health monitoring
- `dispatch-due-scheduled-tasks` - Task scheduler
- `check-for-doc-permissions-sync` - Permission sync
- `check-for-user-file-processing` - File processing
- `check-for-user-file-project-sync` - Project sync
- `check-for-user-file-delete` - File cleanup
- `check-for-connector-deletion` - Connector cleanup
- `check-for-vespa-sync` - Document sync (5 docs synced)
- `check-for-pruning` - Index pruning
- `check-for-indexing` - Document indexing
- `check-for-external-group-sync` - Group sync
- `monitor-celery-queues` - Queue monitoring

**Queue Status (all empty):**
```
celery=1 docfetching=0 docprocessing=0 user_file_processing=0
sync=0 deletion=0 pruning=0 permissions_sync=0
```

**Beat Multiplier:** 8.0 (tasks run every 8 seconds)

---

## Storage & Volumes

**Docker Volumes:**
- `model_cache_huggingface` - HuggingFace model cache
- `inference_model_server_logs` - Inference logs
- `api_server_logs` - API logs
- `craft_venv_volume` - Craft Python venv
- `craft_outputs_volume` - Craft outputs
- `file-system` - Document storage

**Mounted Paths:**
- `/home/ubuntu/aisci` → `/workspace/aisci:ro` (read-only workspace mount)

**Large Directories:**
- `onyx-mcp-server/` - 156 MB
- `chat_output.txt` - 372 KB
- `models.py` - 192 KB

---

## Network Architecture

**Internal Services:**
- API Server: `onyx-api:8080`
- LiteLLM: `onyx-litellm:4001`
- Inference: `onyx-inference:9000`
- Indexing: `onyx-indexing:9000`
- Ollama: `onyx-ollama:11434`
- MCP Server: `onyx-mcp-server:3001`
- Unstructured: `onyx-unstructured:8000`
- Image Bridge: `onyx-image-bridge:8090`

**External Ports:**
- `127.0.0.1:80` - Main web interface
- `127.0.0.1:3000` - Alternative web port
- `127.0.0.1:4001` - LiteLLM API
- `127.0.0.1:8000` - Unstructured API
- `127.0.0.1:8090` - Image bridge
- `127.0.0.1:8095` - MCP proxy

---

## Recommendations

### Immediate Actions Required

1. **Fix Inference Model Configuration** (CRITICAL)
   - Investigate why the inference server is loading `qwen3-embedding:latest` instead of the configured `alibaba-nlp/gte-qwen2-1.5b-instruct`
   - Check for environment variable overrides or runtime model selection logic
   - Restart inference service after fix: `docker compose restart onyx-inference`

2. **Verify Embedding Functionality**
   ```bash
   curl -X POST http://localhost:9000/encoder/bi-encoder-embed \
     -H "Content-Type: application/json" \
     -d '{"texts": ["test query"]}'
   ```

3. **Monitor OpenSearch Health**
   - Consider adding replica configuration if running in production
   - Current YELLOW status is acceptable for development

### Medium-Term Improvements

4. **Document the Model Configuration Flow**
   - Clarify how `DOCUMENT_ENCODER_MODEL` is used vs. runtime model selection
   - Document the relationship between Ollama models and HuggingFace models

5. **Add Health Checks**
   - Implement proper health check endpoints for all services
   - Add dependency health validation before service startup

6. **Logging Improvements**
   - Centralize logs for easier debugging
   - Add structured logging with correlation IDs

### Monitoring Recommendations

7. **Set Up Alerts For:**
   - Inference service 500 errors
   - OpenSearch cluster status changes
   - Celery queue depth > 100
   - GPU memory usage > 90%
   - Document indexing failures

---

## Recent Activity

**Git Status:**
- Current branch: `main`
- Recent commits focus on:
  - Multimodal PDF indexing with Unstructured GPU passthrough
  - RAG evaluation baseline
  - LiteLLM model swaps (qwen-rag-local → qwen2.5vl:7b)
  - Nginx DNS resolver fixes
  - Image editing endpoint additions

**Modified Files (not committed):**
- Multiple configuration files
- Docker compose definitions
- Environment templates
- Helper scripts

---

## Conclusion

The Onyx deployment infrastructure is well-configured with comprehensive service orchestration, but is currently **non-functional for search operations** due to the embedding model configuration error. This is a high-priority issue that blocks core functionality.

The deployment shows good architectural practices:
- ✅ Proper service isolation
- ✅ GPU acceleration configured
- ✅ Multiple LLM providers integrated
- ✅ Background task processing
- ✅ Comprehensive monitoring setup

**Next Step:** Resolve the inference model server configuration to restore search functionality.
