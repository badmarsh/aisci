# AiSci Ecosystem Architecture: Deep Design Document

**Date:** 2026-05-31  
**Status:** Living Architecture Document  
**Purpose:** Define how agenda, knowledge, issues, tools, and pipelines are organized across GitHub, Onyx, Multica, and DeerFlow

---

## Executive Summary

After deep analysis of the current AiSci stack and evaluation of Multica's interactive agent management capabilities, this document proposes a **four-layer architecture** where:

1. **GitHub** = Canonical source of truth (code, evidence, decisions)
2. **Onyx** = Knowledge retrieval layer (RAG, literature, context)
3. **Multica** = Interactive task orchestration (agents, projects, execution)
4. **DeerFlow** = Research automation backend (multi-agent workflows, fact-checking)

The key insight: **Multica should be the interactive frontend that mirrors and orchestrates, not replace canonical sources.**

---

## Current State Analysis

### What We Have (May 2026)

#### **GitHub Repository Structure**
```
aisci/
├── research/robert/
│   ├── evidence-ledger.md          # 18 claims, status tracking
│   ├── next-actions.md             # Science task queue
│   └── runs/YYYY-MM-DD-*/          # Reproducible artifacts
├── physics/src/
│   ├── fitting_pipeline.py         # Scipy curve fitting
│   ├── data_loader.py              # HEPData integration
│   └── sympy_validation_agent.py   # Symbolic math
├── agent-skills/                    # 16 vendor-neutral skills
├── docs/
│   ├── ops/Multica Issues     # 84 operational items
│   ├── decisions/                  # Architecture decisions
│   └── ops/                        # Deployment guides
└── deployment/
    ├── onyx/                       # RAG stack
    ├── deer-flow/                  # Research orchestration
    └── helper/                     # 30+ utility scripts
```

#### **Onyx RAG System**
- **629 chunks** indexed across 279 documents
- **4 personas**: physics-validator, evidence-auditor, referee-prep, arxiv-intake
- **Hybrid search**: OpenSearch (vector) + Vespa (BM25)
- **MCP integration**: Scite, Consensus (OAuth), INSPIRE-HEP (planned)
- **Status**: Q1/Q2/Q4 passing, Q3/Q5 structural gaps (docs/ not indexed)

#### **DeerFlow v2**
- **Tree-of-Thoughts planner** (3 branches, depth 4)
- **Parallel search**: Tavily + Brave + Exa + Serper
- **Fact-checker agent**: Post-generation validation
- **Academic tools**: ArXiv, Semantic Scholar
- **Status**: Merged improvements (commit 4b62828), MCP tools broken (langchain_mcp_adapters bug)

#### **Test Coverage**
- Physics: 679 lines, CI active
- DeerFlow: 23 integration tests
- Onyx: 1,186 lines (45 unit templates, 11 integration templates)
- Secret hygiene: 8 tests
- **Gap**: Onyx unit tests are templates, need implementation

---

## The Core Problem

### **Fragmentation Across 4 Systems**

| What | Where Now | Problem |
|------|-----------|---------|
| **Tasks** | next-actions.md (markdown) | Not interactive, no agent assignment, manual tracking |
| **Evidence** | evidence-ledger.md (markdown) | No automated validation, agents can't query status easily |
| **Issues** | Multica Issues (84 items) | Mixed with GitHub Issues, unclear ownership |
| **Knowledge** | Onyx (indexed) + GitHub (source) | Agents must know which to query when |
| **Execution** | Manual script runs | No visibility into what's running, no progress tracking |
| **Skills** | agent-skills/ (16 skills) | Not discoverable by agents, no reuse metrics |

### **What Multica Solves**

✅ **Interactive task board** - Visual kanban, drag-drop, real-time updates  
✅ **Agent assignment** - Agents are teammates, not scripts  
✅ **Execution visibility** - See what's running, progress, blockers  
✅ **Skill compounding** - Every solution becomes reusable  
✅ **Multi-project organization** - Separate physics, papers, infra  
✅ **Autopilots** - Scheduled recurring work (daily RAG eval, weekly lit scan)

---

