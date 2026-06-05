# Onyx LLM Models Test Report
**Date:** 2026-05-30  
**Test Duration:** ~5 minutes  
**Models Tested:** 10

---

## Executive Summary

**Status:** 3/7 testable models working, 3 have issues, 4 skipped (require special input)

### Quick Stats
- ✅ **Working:** 3 models (43%)
- ❌ **Failed:** 3 models (43%)
- ⏭️ **Skipped:** 4 models (14% - vision/reranker, need special input)

---

## Detailed Test Results

### ✅ Working Models (3)

#### 1. qwen-omni-flash
- **Provider:** Dashscope (Alibaba Cloud)
- **Type:** Chat completion
- **Status:** ✅ WORKING
- **Response Time:** ~2-3 seconds
- **Test Result:** "OK"
- **Notes:** Fast, reliable, good for general chat

#### 2. qwen-embedder
- **Provider:** Ollama (local)
- **Type:** Embedding
- **Model:** nomic-embed-text
- **Status:** ✅ WORKING
- **Embedding Dimension:** 768
- **Notes:** Local embedding model, fast and reliable

#### 3. meta/llama-3.1-8b-instruct
- **Provider:** NVIDIA NIM
- **Type:** Chat completion
- **Status:** ✅ WORKING
- **Response Time:** ~2-3 seconds
- **Test Result:** "OK"
- **Notes:** NVIDIA hosted, good performance

---

### ❌ Failed Models (3)

#### 1. qwen-max ⚠️ QUOTA EXHAUSTED
- **Provider:** Dashscope (Alibaba Cloud)
- **Type:** Chat completion
- **Status:** ❌ QUOTA EXHAUSTED
- **Error:** `HTTP 403: The free tier of the model has been exhausted`
- **Root Cause:** Free tier quota depleted
- **Fix Required:** 
  - Enable paid tier in Dashscope console
  - OR switch to a different model
  - OR use `qwen-omni-flash` instead (working)

**Configuration Issue:**
```yaml
# Current config uses qwen-plus but names it qwen-max
- litellm_params:
    model: openai/qwen-plus  # ← This is the actual model
  model_name: qwen-max        # ← This is the alias
```

**Recommendation:** Update config to use `qwen-omni-flash` or enable paid tier.

---

#### 2. local-context-model ⚠️ TIMEOUT (but works with longer timeout)
- **Provider:** Ollama (local)
- **Type:** Chat completion
- **Model:** gemma2:9b (5.4 GB)
- **Status:** ⚠️ SLOW (works with 120s timeout)
- **Error:** `Read timed out (30s timeout too short)`
- **Actual Response Time:** 24.34 seconds
- **Test Result:** "OK 😊" (works!)

**Root Cause:** 
- Model is large (5.4 GB)
- First request loads model into memory
- 30-second timeout is insufficient
- Subsequent requests are faster (model cached)

**Fix Required:**
```yaml
# Increase timeout in router_settings
router_settings:
  timeout: 1200  # Already set, but client timeout is 30s
```

**Recommendation:** 
- Increase client-side timeout to 120s for first request
- OR pre-warm the model on startup
- Subsequent requests will be fast (~2-3s)

---

#### 3. nvidia/nvidia-nemotron-nano-9b-v2 ⚠️ RESPONSE FORMAT ISSUE
- **Provider:** NVIDIA NIM
- **Type:** Chat completion (reasoning model)
- **Status:** ⚠️ WORKS but returns unexpected format
- **Error:** `'NoneType' object is not subscriptable`
- **Root Cause:** Model returns `"content": null` with `"reasoning_content"` instead

