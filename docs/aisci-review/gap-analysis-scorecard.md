# AiSci Architecture Scorecard & Gap Analysis

Based on the comparative analysis against frontier systems (OpenAI/Gemini Deep Research, OpenHands, Cursor), this scorecard evaluates the `badmarsh/aisci` architecture and identifies critical capability gaps.

## Scorecard

| Capability | Score (0-5) | Justification |
| :--- | :---: | :--- |
| **Epistemic Rigor** | 5 | The `evidence-ledger.md` is world-class. It prevents silent hallucinations and enforces statistical checks before claims are promoted. |
| **Literature Integration** | 4 | Excellent use of MCPs (Onyx RAG, Scite, Consensus). Minor deductions for reliability/uptime of the Onyx integration. |
| **Statistical Analysis** | 5 | Deep integration with `iminuit`, profiling, and covariance matrices. Highly rigorous physics phenomenological analysis. |
| **Autonomous Hypothesis Generation** | 1 | Models (BGBW, Tsallis, etc.) are hardcoded in Python. The AI does not derive or propose novel mathematical forms autonomously. |
| **Autonomous Execution (Agency)** | 2 | Relies on a human to define the queue in `next-actions.md`. The orchestration layer (DeerFlow) is overly complex compared to modern sandboxed agents (like OpenHands). |
| **Dynamic Tool Creation** | 1 | Agents cannot easily write and compile new tools on the fly. They rely on pre-written Python scripts in `physics/src/`. |

---

## Gap Analysis (Missing-Capability Register)

### Gap 1: The "Static Sandbox" Problem
*   **Observation:** AiSci agents are restricted to running pre-built `fitting_pipeline.py` variants. If the data suggests a modification to the Tsallis model (e.g., introducing a flow velocity profile), the agent cannot autonomously write the new integration kernel, test it, and update the fit spec.
*   **Frontier Comparison:** OpenHands or Roo Code would simply write a new Python file, execute it, read the terminal traceback, fix the syntax error, and re-run it until the model converges.
*   **Remediation:** Provide agents with a persistent, sandboxed Jupyter kernel or execution environment where they can write, execute, and iterate on `sympy` derivations and `scipy` integrations in real-time, independent of the hardcoded `physics/src/` pipelines.

### Gap 2: Over-reliance on "DeerFlow"
*   **Observation:** The infrastructure is heavily burdened by the `DeerFlow` application, which seems to act as an unnecessary middleware for agent execution.
*   **Frontier Comparison:** Modern architectures rely on lightweight MCP proxies and direct LLM API connections, pushing complexity into the system prompt and local sandboxes rather than heavy web-app orchestrators.
*   **Remediation:** Execute the "DeerFlow de-vendoring" plan mentioned in `ACTION_PLAN.md`. Shift to a leaner runtime (like a simple CLI or directly invoking models via a standard SDK) that respects the `AGENTS.md` constitution without the web backend overhead.

### Gap 3: Missing Autonomous Exploration Loop
*   **Observation:** The research loop is broken into discrete, human-triggered steps (read queue -> run script -> update ledger). 
*   **Frontier Comparison:** OpenAI Deep Research handles scoping, searching, synthesizing, and writing in one continuous, autonomous loop, backtracking when a path fails.
*   **Remediation:** Upgrade the system prompt (`AGENTS.md` / `MEGAPROMPT_FIX_ALL.md`) to instruct the agent to autonomously append to `next-actions.md` based on anomalies found in `evidence-ledger.md`, creating a self-sustaining research loop.

## Conclusion for Phase 3
To bring AiSci to the frontier, we must preserve its 5/5 Epistemic Rigor (the ledger) while replacing its static execution model with the dynamic, code-writing autonomy seen in OpenHands. Phase 3 (The Roadmap) will outline exactly how to rewrite the constitution and backlog to achieve this.