## Proposed Architecture: Four-Layer Model

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: CANONICAL TRUTH (GitHub)                              │
│  • evidence-ledger.md (18 claims)                               │
│  • next-actions.md (science queue)                              │
│  • Multica Issues (ops queue)                              │
│  • docs/decisions/ (architecture)                               │
│  • physics/src/ (code)                                          │
│  • agent-skills/ (16 skills)                                    │
│                                                                  │
│  Role: Source of truth, version control, audit trail            │
│  Update frequency: On every commit                              │
└─────────────────────────────────────────────────────────────────┘
                              ↕ (bidirectional sync)
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: KNOWLEDGE RETRIEVAL (Onyx)                            │
│  • 629 chunks indexed                                           │
│  • 4 personas (physics-validator, evidence-auditor, etc.)       │
│  • Hybrid search (OpenSearch + Vespa)                           │
│  • MCP: Scite, Consensus, INSPIRE-HEP                           │
│                                                                  │
│  Role: Context for agents, literature validation                │
│  Update frequency: Daily auto-refresh (86400s)                  │
└─────────────────────────────────────────────────────────────────┘
                              ↕ (query during execution)
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: INTERACTIVE ORCHESTRATION (Multica)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Project:     │  │ Project:     │  │ Project:     │          │
│  │ AiSci-Core   │  │ AiSci-Papers │  │ AiSci-Infra  │          │
│  │              │  │              │  │              │          │
│  │ • O-03 fit   │  │ • B-01 data  │  │ • Key rot.   │          │
│  │ • SymPy val  │  │ • RAG eval   │  │ • MCP setup  │          │
│  │ • Plot gen   │  │ • Lit scan   │  │ • Test impl  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  Agents: PhysicsFitter, LiteratureScout, DevOpsHelper           │
│  Role: Task management, execution visibility, agent assignment  │
│  Update frequency: Real-time (WebSocket)                        │
└─────────────────────────────────────────────────────────────────┘
                              ↕ (executes via)
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 4: EXECUTION BACKENDS (DeerFlow + Claude Code + Bash)    │
│  • DeerFlow: Research tasks (ToT, parallel search, fact-check)  │
│  • Claude Code: Coding tasks (fitting, tests, scripts)          │
│  • Bash: Simple automation (git, docker, file ops)              │
│                                                                  │
│  Role: Actual work execution, tool calling, file generation     │
│  Update frequency: On-demand (triggered by Multica)             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Design Principles

### 1. **Single Source of Truth (GitHub)**

**Rule:** GitHub is always authoritative. Multica mirrors, never replaces.

**Implementation:**
- Evidence ledger stays in `research/robert/evidence-ledger.md`
- Multica issues link to evidence ledger rows
- On task completion, agent commits to GitHub first, then updates Multica

**Sync pattern:**
```
GitHub commit → Webhook → Multica updates issue status
Multica issue closed → Agent commits → GitHub updated
```

### 2. **Knowledge as a Service (Onyx)**

**Rule:** Agents query Onyx for context, never duplicate knowledge in Multica.

**Implementation:**
- Multica agents call Onyx API during execution
- Onyx indexes GitHub canonical files (evidence ledger, decisions, ops docs)
- Agents use Onyx personas for domain-specific retrieval

**Query pattern:**
```python
# In Multica agent skill
def get_claim_status(claim_id: str) -> str:
    """Query Onyx for current claim status."""
    result = onyx_client.search(
        query=f"What is the status of claim {claim_id}?",
        persona="physics-validator",
        top_k=3
    )
    return result.passages[0].text
```

### 3. **Interactive Orchestration (Multica)**

**Rule:** Multica is the control plane, not the data plane.

**What Multica stores:**
- Task metadata (title, assignee, status, priority)
- Execution logs (agent actions, progress, errors)
- Skill usage metrics (which skills used when, success rate)
- Project organization (which tasks belong to which project)

**What Multica does NOT store:**
- Evidence ledger content (lives in GitHub)
- Literature PDFs (lives in Onyx)
- Code (lives in GitHub)
- Architecture decisions (lives in GitHub docs/decisions/)

### 4. **Execution Backends as Plugins (DeerFlow/Claude/Bash)**

