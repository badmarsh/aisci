# AiSci Documentation Drift Analysis & Harmonization Plan
**Date:** 2026-05-30  
**Scope:** aisci project docs vs. Onyx and DeerFlow deployments

---

## Executive Summary

**Drift Severity:** MODERATE - Documentation is outdated but not critically wrong

**Key Issues Found:**
1. ✅ Onyx deployment fully documented and current
2. ✅ DeerFlow deployment runtime verified; tool smoke test still pending
3. ⚠️ Port references inconsistent
4. ⚠️ HANDOFF.md references resolved issues
5. ⚠️ Missing recent fixes in main docs
6. ⚠️ Embedding model configuration drift

---

## Drift Analysis by Category

### 1. Service Status & Availability

#### Current Reality (2026-05-30)
```
Onyx Services: 18/18 running ✅
- Web UI: http://localhost:80 (also :3000)
- API: Running, embeddings working
- LiteLLM: http://localhost:4001 (not 4000)
- MCP Proxy: http://localhost:8095
- Ollama: http://localhost:11434
- Unstructured: http://localhost:8000 (not 9560)

DeerFlow Services: RUNNING ✅
- UI: http://localhost:2026 returns HTTP 200
- Runtime: deer-flow-nginx, deer-flow-gateway, deer-flow-frontend running
- Caveat: authenticated UI/API tool execution still needs a focused smoke test
```

#### Documentation Claims
```
README.md:
- Onyx RAG: http://localhost:3000 ✅
- DeerFlow: http://localhost:2026 ✅

deployment-reference.md:
- LiteLLM proxy: http://localhost:4000 ❌ (actually 4001)
- Unstructured: http://localhost:9560 ❌ (actually 8000)
- MCP proxy: http://localhost:8095 ✅
```

**Drift:** Port numbers were incorrect; DeerFlow status was stale and is now verified running

---

### 2. Embedding Model Configuration

#### Current Reality
```
Active Model: Alibaba-NLP/gte-Qwen2-1.5B-instruct
Dimensions: 1536
Index: danswer_chunk_alibaba_nlp_gte_qwen2_1_5b_instruct
Status: WORKING ✅ (fixed 2026-05-30)
```

#### Documentation Claims
```
platform-backlog.md (row 18):
- Claims: Alibaba/1536 active ✅
- Status: Accurate

ACTION_PLAN.md:
- No specific embedding model mentioned
- References "Alibaba/1536 OpenSearch retrieval direction" ✅
```

**Drift:** Documentation is accurate but doesn't reflect today's fix

---

### 3. LLM Model Status

#### Current Reality (2026-05-30)
```
Working Models:
✅ qwen-omni-flash (Dashscope)
✅ meta/llama-3.1-8b-instruct (NVIDIA)
✅ qwen-embedder (Ollama local)

Broken Models:
❌ qwen-max (quota exhausted)
⚠️ local-context-model (slow 24s first load)
⚠️ nvidia/nemotron-nano-9b-v2 (reasoning format)
```

#### Documentation Claims
```
HANDOFF.md:
- "Reconfigured to use gemini-2.5-flash as primary" ❌
- "Qwen models hitting quota limits" ✅ (partially true)

platform-backlog.md (row 16):
- "qwen-cloud-fast, RAG routes, and local fallback all probe green" ⚠️
- Doesn't mention qwen-max quota exhaustion
```

**Drift:** HANDOFF.md references old DeerFlow config, not current Onyx LiteLLM

---

### 4. Recent Fixes Not Documented

#### Fixes Applied Today (2026-05-30)
1. ✅ Fixed inference model database configuration
2. ✅ Tested all 10 LLM models
3. ✅ Analyzed all Docker logs
4. ✅ Created 5 new documentation files

#### Documentation Status
```
New Files Created (not referenced):
- DEPLOYMENT_ANALYSIS.md
- FIXES_APPLIED.md
- LLM_TEST_REPORT.md
- COMPLETE_SUMMARY.md
- DOCKER_LOGS_ANALYSIS.md
- onyx-litellm_config.yaml.recommended
```

**Drift:** Recent work not integrated into canonical docs

---

### 5. HANDOFF.md Staleness

#### Issues Referenced in HANDOFF.md
```
1. "Onyx Bridge: 502 Bad Gateway" ❌
   - Status: RESOLVED (Onyx running healthy)
   
2. "Scite & Consensus MCP fail to load" ⚠️
   - Status: proxy routes verified separately; DeerFlow MCP-client tool execution still needs an authenticated smoke test
   
3. "Model Configuration: gemini-2.5-flash" ❌
   - Status: OUTDATED (refers to DeerFlow, not current Onyx)
   
4. "Drive Mounting fixed" ✅
   - Status: Documented but not verified
```

