## MEGAPROMPT — AISCI-DASHBOARD-PAGES

**Role:**  
You are an AI product designer and UX engineer working on the AiSci Dashboard frontend (`deployment/aisci-dashboard/src/routes`). Your goal is to enrich and sharpen the scientific control-plane UX for autonomous heavy-ion physics research, while keeping the existing architecture (TanStack Router, React Query, Shadcn UI) intact.  

You must improve the **copy, layout, drill-down affordances, and scientific semantics** across all pages:

- `/` → Portfolio overview (projects list)  
- `/projects/$projectId/` → Scientific operations overview (main dashboard)  
- `/projects/$projectId/literature` → Literature control plane  
- `/projects/$projectId/evidence` → Evidence ledger view  
- `/projects/$projectId/fits` → Fit quality and spectra view  
- `/projects/$projectId/anomalies` → Anomaly queue  
- `/projects/$projectId/tasks` → Next actions / task management  
- `/projects/$projectId/agents` → Agent workload / pipelines  
- `/projects/$projectId/jobs` → Job history & logs  

Use the existing files and components as the baseline, not a full rewrite.  

***

### 1. Portfolio page (`index.tsx` — `/`)

**Current:**  
- Simple “Research Portfolio” title + cards for each project, with ID badge and basic capabilities.  

**Improve:**

1. **Make project cards more “scientific”:**  
   - Add a tiny status strip under the title: e.g. “Active collisions: N”, “Open anomalies: M” pulled from a lightweight project summary API (if available).  
   - Replace generic “Enter Control Plane” with domain-specific CTAs: “Enter heavy-ion spectra control plane”, “Open evidence-ledger workspace”, using `project.research_type` to tailor wording.  

2. **Clarify sensitivity and capabilities:**  
   - Use sensitivity badges as a mini legend: “Internal draft”, “Publishable”, “High-stakes”.  
   - Group capabilities into semantic clusters: `[Physics fits] [Evidence tracking] [Agent orchestration]` rather than raw strings.  

3. **Discovery hints:**  
   - Add a small paragraph above the grid: “AiSci currently manages N physics projects. Each card summarizes its current state and supported workflows.”  

***

### 2. Project overview page (`projects.$projectId.index.tsx` — `/projects/$projectId/`)

**Current:**
- Hero section (“Scientific operations overview”), pipelines buttons (Run Full Pipeline, Ingest Literature), hard-coded uptime, metric cards, chi² vs multiplicity chart, agent workload panel, database sync, anomaly queue, activity stream, generated hypotheses.  

**Improve:**

1. **Hero section: replace static “99.98% uptime” with live instrumentation.**  
   - Compute pipeline health from `fetchProjectHealth` and recent `JobExecutions` instead of hardcoded `99.98%`.  
   - Show last run time for fit-validation and ingest-validation pipelines: “Last full pipeline: 2026‑07‑12 14:21 CEST”.  

2. **Pipeline buttons: add clear pre-flight context.**  
   - Before triggering `fit-validation` or `ingest-validation`, show a short checklist: “Will run: (1) ingest newest literature, (2) run fits across 10 multiplicity bins, (3) sync evidence ledger.”  
   - On hover, show a tooltip referencing the pipelines: “Uses Ignition pipeline `fit-validation` in backend.”  

3. **Metrics: make spark lines semantically meaningful.**  
   - Replace static arrays `[2,4,3,5,4,6]` etc with short time-series derived from activity feed or overview history (even if mocked for now, remove pure placeholder values).  
   - Adjust labels to be more research-specific: “Papers ingested (last 24h)”, “Active fit runs”, “Claims under review”, “Open tasks for publication”.  

4. **Chi² chart: tie legend and copy to evidence.**  
   - Update panel copy to reference the evidence ledger: “Model χ²/ndf vs multiplicity, aligned with current evidence-ledger baselines.”  
   - Add click interaction: clicking a data point opens `/projects/$projectId/fits` pre-filtered to that bin/model.  

5. **Agent workload panel:**  
   - Add a mini filter at top: “Show: Active / Blocked / Idle”.  
   - Highlight agents with `status === "failed"|"blocked"` and provide a link to `/projects/$projectId/jobs` with a pre-filter for that agent’s pipeline.  

6. **Database sync panel:**  
   - Remove hard-coded “100%, 12 ms, Consistent” and drive these numbers from real metrics (e.g., last sync time from `/activity`, approximate latency from health).  
   - Add a subtle warning state when overview or evidence queries error (e.g., show “Degraded” with amber badge and hint to re-run `sync` pipeline).  

7. **Anomaly queue & Activity stream:**  
   - Make anomalies list items clickable: clicking goes to `/projects/$projectId/anomalies` with filters set to that bin/model/severity.  
   - For activity entries, add a small tag for `item.action` category (“Fit run”, “Evidence update”, “Pipeline error”), and a link to the relevant view.  

8. **Generated Hypotheses panel:**  
   - Prepend a brief description: “These hypotheses are machine-generated suggestions that must be evaluated through the evidence ledger before being considered publishable.”  
   - Provide CTA buttons in each idea row: “Send to tasks”, “Open related evidence” (hook into `/tasks` and `/evidence` APIs).  

***

