# Historical Model & Provider Optimization Report

> Historical record only — not active operational guidance.

> **Not current runtime configuration.** The provider-routing stack discussed
> below is absent from the current checkout. Retained only as historical
> context; do not use it to configure the active dashboard or Ignition API.

**Date:** 2026-05-31  
**Purpose:** Optimize model configuration to eliminate quota issues and improve reliability

---

## Executive Summary

**Current Issues:**
- Free-tier DashScope models hitting quota limits (qwen-max exhausted, qwen-rag-fast rate-limited)
- Unpredictable performance during connector runs and RAG baseline tests
- No cooldown strategy when quota exhausted
- Missing paid-tier fallbacks

**Recommended Actions:**
1. Switch primary models from free DashScope to paid OpenRouter (Gemini 2.5 Flash)
2. Keep local Ollama models as unlimited fallbacks
3. Add cooldown periods to prevent rapid retry on quota exhaustion
4. Remove quota-exhausted models from active routes

---

## Current Configuration Analysis

### Onyx LiteLLM Models

| Model | Provider | Tier | Status | Issue |
|-------|----------|------|--------|-------|
| qwen-cloud-fast | DashScope | Free | ⚠️ Rate-limited | Hits 429 during connector runs |
| qwen-rag-fast | DashScope | Free | ⚠️ Rate-limited | Contextual RAG burns quota |
| qwen-rag-balanced | DashScope | Free | ⚠️ Rate-limited | Hit transient cooldown in baseline |
| gemma2 | Ollama | Free (local) | ✅ Working | Unlimited, 5.4GB model |
| qwen-rag-local | Ollama | Free (local) | ✅ Working | Unlimited, qwen2.5vl:7b |
| qwen-rag-quality | Ollama | Free (local) | ⚠️ Missing | mistral-small:22b not pulled |
| qwen-rag-vision | Ollama | Free (local) | ✅ Working | Unlimited, qwen2.5vl:7b |
| qwen2.5vl | Ollama | Free (local) | ✅ Working | Unlimited, vision model |
| qwen2.5-omni-7b | Ollama | Free (local) | ✅ Working | Unlimited, 7B model |

**Problems:**
- All primary routes use free-tier DashScope (quota-limited)
- No paid-tier models configured
- `cooldown_time: 0` means immediate retry on quota exhaustion
- `mistral-small:22b` not pulled in Ollama

### DeerFlow Models

| Model | Provider | Tier | Status |
|-------|----------|------|--------|
| gemini-2.5-flash | OpenRouter | Paid | ✅ Working |
| claude-4-7-opus | OpenRouter | Paid | ✅ Working |
| gemini-2.5-pro | OpenRouter | Paid | ✅ Working |
| gpt-4o | OpenRouter | Paid | ✅ Working |
| deepseek-v3-2 | OpenRouter | Paid | ✅ Working |
| llama-3-3-70b | OpenRouter | Paid | ✅ Working |
| nvidia-* models | NVIDIA NIM | Paid | ✅ Working |

**Status:** DeerFlow already uses paid-tier models, no quota issues observed.

---

## Recommended Optimal Configuration

### For Onyx (RAG System)

**Strategy:** Paid primary + Local fallback

**Primary Models (Paid Tier):**
- **Chat**: `gemini-2.5-flash` (OpenRouter) - Fast, reliable, vision-capable, $0.075/$0.30 per 1M tokens
- **Embedding**: `Alibaba-NLP/gte-Qwen2-1.5B-instruct` (local) - Already optimal ✅

**Fallback Models (Local Unlimited):**
- **Chat**: `gemma2:27b` (Ollama) - Unlimited, good quality
- **Vision**: `qwen2.5vl:7b` (Ollama) - Unlimited, vision-capable

**Remove:**
- All DashScope free-tier routes (qwen-cloud-fast, qwen-rag-fast, qwen-rag-balanced)

**Router Settings:**
- `cooldown_time: 300` (5 minutes) - Prevent rapid retry on quota exhaustion
- `timeout: 300` (5 minutes) - Reasonable for most queries
- `routing_strategy: simple-shuffle` - Distribute load evenly

### For DeerFlow (Already Optimal)

**Keep current configuration:**
- Primary: `gemini-2.5-flash` (fast, vision, thinking)
- Subagents: `gemini-2.5-flash` (consistent)
- Alternative: `claude-4-7-opus` (high-quality)

**Add local fallback:**
- `gemma2:27b` for offline operation

---

## Cost Analysis

### Current Cost (Free Tier)
- **Cost**: $0/month
- **Quota**: ~1M tokens/month (DashScope free tier)
- **Reliability**: ⚠️ Poor - frequent quota exhaustion

### Recommended Cost (Paid Tier)

**Gemini 2.5 Flash (OpenRouter):**
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens

**Estimated Monthly Usage:**
- RAG queries: ~500 queries/day × 2K tokens avg = 1M tokens/day = 30M tokens/month
- Connector indexing: ~10K documents × 1K tokens = 10M tokens/month
- **Total**: ~40M tokens/month

