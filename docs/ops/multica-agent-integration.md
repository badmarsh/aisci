# Multica Agent Integration & K-Dense Scientific Skills

**Date:** 2026-05-31  
**Status:** Research complete, skills installed, integration wrappers drafted  
**Related:** MULTICA_SETUP.md, AGENTS.md

## Overview

This document captures the integration architecture for connecting Multica task management with the AiSci agent ecosystem, plus the evaluation and installation of K-Dense scientific agent skills.

## 1. K-Dense Scientific Skills Installation

### Installed Skills (10 high-priority)

Successfully installed 10 HEP-relevant skills from [K-Dense-AI/scientific-agent-skills](https://github.com/k-dense-ai/scientific-agent-skills) (143 total skills, MIT licensed):

| Skill | Priority | Relevance | Location |
|-------|----------|-----------|----------|
| **sympy** | Critical | Symbolic math, already using sympy_validation_agent.py | `.agents/skills/sympy/` |
| **paper-lookup** | Critical | 10 academic DBs (arXiv, Semantic Scholar, OpenAlex) | `.agents/skills/paper-lookup/` |
| **scientific-visualization** | Critical | Publication-quality plots for pT spectra, chi²/ndf | `.agents/skills/scientific-visualization/` |
| **statistical-analysis** | Critical | AIC/BIC, chi²/ndf, covariance gates | `.agents/skills/statistical-analysis/` |
| **matplotlib** | High | Fit plots, residuals, multiplicity bins | `.agents/skills/matplotlib/` |
| **astropy** | High | HEP phenomenology overlaps with coordinate/stats tools | `.agents/skills/astropy/` |
| **database-lookup** | High | 78 databases including arXiv, CrossRef, Semantic Scholar | `.agents/skills/database-lookup/` |
| **literature-review** | High | Structured review against Khuntia/Rath baselines | `.agents/skills/literature-review/` |
| **scientific-writing** | Medium | Manuscript polish, referee response drafting | `.agents/skills/scientific-writing/` |
| **peer-review** | Medium | Structured critique before submission | `.agents/skills/peer-review/` |

### Installation Method

```bash
cd /home/ubuntu/aisci

# Install critical skills (batch 1)
npx skills add K-Dense-AI/scientific-agent-skills \
  --skill sympy \
  --skill paper-lookup \
  --skill scientific-visualization \
  --skill statistical-analysis

# Install high-priority skills (batch 2)
npx skills add K-Dense-AI/scientific-agent-skills \
  --skill matplotlib \
  --skill astropy \
  --skill database-lookup \
  --skill literature-review \
  --skill scientific-writing \
  --skill peer-review
```

Skills are installed to `.agents/skills/` and symlinked to Claude Code's skill directory. Each skill includes:
- `SKILL.md` - comprehensive documentation with examples
- Dependencies managed via `uv` package manager
- Security scanned (Cisco AI Defense Skill Scanner)

### Skills NOT Installed

~60% of the 142 K-Dense skills are bio/genomics/clinical/pharma focused and not relevant to HEP phenomenology:
- Bioinformatics (23 skills): BioPython, Scanpy, scRNA-seq pipelines
- Cheminformatics (10 skills): RDKit, drug discovery tools
- Clinical research (8 skills): EHR modeling, clinical decision support
- Medical imaging (3 skills): DICOM, pathology
- Lab automation (6 skills): Opentrons, PyLabRobot

### Security Notes

Per AGENTS.md: "prefer improving shared skills over adding model-specific instruction files"
- K-Dense skills follow same SKILL.md standard as existing `agent-skills/`
- Drop in cleanly with zero friction
- ⚠️ Scan community-contributed skills before using (K-Dense core ones are vetted)
- Security risk assessments: Most skills are "Safe" or "Low Risk", a few "Med Risk" (acceptable for research use)

## 2. Multica Integration Architecture

### Vision

Integrate Multica task management with existing sandboxed agent runtimes:

```
Multica Board
     │
     ├── assigns card → Onyx Craft Agent (sandboxed)
     │                    • RAG over physics corpus
     │                    • physics-validator persona
     │                    • writes to evidence-ledger.md
     │
     ├── assigns card → DeerFlow Agent (sandboxed)
     │                    • deep research + web search
     │                    • InspireHEP / arXiv MCP tools
     │                    • multi-step physics workflows
     │
     └── assigns card → Claude Code / Codex
                          • code execution
                          • fitting_pipeline.py runs
                          • deployment tasks
```

### Integration Status

| Integration | Status | Implementation |
|------------|--------|----------------|
| Multica → Claude Code/Codex | ✅ Native | Ships out of box |
| Multica → DeerFlow | 🟡 Possible | DeerFlow exposes REST at localhost:2026/api; needs custom runtime config |
| Multica → Onyx Craft Agent | 🟡 Possible | Onyx has no native agent-runner API; needs thin wrapper script |

### Implementation Files

1. **`deployment/helper/trigger_onyx_agent.py`** - Wrapper script for Onyx Craft integration
   - Fetches Multica card details via `multica issue get`
   - Triggers Onyx agent run with specified persona and corpus
   - Writes results to `research/robert/evidence-ledger.md`
   - Exit codes: 0=success, 1=config error, 2=API error, 3=run failed

2. **`deployment/helper/multica_custom_runtimes.yaml`** - Conceptual runtime configuration
   - DeerFlow HTTP runtime (POST to localhost:2026/api/runs)
   - Onyx Craft command runtime (calls trigger_onyx_agent.py)
   - Routing rules by assignee or label
   - Environment variables: `DEERFLOW_JWT`, `ONYX_API_KEY`

### DeerFlow Integration

DeerFlow exposes REST API at `http://localhost:2026/api`:

```yaml
deerflow:
  type: http
  endpoint: http://localhost:2026/api/runs
  headers:
    Authorization: Bearer ${DEERFLOW_JWT}
  timeout: 30m
```

**Next steps:**
- Verify DeerFlow API at localhost:2026/api/docs (OpenAPI spec)
- Test authentication with DEERFLOW_JWT
- Confirm request/response format matches template

### Onyx Craft Integration

Onyx has no native agent-runner API, so we use a command wrapper:

```yaml
onyx-craft:
  type: command
  command: python
  args:
    - deployment/helper/trigger_onyx_agent.py
    - --card-id
    - "{issue_id}"
    - --persona
    - physics-validator
  timeout: 20m
```

**Next steps:**
- Verify Onyx API endpoint (assumed http://localhost:3000)
- Confirm Onyx API request format
- Test wrapper script with sample Multica card
- Set ONYX_API_KEY environment variable

## 3. Testing Plan

### Phase 1: Skill Validation
- [ ] Test SymPy skill with symbolic validation task
- [ ] Test paper-lookup with arXiv/InspireHEP query
- [ ] Test scientific-visualization with pT spectrum plot
- [ ] Test statistical-analysis with chi²/ndf calculation

### Phase 2: Integration Testing
- [ ] Create test Multica cards for each runtime
- [ ] Test DeerFlow HTTP endpoint integration
  - Verify localhost:2026/api is reachable
  - Test authentication with DEERFLOW_JWT
  - Assign test card to DeerFlow agent
- [ ] Test Onyx Craft wrapper integration
  - Verify Onyx API endpoint
  - Test trigger_onyx_agent.py with sample card
  - Assign test card to Onyx agent
- [ ] Verify Claude Code integration (should work out of box)

### Phase 3: End-to-End Workflow
- [ ] Create physics validation card → assign to Onyx
- [ ] Create literature review card → assign to DeerFlow
- [ ] Create code execution card → assign to Claude Code
- [ ] Verify results written to correct locations
- [ ] Check evidence-ledger.md updates from Onyx

## 4. Open Questions

1. **DeerFlow API Format**
   - Does localhost:2026/api support the needed operations?
   - What's the exact request/response format?
   - Is DEERFLOW_JWT the correct auth mechanism?

2. **Onyx API Details**
   - What's the actual Onyx agent API endpoint?
   - Does Onyx have a REST API or only CLI?
   - How to pass Multica card context to Onyx agents?

3. **Skill Registry**
   - Should we create a unified skill registry across all three runtimes?
   - How to share K-Dense skills with DeerFlow and Onyx?

4. **Phased Rollout**
   - Install all 10 high-priority skills at once? ✅ Done
   - Or phase them in gradually? (Decided: all at once for research phase)

## 5. References

- K-Dense repo: https://github.com/k-dense-ai/scientific-agent-skills
- Multica custom runtimes: https://multica.ai/docs/daemon-runtimes
- DeerFlow API: http://localhost:2026/api (check /docs for OpenAPI spec)
- Existing agent-skills: `/home/ubuntu/aisci/agent-skills/`
- K-Dense skills location: `/home/ubuntu/aisci/.agents/skills/`

## 6. Next Actions

1. **Immediate (Done)**
   - ✅ Evaluate K-Dense skills for AiSci fit
   - ✅ Install 10 high-priority skills
   - ✅ Draft trigger_onyx_agent.py wrapper
   - ✅ Draft multica_custom_runtimes.yaml config

2. **Short-term (Next sprint)**
   - Verify DeerFlow API endpoint and authentication
   - Verify Onyx API endpoint and request format
   - Test trigger_onyx_agent.py with sample card
   - Create test Multica cards for each runtime

3. **Medium-term**
   - Configure Multica daemon with custom runtimes
   - Run end-to-end integration tests
   - Document runtime selection patterns
   - Add monitoring/logging for agent runs

4. **Long-term**
   - Evaluate additional K-Dense skills as needs arise
   - Consider contributing AiSci-specific skills back to K-Dense
   - Explore unified skill registry across runtimes
