# v0 Dashboard Redesign Megaprompt

**Instructions:** Run the `deployment/helper/v0-tooling/v0_upload.js` script to initialize a new v0 chat with this prompt and the files from `deployment/aisci-dashboard` automatically attached. Alternatively, you can copy and paste the prompt below into your v0.dev chat and use your MCP integration to read the codebase.

---

### The Prompt

**System & Stack Context:**
I am building the frontend for "AiSci" - an advanced agentic scientific research platform. The stack is TanStack Start (React 19), Tailwind CSS 4, shadcn/ui, Recharts, and Lucide React. 

**Codebase Context:**
The relevant files from the `deployment/aisci-dashboard` frontend codebase are provided in this chat (either via attached files or MCP). Read the existing components, layout, and routing configuration from these files, and build the redesign directly on top of this foundation instead of starting from scratch.

**Objective ($5 Premium Redesign):**
I want you to spend the maximum compute necessary to generate a highly premium, state-of-the-art "Scientific Aesthetic" redesign of our main dashboard, starting from the existing `deployment/aisci-dashboard` codebase. It should feel like a next-generation control plane for AI physics research. Do NOT give me a basic MVP; use micro-animations, glassmorphism, high-density data views, and a sophisticated dark mode palette (deep slate backgrounds with vibrant, legible neon data accents like cyan, amber, and violet). 

**Core Components to Build:**
1. **Global Layout:** A collapsible, sleek sidebar navigation (Navigation items: Overview, Evidence Ledger, Physics Runs, Tasks, Jobs). Include a top breadcrumb bar and a global "Run Sync" action button with a glowing pulse effect.
2. **Control Plane (Tasks & Jobs):** A complex, high-density data table or Kanban view for monitoring ingestion tasks and long-running physics jobs. Include status badges (Pending, Running, Anomaly, Success), progress bars, and expandable rows that reveal provenance details and task logs.
3. **Evidence Ledger Viewer:** A split-screen interface where the left panel lists scientific claims with confidence scores, and the right panel displays interactive data visualizations (using Recharts to mock up physics fits, residuals, and parameter contours).
4. **Dashboard Overview:** A bento-box grid layout summarizing active agents, current database sync status, recent anomalies, and a real-time activity feed.

**Design Constraints:**
- Use modern typography (Inter or Roboto).
- Ensure all components are accessible but visually striking. 
- Build reusable UI blocks that I can directly drop into my TanStack routes.
- Mock all data to look like real high-energy physics parameters (e.g., Tsallis fits, transverse momentum, Jüttner derivations).
- Prioritize visual excellence: use subtle gradients, hover states, and smooth transitions.

Please output the complete code for the layout and the main Overview and Task pages.
