# Model Selection Guide

**Purpose:** Help operators choose the right model for each task to optimize cost, performance, and reliability.

---

## Quick Reference

| Task | Recommended Model | Fallback | Cost |
|------|------------------|----------|------|
| RAG chat queries | `gemini-2.5-flash` | `gemma2:27b` | $0.075-0.30/1M |
| Document indexing | `gemini-2.5-flash` | `gemma2:27b` | $0.075-0.30/1M |
| Vision tasks | `qwen2.5vl:7b` | - | Free (local) |
| Embeddings | `Alibaba-NLP/gte-Qwen2-1.5B-instruct` | - | Free (local) |
| Development/testing | `gemma2:27b` | - | Free (local) |
| Long documents (>100K) | `claude-4-7-opus` | `gemini-2.5-flash` | $15-75/1M |

---

## Decision Tree

### 1. Is this production traffic?

**YES** → Use paid-tier models
- Primary: `gemini-2.5-flash` (OpenRouter)
- Reason: Reliable, no quota limits, fast
- Cost: ~$5/month for typical usage

**NO** → Is network available?
- **YES** → Use paid-tier anyway (cost is minimal)
- **NO** → Use local models (Ollama)

### 2. What type of task?

#### Chat/RAG Queries
- **Production**: `gemini-2.5-flash` (OpenRouter)
- **Development**: `gemma2:27b` (Ollama)
- **Offline**: `gemma2:27b` (Ollama)

#### Vision Tasks
- **All cases**: `qwen2.5vl:7b` (Ollama)
- Reason: Local, unlimited, good quality

#### Embeddings
- **All cases**: `Alibaba-NLP/gte-Qwen2-1.5B-instruct` (local)
- Reason: Already optimal, 1536-dim, 0.2s per query

#### Long Documents (>100K tokens)
- **High quality needed**: `claude-4-7-opus` (200K context)
- **Cost-sensitive**: `gemini-2.5-flash` (1M context)

---

## Model Profiles

### Gemini 2.5 Flash (OpenRouter)

**Use for:** Production RAG, chat, indexing

**Pros:**
- Fast response (2-3s)
- Reliable (99.9% uptime)
- No quota limits
- Vision-capable
- 1M token context

**Cons:**
- Costs $0.075-0.30 per 1M tokens
- Requires network

**When to use:**
- Production traffic
- Connector indexing
- RAG baseline tests
- Any time reliability matters

**Configuration:**
```yaml
- litellm_params:
    api_base: https://openrouter.ai/api/v1
    api_key: os.environ/OPENROUTER_API_KEY
    model: google/gemini-2.5-flash
    timeout: 300
  model_name: gemini-flash
```

---

### Gemma2 27B (Ollama)

**Use for:** Development, testing, offline operation

**Pros:**
- Free (local)
- Unlimited usage
- Good quality
- No network required

**Cons:**
- Slower (5-10s first load, 2-3s cached)
- Requires 5.4GB VRAM
- 8K context limit

**When to use:**
- Development/testing
- Offline operation
- Fallback when quota exhausted
- Cost-sensitive workloads

**Configuration:**
```yaml
- litellm_params:
    api_base: http://ollama:11434/v1
    api_key: none
    model: gemma2:27b
    timeout: 600
  model_name: gemma2
```

---

### Qwen2.5-VL 7B (Ollama)

**Use for:** Vision tasks (image analysis, PDF with figures)

**Pros:**
- Free (local)
- Unlimited usage
- Vision-capable
- 32K context

**Cons:**
- Slower than cloud models
- Requires 3.2GB VRAM

**When to use:**
- Image analysis
- PDF indexing with figures
- Vision RAG
- Any vision task

**Configuration:**
```yaml
- litellm_params:
    api_base: http://ollama:11434/v1
    api_key: none
    model: qwen2.5vl:7b
    timeout: 600
  model_name: qwen-rag-vision
```

---

### Claude 4.7 Opus (OpenRouter)

**Use for:** High-quality, long-context tasks

**Pros:**
- Highest quality
- 200K context
- Thinking mode
- Vision-capable

**Cons:**
- Expensive ($15-75 per 1M tokens)
- Slower (10-30s)

**When to use:**
- Long documents (>100K tokens)
- Complex reasoning
- High-stakes decisions
- When quality > cost

**Configuration:**
```yaml
- litellm_params:
    api_base: https://openrouter.ai/api/v1
    api_key: os.environ/OPENROUTER_API_KEY
    model: anthropic/claude-4-7-opus
    timeout: 600
  model_name: claude-opus
```

---

## Cost Optimization Strategies

### 1. Use Local Models for Development

**Before:**
```bash
# Uses paid API for every test
pytest deployment/onyx/tests/
```