**Drift:** HANDOFF.md is stale and confusing

---

### 6. DeerFlow Deployment Status

#### Documentation Claims
```
README.md: "DeerFlow: http://localhost:2026"
deployment-reference.md: "DeerFlow | http://localhost:2026"
platform-backlog.md: Multiple DeerFlow entries (rows 40-51)
```

#### Current Reality
```
Status: RUNNING ✅
- `deer-flow-nginx`, `deer-flow-gateway`, and `deer-flow-frontend` are up
- `http://127.0.0.1:2026` returns HTTP 200
- Raw API curl is auth-protected
- End-to-end tool execution from DeerFlow still needs a focused authenticated test
```

**Drift:** DeerFlow status was stale; runtime is now verified, tool execution remains the open check

---

### 7. Port Binding Documentation

#### Current Reality (Verified)
```
Onyx:
- Web: 127.0.0.1:80, 127.0.0.1:3000
- LiteLLM: 127.0.0.1:4001
- MCP Proxy: 127.0.0.1:8095
- Unstructured: 127.0.0.1:8000
- Image Bridge: 127.0.0.1:8090

All bound to 127.0.0.1 ✅ (security fix applied)
```

#### Documentation Claims
```
deployment-reference.md:
- LiteLLM: localhost:4000 ❌ (should be 4001)
- Unstructured: localhost:9560 ❌ (should be 8000)
- MCP proxy: localhost:8095 ✅
```

**Drift:** Port numbers incorrect in docs

---

## Harmonization Plan

### Phase 1: Immediate Corrections (High Priority)

#### 1.1 Update deployment-reference.md
```markdown
CHANGE:
| LiteLLM proxy | http://localhost:4000 |
TO:
| LiteLLM proxy | http://localhost:4001 |

CHANGE:
| Unstructured | http://localhost:9560 |
TO:
| Unstructured | http://localhost:8000 |

ADD:
| Onyx Web (alt) | http://localhost:80 |
| Image Bridge | http://localhost:8090 |
```

#### 1.2 Update HANDOFF.md
```markdown
ADD HEADER:
> **Status:** This handoff is from 2026-05-20. See COMPLETE_SUMMARY.md 
> for current status as of 2026-05-30.

UPDATE:
- "Onyx 502 Error" → RESOLVED
- "Model Configuration" → See LLM_TEST_REPORT.md
- Add pointer to new documentation
```

#### 1.3 Update platform-backlog.md
```markdown
ADD NEW ROW (P0):
| P0 | Onyx | Inference embedding model database drift | Database had wrong model name causing 500 errors | Fixed 2026-05-30: Updated to Alibaba-NLP/gte-Qwen2-1.5B-instruct | Done |

ADD NEW ROW (P1):
| P1 | Onyx | LLM model testing and quota management | qwen-max quota exhausted, 3/10 models working | Tested 2026-05-30: See LLM_TEST_REPORT.md | Done |

ADD NEW ROW (P2):
| P2 | Onyx | Docker logs analysis | Comprehensive log analysis needed | Completed 2026-05-30: See DOCKER_LOGS_ANALYSIS.md | Done |
```

---

### Phase 2: DeerFlow Status Verification (Medium Priority)

#### 2.1 Verify DeerFlow Deployment
```bash
cd /home/ubuntu/aisci/deployment/deer-flow
docker compose ps
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:2026
```

#### 2.2 Update Documentation Based on Status
Verified running:
- Update README.md with current status
- Verify MCP integration
- Test Onyx bridge from an authenticated DeerFlow session

---

### Phase 3: Documentation Consolidation (Medium Priority)

#### 3.1 Create Master Status Document
```
File: docs/ops/CURRENT_STATUS.md

Contents:
- Service status (all 18 Onyx + DeerFlow)
- Recent fixes (link to FIXES_APPLIED.md)
- Known issues (link to platform-backlog.md)
- Port mappings (canonical list)
- Model status (link to LLM_TEST_REPORT.md)
- Last updated: 2026-05-30
```

#### 3.2 Update ACTION_PLAN.md
```markdown
ADD:
- Link to CURRENT_STATUS.md as a snapshot
- Reference recent embedding fix
- Update milestone status
```

#### 3.3 Update README.md
```markdown
ADD SECTION:
## 📊 Current System Status
Last updated: 2026-05-30

**Onyx:** ✅ All 18 services running
- Embedding: Working (1536-dim)
- Search: Operational
- LLM Models: 3/10 working (see LLM_TEST_REPORT.md)