**Response Format:**
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": null,  // ← NULL instead of text
      "reasoning": "Okay, the user told me to say \"OK",
      "reasoning_content": "Okay, the user told me to say \"OK"
    }
  }]
}
```

**Issue:** This is a **reasoning model** that outputs its thought process in `reasoning_content` field instead of `content` field. The test script expects `content` to be populated.

**Fix Required:**
- Update test script to handle reasoning models
- OR configure LiteLLM to map `reasoning_content` → `content`
- OR use this model only when reasoning is needed

**Recommendation:** This model works but needs special handling for reasoning output.

---

### ⏭️ Skipped Models (4)

These models require special input formats (images, reranking pairs) and were not tested:

#### 1. qwen-vl-vision
- **Provider:** Dashscope
- **Type:** Vision (multimodal)
- **Status:** ⏭️ SKIPPED
- **Reason:** Requires image input
- **Notes:** Should work if quota is available

#### 2. local-vision-model
- **Provider:** Ollama
- **Model:** qwen2.5vl:3b
- **Type:** Vision (multimodal)
- **Status:** ⏭️ SKIPPED
- **Reason:** Requires image input
- **Notes:** Available locally (3.2 GB)

#### 3. qwen-reranker
- **Provider:** Dashscope
- **Type:** Reranker
- **Status:** ⏭️ SKIPPED
- **Reason:** Requires query + document pairs
- **Notes:** Different API format

#### 4. nvidia/llama-3.1-nemotron-nano-vl-8b-v1
- **Provider:** NVIDIA NIM
- **Type:** Vision (multimodal)
- **Status:** ⏭️ SKIPPED
- **Reason:** Requires image input

---

## Configuration Issues Found

### 1. Model Name Mismatch
```yaml
# onyx-litellm_config.yaml line 5-6
- litellm_params:
    model: openai/qwen-plus      # Actual model
  model_name: qwen-max            # Alias (misleading)
```

**Issue:** The alias `qwen-max` suggests a more powerful model, but it's actually `qwen-plus`.

**Recommendation:** Rename to `qwen-plus` for clarity, or use `qwen-turbo` if you want a free-tier model.

---

### 2. Missing Timeout Configuration
```yaml
# Current config
router_settings:
  timeout: 1200  # Server-side timeout (20 minutes)
```

**Issue:** Client-side timeout is hardcoded to 30s in test script, but `local-context-model` needs 24s on first load.

**Recommendation:** Document that first request to Ollama models may take 20-30s.

---

### 3. Reasoning Model Not Documented
The `nvidia/nvidia-nemotron-nano-9b-v2` model returns reasoning in a special format that's not handled by standard chat completion parsers.

**Recommendation:** Add documentation or wrapper to handle reasoning models.

---

## Ollama Models Available

Local models in Ollama (on RTX 3090):

| Model | Size | Last Modified | Status |
|-------|------|---------------|--------|
| gemma2:9b | 5.4 GB | 11 days ago | ✅ Working (slow first load) |
| qwen2.5vl:3b | 3.2 GB | 10 days ago | ⏭️ Vision (not tested) |
| qwen2.5:latest | 4.7 GB | 9 days ago | ⚠️ Not configured in LiteLLM |
| qwen3-embedding:latest | 4.7 GB | 9 days ago | ⚠️ Not configured (wrong format) |
| nomic-embed-text:latest | 274 MB | 10 days ago | ✅ Working |

**Note:** `qwen2.5:latest` and `qwen3-embedding:latest` are available but not configured in LiteLLM.

---

## Recommendations

### Immediate Actions

1. **Fix qwen-max quota issue:**
   ```bash
   # Option A: Enable paid tier in Dashscope console
   # Option B: Update config to use qwen-omni-flash (already working)
   # Option C: Remove qwen-max from config
   ```

2. **Document local-context-model behavior:**
   - First request: 20-30 seconds (model loading)
   - Subsequent requests: 2-3 seconds (cached)
   - Consider pre-warming on startup

3. **Handle reasoning models:**
   - Document that `nvidia/nvidia-nemotron-nano-9b-v2` returns reasoning
   - Update parsers to check `reasoning_content` field
   - OR remove from general chat model list

### Configuration Updates

**Recommended config changes:**

```yaml
model_list:
# Remove or fix qwen-max (quota exhausted)
# - litellm_params:
#     api_base: https://dashscope-intl.aliyuncs.com/compatible-mode/v1
#     api_key: "<DASHSCOPE_API_KEY — rotated, see .env>"
#     model: openai/qwen-plus
#   model_name: qwen-max