### 3. Literature page (`projects.$projectId.literature.tsx`)

**Goals:**  
- Present papers as **live scientific assets**: show claim counts, bridge flags, Scite-style support/contrast counts, and direct links.  

**Prompt improvements:**

1. **Table columns:**  
   - Title (with icon for source: OpenAlex/arXiv).  
   - Category (nucl-ex/nucl-th/hep-ph etc).  
   - Claims extracted (count, colored by confidence).  
   - Bridge flag (“Interdisciplinary bridge” badge).  
   - Scite summary (“Supported N, Contrasting M”).  

2. **Row expansion:**  
   - Expand row to show sample claims, dataset names, and direct evidence entries associated with this paper.  
   - Provide a “Promote to evidence ledger” button that opens `/evidence` filtered to claims from that paper.  

3. **Filters:**  
   - Add filters for date range, category, bridge only, and claim confidence (LOW/MEDIUM/HIGH).  

***

### 4. Evidence page (`projects.$projectId.evidence.tsx`)

**Goals:**  
- Make the ledger feel like a **scientific review board** UI.  

**Prompt improvements:**

1. **Evidence rows:**  
   - Show claim text, status badge (`Proposed`, `Sanity checked`, `Validated`, `Rejected`, `Bulletproof`, `Tension`), nextGate, linked run ID, and supporting papers count.  
   - Distinguish internal computational findings vs literature-backed claims with icons (“calculation” vs “paper”).  

2. **Review workflow:**  
   - Add bulk actions: “Select N claims → request review”, with clear disclaimers about materialization workflow.  
   - For each claim, show a mini timeline: last status change, reviewer, and link to review requests panel.  

3. **Cross-links:**  
   - Clicking a “run” field opens `/projects/$projectId/fits` anchored to that run/bin.  
   - Clicking supporting papers opens `/projects/$projectId/literature` filtered to those sources.  

***

### 5. Fits page (`projects.$projectId.fits.tsx`)

**Goals:**  
- Give a **deep, interactive view** of fit quality and model behavior.  

**Prompt improvements:**

1. **Run selector:**  
   - Clear label: “Run directory (yyyy-mm-dd-name)” with tooltips showing summary of that run (models used, bins covered).  

2. **Tables & charts:**  
   - Add AIC/BIC columns per model-per-bin once backend exposes them.  
   - Provide residuals plots (data–fit)/σ and parameter trend plots (T, ⟨β⟩ vs multiplicity).  

3. **Callbacks into evidence/anomalies:**  
   - Clicking a row with high χ² automatically surfaces related anomalies and evidence entries.  

***

### 6. Anomalies page (`projects.$projectId.anomalies.tsx`)

**Goals:**  
- Make anomalies actionable.  

**Prompt improvements:**

1. **Categorization:**  
   - Group anomalies by type: “Fit-range sensitive”, “High χ²”, “Correlation degeneracy (T–β, T–q)”, “Boundary violation”.  

2. **Actions:**  
   - Provide “Create task” button for each anomaly, populating a draft in `/tasks` with details.  
   - Provide “Open fits for this bin/model” link.  

***

### 7. Tasks page (`projects.$projectId.tasks.tsx`)

**Goals:**  
- Turn tasks into a **publication pipeline** (from idea → evidence → manuscript patch).  

**Prompt improvements:**

1. **Task cards:**  
   - Show links back to evidence claims and anomalies they are meant to address.  
   - Add statuses aligned with science: “Scoping”, “Data collection”, “Fit rerun”, “Manuscript patch ready”, “Submitted”.  

2. **Filters:**  
   - Filter by type (physics, software, documentation) and by target (literature, fits, ledger).  

***

### 8. Agents page (`projects.$projectId.agents.tsx`)

**Goals:**  
- Make it clear how each agent fits into the research fabric.  

**Prompt improvements:**

1. **Agent list:**  
   - For each agent, show its scope (“literature ingest”, “fit pipeline”, “ledger sync”, “hypothesis generation”), last run duration, and error rate.  

2. **Controls:**  
   - Add per-agent “Run” button and “View logs” link to `/jobs` filtered by that agent/pipeline.  

***

### 9. Jobs page (`projects.$projectId.jobs.tsx`)

**Goals:**  
- Provide a clean, inspectable history for pipeline runs.  

**Prompt improvements:**

1. **Job table:**  
   - Show pipeline id, status, requester, start/end, duration, and a small badge for “Artifacts produced” (with count).  

2. **Log viewer:**  
   - Use SSE stream with consistent styling, showing key phases (`DRY-RUN`, `EXEC`, `SYNC`).  
   - Add quick links to open related fits/evidence when a job finishes.  

***

### Behavioral rules

- Do **not** remove existing architecture (PageShell, QueryErrorBoundary, Suspense, Shadcn UI); enrich and refine UX and copy on top of it.  
- Replace purely decorative or hard-coded numbers with live, scientifically meaningful ones wherever possible.  
- Make every panel and chart a gateway into deeper views: overview → fits/evidence/anomalies/tasks/jobs.  
- Keep the visual style consistent with the current “control plane” aesthetic, but reduce any “AI template” feel (generic gradients, arbitrary uptime percentages, placeholder stats).
