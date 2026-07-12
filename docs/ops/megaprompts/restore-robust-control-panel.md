# Restore Robust Control Panel & Pipeline Interactions

## Context
Recent stabilization efforts simplified the AiSci dashboard UI significantly, removing the interactive "Run" buttons and pipeline triggering forms. The user noted: "the aisci dashboard has lost all the run buttons, its much more simple, its worse than before."

Your objective is to **analyze the recent UI simplifications** and **rebuild a robust, interactive, and premium control panel** while maintaining the current underlying project isolation, capability gating, and SQLite backend stability.

## Required Tasks

### 1. Analyze the Missing Capabilities
- Review `deployment/aisci-dashboard/src/routes/projects.$projectId.fits.tsx` and `projects.$projectId.index.tsx`.
- Review `deployment/aisci-dashboard/src/lib/api.ts` (specifically `triggerPipeline`, `dryRunPipeline`, `updateTask`).
- Note that the UI currently only reads data (e.g., rendering static tables for fits and jobs) and lacks interactive controls to execute new fits, dispatch pipelines, or manipulate tasks.

### 2. Restore Pipeline & Run Interactions
- **Add Action Interfaces**: Reintroduce interactive "Run" buttons and pipeline dispatch forms. For example:
  - In the **Fits Page** (`projects.$projectId.fits.tsx`), add a "Run New Fit" button that triggers the fitting pipeline for the current project.
  - In the **Tasks & Agents Pages**, add controls to manually invoke agent pipelines or update task statuses.
  - In the **Overview Page**, restore any quick-action capabilities (like "Run Full Pipeline" or "Ingest Literature").
- **State Management**: Implement loading states, success toasts (via `sonner`), and error handling when dispatching pipelines using the API functions from `src/lib/api.ts`.

### 3. Elevate UI Aesthetics
- Re-apply premium web design aesthetics (as mandated by the `web_application_development` system instructions).
- **Glassmorphism & Gradients**: Ensure the newly added interaction panels use rich, subtle gradients and the existing `glass-card` utilities.
- **Micro-animations**: Add hover states, active states, and transition animations (e.g., `fade-in-up`) to the interactive buttons and forms.
- **Feedback Loops**: When a user clicks "Run Pipeline", the button should indicate processing state, and upon completion, a toast notification should appear. The relevant data tables should proactively invalidate and refetch via TanStack Query.

### 4. Constraints
- **Preserve Architecture**: Do not break the routing structure or the capability gating (e.g., `phd-audit` should not see "Run Fit" buttons).
- **Backend Safety**: Ensure that the "Run" buttons correctly pass the `projectId` to the API. Do not hardcode project IDs.
- **Dependencies**: Use existing UI components (e.g., Radix UI primitives, Lucide icons, existing Tailwind config).

## Execution Guidelines
1. Start by inspecting `src/lib/api.ts` to see what mutation endpoints are available.
2. Modify the frontend routes (e.g., `projects.$projectId.fits.tsx`, `projects.$projectId.jobs.tsx`, `projects.$projectId.index.tsx`) to add action buttons.
3. Integrate `useMutation` from `@tanstack/react-query` to connect the UI buttons to the backend endpoints gracefully.
4. Verify the frontend builds correctly by running `npm run typecheck && npm run build`.
5. Summarize your additions clearly to the user, highlighting the restored interactive capabilities.