**Rule:** Multica doesn't care how work gets done, only that it gets done.

**Implementation:**
- Multica agent "PhysicsFitter" can use Claude Code OR DeerFlow
- User chooses backend when creating agent
- Multica tracks execution, backend does the work

---

## Detailed Design: Three Projects

### **Project 1: AiSci-Core** (Physics Validation)

**Purpose:** Science pipeline execution, evidence validation, reproducible runs

**Agents:**
1. **PhysicsFitter**
   - Backend: Claude Code
   - Skills: reproducible-physics-runner, fit-quality-auditor
   - Working dir: `/home/ubuntu/aisci`
   - Typical tasks: "Run O-03 fitting pipeline", "Generate chi²/ndf heatmap"

2. **SymPyValidator**
   - Backend: Claude Code
   - Skills: symbolic-math-validator
   - Typical tasks: "Verify Lorentz covariance symbolically", "Check dimensional analysis"

3. **PlotGenerator**
   - Backend: Claude Code
   - Skills: scientific-visualization
   - Typical tasks: "Generate residual plots for all bins", "Create pull histogram"

**Multica Project Structure:**
```
AiSci-Core/
├── Issues/
│   ├── #1: O-03 Tsallis fitting [PhysicsFitter] [In Progress]
│   ├── #2: Verify U < 1c subluminal [SymPyValidator] [Done]
│   ├── #3: Generate chi²/ndf heatmap [PlotGenerator] [Todo]
│   └── #4: Run sensitivity scan [PhysicsFitter] [Blocked by B-01]
├── Skills/
│   ├── reproducible-physics-runner (used 12 times, 100% success)
│   ├── fit-quality-auditor (used 8 times, 87% success)
│   └── scientific-visualization (used 15 times, 93% success)
└── Autopilots/
    └── Daily fit quality check (9 AM, PhysicsFitter)
```

**Sync with GitHub:**
- Issue #1 links to `research/robert/next-actions.md` → O-03 section
- On completion, PhysicsFitter commits to `research/robert/runs/2026-05-31-o03-fitting/`
- Evidence ledger updated: O-03 status → Confirmed
- Multica issue #1 auto-closes via webhook

---

### **Project 2: AiSci-Papers** (Literature & RAG)

**Purpose:** Literature discovery, RAG evaluation, citation validation

**Agents:**
1. **LiteratureScout**
   - Backend: DeerFlow
   - Skills: paper-lookup, literature-review, onyx-rag-eval-manager
   - Typical tasks: "Find per-bin pT spectra (B-01)", "Scan ArXiv for Tsallis papers"

2. **RAGEvaluator**
   - Backend: Claude Code
   - Skills: onyx-rag-eval-manager
   - Typical tasks: "Run Q1-Q5 evaluation set", "Check RAG baseline regression"

3. **CitationValidator**
   - Backend: DeerFlow (uses Scite/Consensus MCP)
   - Skills: citation-validator
   - Typical tasks: "Validate all DOIs in evidence ledger", "Check Bíró paper citations"

**Multica Project Structure:**
```
AiSci-Papers/
├── Issues/
│   ├── #5: B-01 Find per-bin data [LiteratureScout] [In Progress]
│   ├── #6: Daily RAG eval Q1-Q5 [RAGEvaluator] [Recurring]
│   ├── #7: Validate Khuntia citations [CitationValidator] [Done]
│   └── #8: Weekly ArXiv scan [LiteratureScout] [Scheduled Mon 10AM]
├── Skills/
│   ├── paper-lookup (used 45 times, 91% success)
│   ├── literature-review (used 8 times, 100% success)
│   └── onyx-rag-eval-manager (used 23 times, 78% success)
└── Autopilots/
    ├── Daily RAG evaluation (9 AM, RAGEvaluator)
    └── Weekly ArXiv scan (Mon 10 AM, LiteratureScout)
```

**Knowledge Integration:**
- LiteratureScout queries Onyx: "What HEPData records are referenced in evidence ledger?"
- Onyx returns: `ins1419652` from indexed evidence-ledger.md
- LiteratureScout searches INSPIRE-HEP for related records
- Validates findings via Scite/Consensus MCP
- Commits `fit_input.csv` to GitHub
- Updates evidence ledger: B-01 → Resolved