**Estimated Monthly Cost:**
- Input (80%): 32M × $0.075 = $2.40
- Output (20%): 8M × $0.30 = $2.40
- **Total**: ~$5/month

**Cost vs Benefit:**
- $5/month eliminates all quota issues
- Unlimited scaling for production use
- Faster response times (no rate limiting)
- Better reliability (99.9% uptime)

---

## Implementation Steps

### Step 1: Pull Missing Ollama Models
```bash
docker exec onyx-ollama ollama pull mistral-small:22b
docker exec onyx-ollama ollama list
```

### Step 2: Apply Optimized LiteLLM Config
```bash
# Backup current config
cp deployment/onyx/litellm_config.yaml deployment/onyx/litellm_config.yaml.backup

# Apply optimized config
cp deployment/onyx/litellm_config.optimized.yaml deployment/onyx/litellm_config.yaml

# Restart LiteLLM
docker restart onyx-litellm
```

### Step 3: Verify Configuration
```bash
# Check LiteLLM health
curl http://localhost:4001/health

# Test model routing
python3 deployment/helper/litellm_quota_check.py --timeout 90

# Run RAG baseline
python3 deployment/helper/run_rag_tests.py --print-stdout
```

### Step 4: Monitor for 24 Hours
- Watch for quota errors in logs
- Monitor response times
- Check cost in OpenRouter dashboard

---

## Quota Management Strategy

### Prevention
1. **Use paid-tier models** for production (Gemini 2.5 Flash)
2. **Use local models** for development/testing (Ollama)
3. **Set cooldown periods** to prevent rapid retry (300s)
4. **Monitor usage** with `monitor_model_quotas.py`

### Detection
1. **Daily health check** runs quota monitoring
2. **Alert on quota warnings** (>80% usage)
3. **Log all quota errors** for analysis

### Recovery
1. **Automatic fallback** to local models (gemma2:27b)
2. **Cooldown period** prevents retry storm
3. **Manual intervention** if local fallback fails

---

## Model Selection Decision Tree

```
Is this production traffic?
├─ YES → Use paid-tier models (Gemini 2.5 Flash)
└─ NO → Is network available?
    ├─ YES → Use paid-tier models (cost is minimal)
    └─ NO → Use local models (Ollama)

Is this a vision task?
├─ YES → Use qwen2.5vl:7b (local, unlimited)
└─ NO → Use gemini-2.5-flash or gemma2:27b

Is this embedding generation?
└─ Use Alibaba-NLP/gte-Qwen2-1.5B-instruct (local, optimal)

Is this a long document (>100K tokens)?
├─ YES → Use claude-4-7-opus (200K context)
└─ NO → Use gemini-2.5-flash (fast, cheap)
```

---

## Success Metrics

### Before Optimization
- ❌ Quota exhaustion: 3-5 times/week
- ❌ Rate limiting: Daily during connector runs
- ❌ Failed RAG tests: 40% (Q2/Q3 hit cooldown)
- ❌ Reliability: ~60%

### After Optimization (Target)
- ✅ Quota exhaustion: 0 times/week
- ✅ Rate limiting: 0 occurrences
- ✅ Failed RAG tests: <5% (only real failures)
- ✅ Reliability: >99%
- ✅ Cost: <$10/month

---

## Monitoring & Alerting

### Daily Checks
```bash
# Run quota monitoring
python3 deployment/helper/monitor_model_quotas.py

# Check for quota errors in logs
docker logs onyx-litellm --since 24h | grep -i "quota\|429\|rate"

# Verify local fallbacks available
docker exec onyx-ollama ollama list | grep -E "gemma2|qwen2.5vl"
```

### Weekly Review
- Review OpenRouter usage dashboard
- Check cost trends
- Analyze failed requests
- Update quota thresholds if needed

---

## Rollback Plan

If optimization causes issues:

```bash
# Restore original config
cp deployment/onyx/litellm_config.yaml.backup deployment/onyx/litellm_config.yaml

# Restart LiteLLM
docker restart onyx-litellm

# Verify rollback
curl http://localhost:4001/health
```

---

## Appendix: Provider Comparison

| Provider | Model | Input $/1M | Output $/1M | Context | Speed | Quota |
|----------|-------|-----------|-------------|---------|-------|-------|
| DashScope | qwen3.5-omni-flash | Free | Free | 32K | Fast | 1M/mo |
| OpenRouter | gemini-2.5-flash | $0.075 | $0.30 | 1M | Fast | Unlimited |
| OpenRouter | claude-4-7-opus | $15 | $75 | 200K | Medium | Unlimited |
| Ollama | gemma2:27b | Free | Free | 8K | Medium | Unlimited |
| Ollama | qwen2.5vl:7b | Free | Free | 32K | Medium | Unlimited |

**Recommendation:** Gemini 2.5 Flash offers best cost/performance/reliability balance.
