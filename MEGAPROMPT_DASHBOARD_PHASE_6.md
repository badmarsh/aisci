# AiSci Dashboard Integration - Phase 6 Megaprompt

## Context
In Phase 5, we successfully built the backend connections and API endpoints (`/api/literature`, `/api/evidence`, `/api/fits`, `/api/tasks`, `/api/agents`, `/api/activity`). The backend is fully operational, tailing real logs, executing real sub-agents, and syncing Markdown bidirectionally to the SQLite database.

However, a Playwright audit of the frontend (`apps/aisci-dashboard`) revealed that the React components are still partially wired. Many pages still rely on hardcoded variables and imports from `src/lib/mock-data.ts`. The UI is rendering static numbers while ignoring the live data fetched from the API.

## Goal
Phase 6 focuses exclusively on the frontend. The objective is to sever all ties to `mock-data.ts`, enforce dynamic data rendering across all pages, fix mismatched mapping logic, and ensure the UI strictly reflects the live API responses.

## Phase 6 Tasks

### 1. Completely Remove Mock Data
- Delete the file `apps/aisci-dashboard/src/lib/mock-data.ts`.
- Ensure no files in `src/routes/` or `src/components/` attempt to import it. This will intentionally break the build so you can find every place that needs dynamic wiring.

### 2. Overview Page (`src/routes/index.tsx`)
- The KPI cards currently display hardcoded fallback values (e.g., `+0 today`, `pending review`). Update these computations to dynamically calculate from the fetched API arrays (`literature`, `fitsData`, `evidence`, `tasks`).
- The "Recent Activity" feed relies on the static `activityFeed` array.
  - Implement a `fetchActivity()` function in `src/lib/api.ts` calling `GET /api/activity`.
  - Use `@tanstack/react-query` to fetch this data on the Overview page.
  - Map the backend `ActivityModel` properties to the timeline UI.

### 3. Literature Intake (`src/routes/literature.tsx`)
- The "Total Papers", "arXiv Papers", and "OpenAlex Papers" stats cards are hardcoded. Calculate these dynamically from the `papers` array returned by `fetchLiterature()`.
- The "Claim Type Distribution" chart imports `claimTypeDist` from mock data. Dynamically compute this breakdown by traversing `papers.flatMap(p => p.claimList)` and aggregating claim categories.

### 4. Evidence Ledger (`src/routes/evidence.tsx`)
- The frontend `statusStyles` and KPI filtering checks rely on strict case-sensitive strings (e.g., `e.status === "Supported"`).
- Review the `status` string exactly as it is returned by the `GET /api/evidence` backend. Ensure the React component's string matching (or capitalization) aligns perfectly with the backend so the 🟢/🟡/🔵 summary dots count >0 claims.

### 5. Mutations & Agent Logs
- Verify that `apps/aisci-dashboard/src/components/Sidebar.tsx` and the page headers are actually invoking the `triggerIngest()` and `triggerFits()` mutations.
- The `GET /api/agents` endpoint correctly streams the tail logs. If the UI displays errors parsing the `log` array (or if the formatting is broken), refine the presentation in `agents.tsx`.
- Make sure `updateEvidence` and `updateTask` mutations in `evidence.tsx` and `tasks.tsx` properly invalidate the Query Client to refresh the tables upon success.

## Instructions for the Agent
1. **Frontend Only**: You should not need to modify any Python backend files. This phase is purely about fixing the React components.
2. **Handle Loading States**: Since we are moving entirely to live data, ensure `isLoading` states return elegant `Skeleton` placeholders rather than empty screens.
3. **TypeScript Safety**: When removing `mock-data.ts`, be sure to migrate any essential TypeScript interfaces (like `EvidenceRow`, `Paper`, `TaskModel`) into a dedicated `types.ts` file or directly into `src/lib/api.ts`.
4. **Validation**: Run the Vite dev server (`npm run dev`) and manually verify the Overview, Literature, Evidence, and Task pages render real DB metrics before completing the phase.