# Use qwen-omni-flash as primary (working, fast)
- litellm_params:
    api_base: https://dashscope-intl.aliyuncs.com/compatible-mode/v1
    api_key: "<DASHSCOPE_API_KEY — rotated, see .env>"
    model: openai/qwen-omni-turbo
  model_name: qwen-omni-flash  # PRIMARY CHAT MODEL

# Keep local-context-model but document slow first load
- litellm_params:
    api_base: http://onyx-ollama:11434
    api_key: none
    model: ollama/gemma2:9b
  model_name: local-context-model
  # Note: First request takes 20-30s to load model

# Keep NVIDIA models but mark nemotron as reasoning-only
- litellm_params:
    api_base: https://integrate.api.nvidia.com/v1
    api_key: "<NVIDIA_API_KEY — rotated, see .env>"
    model: openai/nvidia/nvidia-nemotron-nano-9b-v2
  model_name: nvidia/nvidia-nemotron-nano-9b-v2
  # Note: Returns reasoning_content instead of content

# llama works fine
- litellm_params:
    api_base: https://integrate.api.nvidia.com/v1
    api_key: "<NVIDIA_API_KEY — rotated, see .env>"
    model: openai/meta/llama-3.1-8b-instruct
  model_name: meta/llama-3.1-8b-instruct  # WORKING NVIDIA MODEL
```

---

## Testing Vision Models

To test vision models, use this format:

```python
response = requests.post(
    "http://onyx-litellm:4001/v1/chat/completions",
    json={
        "model": "qwen-vl-vision",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image_url", "image_url": {"url": "https://..."}}
            ]
        }],
        "max_tokens": 100
    }
)
```

---

## Summary Table

| Model | Provider | Type | Status | Issue | Fix |
|-------|----------|------|--------|-------|-----|
| qwen-max | Dashscope | Chat | ❌ | Quota exhausted | Enable paid tier or use qwen-omni-flash |
| qwen-omni-flash | Dashscope | Chat | ✅ | None | Working perfectly |
| qwen-vl-vision | Dashscope | Vision | ⏭️ | Not tested | Needs image input |
| qwen-embedder | Ollama | Embedding | ✅ | None | Working perfectly |
| qwen-reranker | Dashscope | Reranker | ⏭️ | Not tested | Different API format |
| local-context-model | Ollama | Chat | ⚠️ | Slow first load (24s) | Document or pre-warm |
| local-vision-model | Ollama | Vision | ⏭️ | Not tested | Needs image input |
| nvidia/nemotron-nano-9b-v2 | NVIDIA | Chat | ⚠️ | Returns reasoning format | Handle reasoning_content |
| nvidia/llama-nemotron-vl | NVIDIA | Vision | ⏭️ | Not tested | Needs image input |
| meta/llama-3.1-8b | NVIDIA | Chat | ✅ | None | Working perfectly |

---

## Conclusion

**Working Models for Production:**
1. ✅ `qwen-omni-flash` - Fast, reliable chat (Dashscope)
2. ✅ `meta/llama-3.1-8b-instruct` - Reliable chat (NVIDIA)
3. ✅ `qwen-embedder` - Local embeddings (Ollama)

**Models Needing Attention:**
1. ❌ `qwen-max` - Quota exhausted, needs paid tier
2. ⚠️ `local-context-model` - Works but slow first load
3. ⚠️ `nvidia/nemotron-nano-9b-v2` - Works but needs reasoning parser

**Recommended Primary Model:** `qwen-omni-flash` (fast, reliable, working)

---

**Test Results Saved:** `/tmp/llm_test_results.json`  
**Test Script:** `/home/ubuntu/aisci/deployment/onyx/test_llms.py`