**After:**
```bash
# Set local model for tests
export LITELLM_MODEL=gemma2
pytest deployment/onyx/tests/
```

**Savings:** $0.50-1.00 per test run

---

### 2. Cache Embeddings

**Before:**
```python
# Regenerate embeddings every time
embedding = generate_embedding(text)
```

**After:**
```python
# Cache embeddings by content hash
cache_key = hashlib.sha256(text.encode()).hexdigest()
embedding = cache.get(cache_key) or generate_embedding(text)
cache.set(cache_key, embedding)
```

**Savings:** 90% reduction in embedding API calls

---

### 3. Use Appropriate Context Windows

**Before:**
```python
# Send full 100K document to model
response = llm.complete(full_document)
```

**After:**
```python
# Send only relevant chunks (5K tokens)
relevant_chunks = retrieve_top_k(query, k=5)
response = llm.complete(relevant_chunks)
```

**Savings:** 95% reduction in token usage

---

### 4. Batch Similar Requests

**Before:**
```python
# Process documents one at a time
for doc in documents:
    summary = llm.summarize(doc)
```

**After:**
```python
# Batch documents together
batch = "\n\n---\n\n".join(documents[:10])
summaries = llm.summarize_batch(batch)
```

**Savings:** 50% reduction in API calls

---

## Quota Management

### Prevention

1. **Use paid-tier models** for production
   - No quota limits
   - Predictable costs
   - Better reliability

2. **Set cooldown periods**
   ```yaml
   router_settings:
     cooldown_time: 300  # 5 minutes
   ```

3. **Monitor usage daily**
   ```bash
   python3 deployment/helper/monitor_model_quotas.py
   ```

### Detection

1. **Watch for 429 errors** in logs
   ```bash
   docker logs onyx-litellm --since 24h | grep "429"
   ```

2. **Check quota status** before long runs
   ```bash
   python3 deployment/helper/litellm_quota_check.py
   ```

3. **Alert on quota warnings** (>80% usage)
   ```bash
   # Add to monitoring/check_health.sh
   python3 deployment/helper/monitor_model_quotas.py --alert-threshold 80
   ```

### Recovery

1. **Automatic fallback** to local models
   - LiteLLM router handles this automatically
   - Logs fallback events

2. **Manual intervention**
   ```bash
   # Switch to local-only mode
   export LITELLM_FALLBACK_ONLY=true
   docker restart onyx-litellm
   ```

3. **Upgrade to paid tier**
   - DashScope: Enable paid tier in console
   - OpenRouter: Add payment method

---

## Monitoring Commands

### Daily Health Check
```bash
# Check all model routes
python3 deployment/helper/litellm_quota_check.py --timeout 90

# Check Ollama models available
docker exec onyx-ollama ollama list

# Check for quota errors
docker logs onyx-litellm --since 24h | grep -i "quota\|429\|rate"
```

### Weekly Review
```bash
# Review OpenRouter usage
open https://openrouter.ai/activity

# Check cost trends
python3 deployment/helper/analyze_model_costs.py --last-7-days

# Verify local fallbacks
docker exec onyx-ollama ollama list | grep -E "gemma2|qwen2.5vl|mistral"
```

---

## Troubleshooting

### Issue: Quota Exhausted

**Symptoms:**
- 429 errors in logs
- "quota exceeded" messages
- Slow or failed requests

**Solution:**
1. Check quota status: `python3 deployment/helper/monitor_model_quotas.py`
2. Switch to local models: Set `LITELLM_FALLBACK_ONLY=true`
3. Upgrade to paid tier or wait for quota reset

---

### Issue: Slow Responses

**Symptoms:**
- Requests taking >30s
- Timeout errors

**Solution:**
1. Check if using local models (first load is slow)
2. Verify network connectivity
3. Switch to faster model (gemini-flash)
4. Increase timeout in config

---

### Issue: High Costs

**Symptoms:**
- OpenRouter bill >$50/month
- Unexpected charges

**Solution:**
1. Review usage: `python3 deployment/helper/analyze_model_costs.py`
2. Switch development to local models
3. Implement caching strategies
4. Reduce context window sizes

---

## Best Practices

1. **Use paid models for production** - Reliability > cost
2. **Use local models for development** - Cost > speed
3. **Cache embeddings** - Avoid regeneration
4. **Monitor quota daily** - Prevent surprises
5. **Set budget alerts** - OpenRouter dashboard
6. **Keep local fallbacks ready** - Ollama models pulled
7. **Test before deploying** - Verify model changes
8. **Document model choices** - Why this model for this task

---

## References

- [OpenRouter Pricing](https://openrouter.ai/docs/pricing)
- [Ollama Models](https://ollama.ai/library)
- [LiteLLM Router](https://docs.litellm.ai/docs/routing)
- [Model Optimization Report](./model-optimization-report.md)