**DeerFlow:** ✅ Running; MCP/tool execution smoke test pending

For deployment details and open work: [docs/ops/deployment-reference.md], [docs/ops/platform-backlog.md]. Snapshot: [docs/ops/CURRENT_STATUS.md].
```

---

### Phase 4: Embedding Model Documentation (Low Priority)

#### 4.1 Document Today's Fix
```
File: docs/ops/embedding-model-fix-2026-05-30.md

Contents:
- Problem: qwen3-embedding:latest in database
- Solution: Updated to Alibaba-NLP/gte-Qwen2-1.5B-instruct
- Verification: Embeddings working at 0.2s
- Related: FIXES_APPLIED.md
```

#### 4.2 Update platform-backlog.md
```markdown
UPDATE ROW 18:
Add note: "Database model name fixed 2026-05-30 (was qwen3-embedding:latest)"
```

---

### Phase 5: Cleanup & Archival (Low Priority)

#### 5.1 Archive Stale Documents
```bash
# Move to docs/archive/
- HANDOFF.md → docs/archive/handoff-2026-05-20.md
```

#### 5.2 Create Fresh HANDOFF.md
```markdown
# Current System Handoff
Last updated: 2026-05-30

## Quick Status
- Onyx: ✅ Fully operational
- DeerFlow: ✅ Running; MCP/tool execution smoke test pending
- Recent fixes: See COMPLETE_SUMMARY.md

## For Next Session
1. Test DeerFlow MCP integration
3. Rotate exposed API keys (see platform-backlog.md P0)

## Documentation
- Status snapshot: docs/ops/CURRENT_STATUS.md
- Platform backlog: docs/ops/platform-backlog.md
- Recent fixes: deployment/onyx/FIXES_APPLIED.md
```

---

## Critical Drift Items

### 🔴 Critical (Fix Immediately)

1. **Port numbers in deployment-reference.md**
   - Impact: Users can't connect to services
   - Fix: Update 4000→4001, 9560→8000

2. **DeerFlow status stale**
   - Impact: Incorrect docs can send operators into unnecessary restart work
   - Fix: Runtime verified and documented as running; tool execution smoke test remains

### 🟡 Important (Fix Soon)

3. **HANDOFF.md is stale**
   - Impact: Confusing for next session
   - Fix: Archive and create fresh version

4. **Recent fixes not in canonical docs**
   - Impact: Work not discoverable
   - Fix: Update platform-backlog.md

5. **LLM model status not documented**
   - Impact: Users don't know which models work
   - Fix: Reference LLM_TEST_REPORT.md

### 🟢 Nice to Have (Fix Eventually)

6. **No status snapshot document**
   - Impact: Status scattered across files
   - Fix: Create CURRENT_STATUS.md as a snapshot, not a replacement for `platform-backlog.md`

7. **Embedding fix not documented**
   - Impact: Future debugging harder
   - Fix: Create embedding-model-fix doc

---

## Recommended Execution Order

1. ✅ **Verify DeerFlow status** (5 min) — running
2. ✅ **Fix port numbers** in deployment-reference.md (2 min)
3. ✅ **Update HANDOFF.md** with status note (2 min)
4. ✅ **Add recent fixes** to platform-backlog.md (5 min)
5. ✅ **Create CURRENT_STATUS.md snapshot** (10 min)
6. ✅ **Update README.md** with current status (5 min)
7. ⏭️ **Archive old HANDOFF.md** (optional)
8. ⏭️ **Create embedding fix doc** (optional)

**Total Time:** ~30 minutes for critical items

---

## Files Requiring Updates

### Must Update
1. `docs/ops/deployment-reference.md` - Port numbers
2. `HANDOFF.md` - Add status note
3. `docs/ops/platform-backlog.md` - Add recent fixes
4. `README.md` - Add current status section

### Should Create
5. `docs/ops/CURRENT_STATUS.md` - Status snapshot

### Optional
6. `docs/ops/embedding-model-fix-2026-05-30.md`
7. `docs/archive/handoff-2026-05-20.md`

---

## Validation Checklist

After harmonization, verify:
- [ ] All port numbers match actual deployment
- [x] DeerFlow runtime status is documented
- [ ] Recent fixes are referenced
- [ ] HANDOFF.md is current
- [ ] README.md reflects reality
- [ ] platform-backlog.md is up to date
- [ ] New docs are linked from canonical files

---

**Analysis by:** Claude Opus 4.7  
**Date:** 2026-05-30  
**Drift Severity:** MODERATE  
**Estimated Fix Time:** 30 minutes