---

### **Project 3: AiSci-Infra** (DevOps & Platform)

**Purpose:** Docker configs, secret management, MCP integration, test implementation

**Agents:**
1. **DevOpsHelper**
   - Backend: Claude Code
   - Skills: secret-config-auditor, platform-backlog-manager
   - Typical tasks: "Rotate API keys", "Update docker-compose", "Fix nginx config"

2. **TestImplementer**
   - Backend: Claude Code
   - Skills: python-testing-patterns
   - Typical tasks: "Implement Onyx unit tests", "Add RAG regression tests"

3. **MCPIntegrator**
   - Backend: Claude Code
   - Skills: mcp-integration-planner
   - Typical tasks: "Add INSPIRE-HEP MCP server", "Fix Scite OAuth flow"

**Multica Project Structure:**
```
AiSci-Infra/
├── Issues/
│   ├── #9: Rotate all API keys [DevOpsHelper] [Done]
│   ├── #10: Implement Onyx unit tests [TestImplementer] [In Progress]
│   ├── #11: Add INSPIRE-HEP MCP [MCPIntegrator] [Todo]
│   └── #12: Fix DeerFlow MCP loading [DevOpsHelper] [Blocked]
├── Skills/
│   ├── secret-config-auditor (used 5 times, 100% success)
│   ├── platform-backlog-manager (used 12 times, 92% success)
│   └── mcp-integration-planner (used 3 times, 67% success)
└── Autopilots/
    └── Weekly secret hygiene scan (Sun 11 PM, DevOpsHelper)
```

---

## What Gets Mirrored to Multica Frontend

### ✅ **Mirror These (Interactive Management)**

1. **Tasks from next-actions.md**
   - O-03, O-04, O-05 → Multica issues in AiSci-Core
   - Assignable to agents
   - Track progress, blockers, completion

2. **Platform backlog items (P0/P1 only)**
   - Top 20 items from Multica Issues → Multica issues in AiSci-Infra
   - P2/P3 stay in markdown (too low priority for interactive tracking)

3. **Agent skills (metadata only)**
   - Skill name, description, success rate
   - NOT the full SKILL.md content (stays in GitHub)
   - Multica shows: "reproducible-physics-runner: used 12 times, 100% success"

4. **Evidence ledger status (read-only view)**
   - Multica dashboard widget: "18 claims: 8 Sanity checked, 3 Confirmed, 2 Blocked, 5 Open"
   - Click → opens GitHub evidence-ledger.md (not editable in Multica)

5. **Execution logs**
   - Agent actions, tool calls, errors
   - Stored in Multica for debugging
   - NOT committed to GitHub (too verbose)

### ❌ **Do NOT Mirror These (Stay in GitHub)**

1. **Evidence ledger content**
   - Too complex for Multica UI
   - Needs markdown tables, LaTeX, citations
   - Agents commit directly to GitHub

2. **Code**
   - physics/src/ stays in GitHub
   - Agents edit via git, not Multica UI

3. **Architecture decisions**
   - docs/decisions/ stays in GitHub
   - Too long-form for task tracking

4. **Literature PDFs**
   - Stay in Onyx corpus
   - Multica doesn't store documents

