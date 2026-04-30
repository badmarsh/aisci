## How the 15 Skills Connect

The skills form **two parallel pipelines** — one for platform/ops work, one for science work — joined by three shared infrastructure skills that both pipelines call.

***

## The Skill Map

```
╔══════════════════════════════════════════════════════════════════════╗
║                     SHARED INFRASTRUCTURE                           ║
║                                                                      ║
║   git-worktree-guard          analysis-handoff-router               ║
║   (safe git context           (post-analysis routing:               ║
║    before any change)          implement / persist / handoff)        ║
║                                                                      ║
║   secret-config-auditor                                             ║
║   (called by ops pipeline whenever config files are touched)        ║
╚══════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════╗   ╔══════════════════════════════════╗
║    OPS / PLATFORM PIPELINE   ║   ║      SCIENCE PIPELINE            ║
║                              ║   ║                                  ║
║  aisci-tech-kickoff          ║   ║  reproducible-physics-runner     ║
║  (session start → pick task) ║   ║  (run scripts, save artifacts)   ║
║          ↓                   ║   ║          ↓                       ║
║  aisci-ops-auditor           ║   ║  science-source-curator          ║
║  (full structured audit)     ║   ║  (extract evidence from papers)  ║
║          ↓                   ║   ║          ↓                       ║
║  onyx-rag-eval-manager       ║   ║  science-ledger-manager          ║
║  (RAG tuning gate)           ║   ║  (update claim status)           ║
║          ↓                   ║   ║          ↓                       ║
║  mcp-integration-planner     ║   ║  science-report-writer           ║
║  (plan/document MCP tools)   ║   ║  (draft referee reports)         ║
║          ↓                   ║   ║                                  ║
║  platform-backlog-manager    ║   ║  researcher-docs-manager         ║
║  (maintain task tracker)     ║   ║  (curate all docs, archive stale)║
║          ↓                   ║   ╚══════════════════════════════════╝
║  vendored-runtime-maintainer ║
║  (deer-flow / vendor trees)  ║
║          ↓                   ║
║  aisci-tech-kickoff          ║
║  (next session kickoff)      ║
╚══════════════════════════════╝
```


***

## Daily Routine — Coding Agent Manager

### Morning Kickoff (every session start)

**Skill: `aisci-tech-kickoff`**

1. Read `AGENTS.md`, `ACTION_PLAN.md`, `docs/ops/platform-backlog.md`, and `docs/decisions/2026-04-26-system-boundaries.md`
2. Run `git status --short` + `git log --oneline -n 20` via `git-worktree-guard`
3. Pick the single highest-leverage non-destructive task from the backlog
4. State the task and reasoning — then implement or produce an approval-gated plan
5. End with `analysis-handoff-router`: implement now / persist / handoff prompt

***

### Platform Work Session

**Trigger:** Docker, Onyx, LiteLLM, MCP, compose, or deployment issue

```
aisci-tech-kickoff          → orient, pick task
  ├── aisci-ops-auditor      → full audit if broad investigation needed
  ├── onyx-rag-eval-manager  → if RAG settings are on the table
  ├── mcp-integration-planner → if adding or fixing an MCP endpoint
  ├── secret-config-auditor  → always when touching .env / config files
  ├── vendored-runtime-maintainer → if deer-flow tree is involved
  └── platform-backlog-manager → write accepted findings to backlog
        └── analysis-handoff-router → close session with 3 options
```


***

### Science Work Session

**Trigger:** Robert asks to run a fit, check a claim, find a paper, or draft a report

```
science-source-curator       → find and extract evidence from papers/Onyx
  └── reproducible-physics-runner → run scripts, save dated run artifacts
        └── science-ledger-manager → update claim status in evidence-ledger.md
              └── science-report-writer → only when a claim reaches Supported
                    └── researcher-docs-manager → archive anything stale this session
```


***

### End-of-Session Cleanup (always)

**Skill: `researcher-docs-manager`** — runs last in any session:

- Are any docs now stale because of today's work?
- Did any new file get created that belongs in archive?
- Is `platform-backlog.md` or `evidence-ledger.md` still in sync?

Then `analysis-handoff-router` closes with the three options for the next agent.

***

## Where New Ideas Come From

The system has **three idea inlets**, each with a designated landing zone:


| Source | Landing Zone | Skill That Processes It |
| :-- | :-- | :-- |
| Robert's physics intuition / new manuscript version | `research/robert/next-actions.md` | `science-ledger-manager` to gate it, `science-source-curator` to ground it |
| Platform observation (something broken, slow, or missing) | `docs/ops/platform-backlog.md` | `platform-backlog-manager` to add it, `aisci-ops-auditor` to audit the surrounding area |
| External literature (new paper on Tsallis, arXiv preprint, Scite citation) | `research/robert/science-questions.md` or directly into `evidence-ledger.md` | `science-source-curator` → `science-ledger-manager` |

**Ideas never go directly into `ACTION_PLAN.md`** — that file is high-level tracking only . An idea becomes real only after it lands in one of the two canonical trackers (`platform-backlog.md` or `next-actions.md`) and is accepted by the user.

***

## The One Rule That Holds Everything Together

Every skill in both pipelines respects the same hard boundary: **platform details stay out of science files; science claims stay out of ops files** . `analysis-handoff-router` is the enforcement mechanism — it routes findings to the correct canonical file rather than letting an agent dump everything into one document. `git-worktree-guard` ensures no session ever destroys another agent's in-progress work. `secret-config-auditor` ensures no credentials ever cross into `docs/`. These three cross-cutting skills are the connective tissue that makes the rest safe to run in parallel.