5. **Detailed skill implementations**
   - agent-skills/*/SKILL.md stays in GitHub
   - Multica shows usage metrics only

---

## Sync Mechanisms

### **GitHub → Multica (Webhook)**

```yaml
# .github/workflows/multica-sync.yml
on:
  push:
    paths:
      - 'research/robert/evidence-ledger.md'
      - 'research/robert/next-actions.md'
      - 'docs/ops/Multica Issues'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Parse changed files
        run: |
          # Extract new tasks from next-actions.md
          # Create/update Multica issues via API
          
      - name: Update evidence ledger status
        run: |
          # Parse evidence ledger table
          # Update Multica dashboard widget
```

### **Multica → GitHub (Agent Commits)**

```python
# In Multica agent skill
def complete_task(task_id: str, results: dict):
    """Complete task and sync to GitHub."""
    # 1. Commit results to GitHub
    git_commit(
        files=[results["output_file"]],
        message=f"science(O-03): {results['summary']}\n\nCompleted by agent PhysicsFitter"
    )
    
    # 2. Update evidence ledger
    update_evidence_ledger(
        claim_id=results["claim_id"],
        status="Confirmed",
        evidence=f"research/robert/runs/{results['run_dir']}/"
    )
    
    # 3. Close Multica issue
    multica_client.close_issue(task_id)
```

### **Onyx ↔ Multica (Query During Execution)**

```python
# Agent queries Onyx for context before starting work
def start_task(task: MulticaTask):
    # 1. Query Onyx for relevant context
    context = onyx_client.search(
        query=f"What is the current status of {task.title}?",
        persona="physics-validator"
    )
    
    # 2. Check if work already done
    if "Confirmed" in context.passages[0].text:
        return "Task already completed, skipping"
    
    # 3. Get requirements from Onyx
    requirements = onyx_client.search(
        query=f"What are the requirements for {task.title}?",
        persona="physics-validator"
    )
    
    # 4. Execute task with context
    execute_with_context(task, context, requirements)
```

---

## Implementation Roadmap

### **Phase 1: Setup Multica (Week 1)**

**Day 1-2: Install and Configure**
```bash
# Install Multica
brew install multica-ai/tap/multica

# Setup for self-hosted
multica setup self-host

# Create workspace
multica workspace create aisci --slug aisci

# Start daemon
multica daemon start
```

**Day 3-4: Create Projects**
- Create 3 projects: AiSci-Core, AiSci-Papers, AiSci-Infra
- Set descriptions, configure settings
- Add project-specific skills

**Day 5-7: Create Agents**
- PhysicsFitter (Claude Code backend)
- LiteratureScout (DeerFlow backend)
- DevOpsHelper (Claude Code backend)
- Test each agent with simple task

**Deliverable:** Multica running with 3 projects, 3 agents, daemon healthy

---

### **Phase 2: Migrate Tasks (Week 2)**

**Day 1-3: Science Tasks**
- Parse `research/robert/next-actions.md`
- Create Multica issues for O-03, O-04, O-05
- Link to evidence ledger rows
- Assign to PhysicsFitter

**Day 4-5: Platform Tasks**
- Parse `docs/ops/Multica Issues` (P0/P1 only)
- Create Multica issues for top 20 items
- Assign to DevOpsHelper or TestImplementer

**Day 6-7: Test Execution**
- Run one task end-to-end
- Verify: Multica → Agent → GitHub commit → Multica update
- Fix any sync issues

**Deliverable:** 25+ tasks migrated, 1 successful end-to-end execution

---

### **Phase 3: Onyx Integration (Week 3)**

**Day 1-2: Agent Query Layer**
- Implement `onyx_client.py` wrapper
- Add to Multica agent skills
- Test: Agent queries Onyx for evidence ledger status

**Day 3-4: Index Canonical Files**
- Add Multica project files to Onyx connector
- Verify: Onyx can retrieve from evidence ledger, next-actions, platform-backlog
- Test RAG evaluation with Multica context

**Day 5-7: MCP Integration**
- Wire Scite/Consensus MCP to Multica agents
- Test: LiteratureScout validates citations via Scite
- Fix OAuth flows if needed

**Deliverable:** Agents can query Onyx, use MCP tools, retrieve canonical file context

---

### **Phase 4: Autopilots (Week 4)**

**Day 1-2: Daily RAG Evaluation**
```yaml
name: "Daily RAG Eval"
schedule: "0 9 * * *"  # 9 AM daily
action:
  create_issue:
    title: "Daily RAG eval: Run Q1-Q5 test set"
    assignee: "RAGEvaluator"
    project: "AiSci-Papers"
```

**Day 3-4: Weekly Literature Scan**
```yaml
name: "Weekly ArXiv Scan"
schedule: "0 10 * * 1"  # Monday 10 AM
action:
  create_issue:
    title: "Scan ArXiv for new Tsallis/BGBW papers"
    assignee: "LiteratureScout"
    project: "AiSci-Papers"
```

**Day 5-7: Monitoring and Alerts**
- Set up Multica webhooks for task failures
- Add Slack/email notifications
- Create dashboard for agent health

**Deliverable:** 2+ autopilots running, notifications working, dashboard live

---

## Success Metrics

### **Quantitative**

| Metric | Baseline (Now) | Target (3 months) |
|--------|----------------|-------------------|
| Time to complete O-03 task | 4-6 hours manual | 30 min automated |
| Tasks tracked in Multica | 0 | 50+ |
| Agent success rate | N/A | 85%+ |
| Evidence ledger updates/week | 1-2 manual | 5-10 automated |
| RAG evaluation frequency | Ad-hoc | Daily automated |
| Literature scans/month | 0 | 4 (weekly) |

### **Qualitative**

✅ **Visibility**: Can see what agents are working on at any time  
✅ **Reproducibility**: Every agent action has audit trail in GitHub  
✅ **Knowledge reuse**: Agents query Onyx instead of re-reading files  
✅ **Skill compounding**: Solutions become reusable skills  
✅ **Reduced context switching**: Multica UI instead of 4 different tools  
✅ **Autonomous execution**: Agents work while you sleep

---

## Risk Mitigation

### **Risk 1: Sync Drift (Multica ↔ GitHub)**

**Mitigation:**
- GitHub is always source of truth
- Multica issues link to GitHub files (not duplicate content)
- Webhook validates sync every commit
- Daily reconciliation job checks for drift

### **Risk 2: Agent Hallucination (Wrong Evidence Updates)**

**Mitigation:**
- Agents query Onyx for current state before updating
- Evidence ledger updates require chi²/ndf gate pass
- Human review required for status promotion (Sanity checked → Confirmed)
- All agent commits tagged with `Co-Authored-By: Agent <agent@multica.ai>`

### **Risk 3: Onyx Index Staleness**

**Mitigation:**
- Daily auto-refresh (86400s) for all connectors
- Multica agents check Onyx index timestamp before querying
- Manual refresh trigger in Multica UI
- Alert if index age > 48 hours

### **Risk 4: Multica Downtime (Can't Access Tasks)**

**Mitigation:**
- GitHub remains accessible (canonical source)
- Agents can run directly via CLI (bypass Multica)
- Task queue persists in Multica database (survives restart)
- Backup: Export Multica issues to GitHub Issues weekly

---

## Open Questions for User Decision

### **1. Skill Mirroring Depth**

**Option A:** Mirror only skill metadata (name, usage count, success rate)  
**Option B:** Mirror full skill content (SKILL.md) to Multica  
**Option C:** Hybrid (metadata in Multica, link to GitHub for full content)

**Recommendation:** Option C (hybrid)

### **2. Evidence Ledger in Multica**

**Option A:** Read-only dashboard widget (status summary only)  
**Option B:** Full table view in Multica (editable)  
**Option C:** No mirroring (agents commit directly to GitHub)

**Recommendation:** Option A (read-only widget)

### **3. Test Results Storage**

**Option A:** Store in Multica (execution logs)  
**Option B:** Store in GitHub (commit test artifacts)  
**Option C:** Both (logs in Multica, artifacts in GitHub)

**Recommendation:** Option C (both)

### **4. DeerFlow MCP Bug**

**Current blocker:** langchain_mcp_adapters UnboundLocalError breaks all MCP tools

**Option A:** Wait for upstream fix  
**Option B:** Patch library locally  
**Option C:** Use Multica agents with direct MCP calls (bypass DeerFlow)

**Recommendation:** Option C short-term, Option B long-term

---

## Conclusion

This architecture provides:

✅ **Single source of truth** (GitHub) with interactive frontend (Multica)  
✅ **Knowledge as a service** (Onyx) queried by agents during execution  
✅ **Autonomous execution** with full visibility and audit trail  
✅ **Skill compounding** through reusable agent skills  
✅ **Scalability** from 3 agents to 10+ without architectural changes

**Next step:** User decides on open questions, then we implement Phase 1 (Week 1: Setup Multica).

---

**Document Status:** Draft for review  
**Author:** Claude Opus 4.7  
**Review Required:** Marek (user decision on open questions)  
**Implementation Start:** After approval
