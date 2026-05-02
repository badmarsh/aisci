# Onyx Configuration Prompt

Paste this entire document into a coding-agent session (Claude, Cursor, VS Code Copilot,
or any agent with shell and HTTP access to the server). The agent will read current Onyx
state and apply the desired state idempotently — safe to run repeatedly.

**Pre-requisites before running:**
- Onyx stack is up: `docker ps | grep onyx-api_server` returns a running container
- Both MCP proxy routes are reachable:
  ```bash
  curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8095/scite/
  curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8095/consensus/
  ```
  Scite may return `400` without a valid MCP request body; Consensus may return `401` or `411` without OAuth/body headers. Those statuses still prove the proxy route is alive.
- `.env` contains `ONYX_API_KEY`; MCP bearer tokens are supplied by the OAuth-capable client or by ignored local env when a custom Onyx tool needs a static bearer header.

---

## The Prompt

```
You are configuring the Onyx instance for the AiSci physics research pipeline.
Work through the steps below in order. Use `curl` or Python `requests` for all
API calls. Read the AUTH block first — every subsequent API call uses those credentials.

═══════════════════════════════════════════════════════════
STEP 0 — AUTH & BASE URL
═══════════════════════════════════════════════════════════

Base URL: http://localhost:3000
Auth: read ONYX_API_KEY from the .env file at deployment/onyx/.env
Header for all admin calls: Authorization: Bearer <ONYX_API_KEY>

Verify connectivity:
  GET /api/me  → must return 200 and contain "is_admin": true

If you get 401 or 403, stop and report the auth error. Do not continue.

═══════════════════════════════════════════════════════════
STEP 1 — LLM PROVIDER
═══════════════════════════════════════════════════════════

Desired state: one LiteLLM provider configured as the default.

  GET /api/admin/llm/provider
  → parse the list. Look for a provider with model_name containing "litellm" or
    provider "litellm_proxy".

If NOT found, create it:
  POST /api/admin/llm/provider
  Body:
  {
    "name": "LiteLLM Proxy",
    "provider": "litellm_proxy",
    "api_key": "",
    "api_base": "http://litellm:4000",
    "default_model_name": "qwen-cloud-fast",
    "fast_default_model_name": "qwen-cloud-fast",
    "is_default_provider": true,
    "is_public": true
  }

If already found, PATCH it to ensure:
  - default_model_name = "qwen-cloud-fast"
  - is_default_provider = true
  - api_base = "http://litellm:4000"

Models available via LiteLLM (defined in deployment/onyx/litellm_config.yaml):
  - qwen-cloud-fast   → qwen3-omni-flash-2025-09-15 via Alibaba Cloud + gemma2:27b fallback
  - qwen2.5:32b       → local Ollama, large context, used for deep analysis

Record the provider ID for use in persona creation.

═══════════════════════════════════════════════════════════
STEP 2 — DOCUMENT SETS
═══════════════════════════════════════════════════════════

Desired document sets. For each, check if it exists (GET /api/admin/document-set),
then create if missing.

2a. "Robert Corpus"
  POST /api/admin/document-set
  Body:
  {
    "name": "Robert Corpus",
    "description": "Robert's manuscript, Tsallis baselines, and all papers listed in research/robert/evidence-ledger.md. Upload source: File connector. Tag: source:robert-corpus.",
    "cc_pair_ids": [],
    "is_public": true
  }
  Note: cc_pair IDs are attached after the File connector is configured. Leave empty
  for now — the connector upload flow links files to this set at upload time.

2b. "arXiv Auto — Quarantine"
  Body:
  {
    "name": "arXiv Auto — Quarantine",
    "description": "New arXiv papers ingested by the scheduled web connector. NOT directly visible to research personas. Triage via arxiv-intake persona before promoting to Robert Corpus.",
    "cc_pair_ids": [],
    "is_public": false
  }

2c. "Scite Citations"
  Body:
  {
    "name": "Scite Citations",
    "description": "Live citation snippets retrieved on-demand from Scite MCP. Not an indexed document set — this label is used in persona prompts to tag the evidence origin.",
    "cc_pair_ids": [],
    "is_public": true
  }

Record the IDs of each document set: ROBERT_CORPUS_ID, ARXIV_QUARANTINE_ID, SCITE_CITATIONS_ID.

═══════════════════════════════════════════════════════════
STEP 3 — MCP TOOLS
═══════════════════════════════════════════════════════════

Desired state: two MCP server tools registered in Onyx.

  GET /api/tool  → list existing tools. Look for tools named "Scite" and "Consensus".

For each tool below, create if not found:

3a. Scite MCP
  POST /api/tool
  Body:
  {
    "name": "Scite",
    "description": "Retrieves Smart Citation context — supporting, contrasting, and mentioning citations for a paper DOI. Returns exact quoted snippets with section labels (Intro/Methods/Results). Call with {\"doi\": \"10.xxxx/...\"}.",
    "in_code_only": false,
    "tool_type": "custom",
    "openai_function_definition": {
      "name": "scite_search",
      "description": "Search Scite for Smart Citations on a paper by DOI. Returns supporting, contrasting, and mentioning snippets.",
      "parameters": {
        "type": "object",
        "properties": {
          "doi": {
            "type": "string",
            "description": "The DOI of the paper to look up citations for, e.g. 10.1234/example"
          },
          "query": {
            "type": "string",
            "description": "Optional keyword query to filter citations by content"
          }
        },
        "required": ["doi"]
      }
    },
    "custom_headers": [
      {"key": "Authorization", "value": "Bearer {SCITE_MCP_BEARER_TOKEN}"}
    ],
    "endpoint": "http://127.0.0.1:8095/scite/",
    "method": "POST"
  }
  → replace {SCITE_MCP_BEARER_TOKEN} only if the Onyx custom tool, rather than an OAuth-aware MCP client, owns the bearer header.

3b. Consensus MCP
  POST /api/tool
  Body:
  {
    "name": "Consensus",
    "description": "Searches peer-reviewed literature and returns AI-synthesised consensus summaries. Best for claim-level questions: 'does the literature support X?'. Use for exploratory signal only — do not use Consensus output to directly amend evidence-ledger.md.",
    "in_code_only": false,
    "tool_type": "custom",
    "openai_function_definition": {
      "name": "consensus_search",
      "description": "Search Consensus for an evidence-based answer to a scientific claim or question. Returns a consensus summary with supporting paper references.",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "A scientific question or claim to search, e.g. 'Do Tsallis distributions describe LHC pT spectra?'"
          }
        },
        "required": ["query"]
      }
    },
    "custom_headers": [
      {"key": "Authorization", "value": "Bearer {CONSENSUS_MCP_BEARER_TOKEN}"}
    ],
    "endpoint": "http://127.0.0.1:8095/consensus/",
    "method": "POST"
  }
  → replace {CONSENSUS_MCP_BEARER_TOKEN} only if the Onyx custom tool, rather than an OAuth-aware MCP client, owns the bearer header.

Record tool IDs: SCITE_TOOL_ID, CONSENSUS_TOOL_ID.

Also check for the three HEP readonly tools. If they exist, record their IDs:
  HEP_ARXIV_TOOL_ID, HEP_INSPIRE_TOOL_ID, HEPDATA_TOOL_ID
These are registered by deployment/onyx/hep_readonly_tools.py. If missing, run:
  python deployment/onyx/hep_readonly_tools.py

═══════════════════════════════════════════════════════════
STEP 4 — PERSONAS
═══════════════════════════════════════════════════════════

Desired state: exactly four research personas. For each, check if a persona with
that name exists (GET /api/persona). If it exists, PATCH it. If not, POST to create.

Read the EXACT system prompt text for each persona from:
  docs/user-manual/onyx-setup-guide.md
(The prompts are in the triple-backtick blocks under each persona heading.)
Do NOT paraphrase or shorten them.

───────────────────────────────────────────────────────────
4a. physics-validator
───────────────────────────────────────────────────────────
  Name: "physics-validator"
  Description: "Retrieval-only corpus checker. Finds and quotes exact passages. Never reasons or derives — only retrieves and cites."
  System prompt: [copy verbatim from docs/user-manual/onyx-setup-guide.md §Persona 1]
  Document sets: [ROBERT_CORPUS_ID]
  Tools: []   ← no tools, retrieval only
  LLM override: null (uses default provider)
  Is public: true
  Display priority order: 1
  Opening questions:
    - "Does my formula reduce to Cooper-Frye at U=0? Quote the exact chunk."
    - "What does the corpus say about χ²/ndf methodology? Quote every relevant chunk."
    - "Find and quote the normalization derivation from the manuscript."
    - "Is the η-cut condition stated verbatim in the corpus? Show me the exact text."

───────────────────────────────────────────────────────────
4b. evidence-auditor
───────────────────────────────────────────────────────────
  Name: "evidence-auditor"
  Description: "Consistency checker. Audits a pasted list of ledger claims against the corpus and Scite citations. Returns CONFIRMED / WEAKENED / MISSING per claim."
  System prompt: [copy verbatim from docs/user-manual/onyx-setup-guide.md §Persona 2]
  Document sets: [ROBERT_CORPUS_ID, SCITE_CITATIONS_ID]
  Tools: [SCITE_TOOL_ID, CONSENSUS_TOOL_ID]
  LLM override: "qwen2.5:32b"   ← deep analysis, use the large local model
  Is public: true
  Display priority order: 2
  Opening questions:
    - "Paste your current evidence-ledger.md claim list — I will audit every claim."
    - "Which claims are currently MISSING from the corpus?"
    - "Check whether external papers support or contradict the η-integration step."
    - "Run a Consensus signal on: 'Does the Jüttner distribution describe heavy-ion pT spectra at LHC energies?'"

───────────────────────────────────────────────────────────
4c. referee-prep
───────────────────────────────────────────────────────────
  Name: "referee-prep"
  Description: "Drafts referee-report prose from pre-verified CONFIRMED ledger claims only. Blocks any unconfirmed claim with an explicit placeholder."
  System prompt: [copy verbatim from docs/user-manual/onyx-setup-guide.md §Persona 3]
  Document sets: [ROBERT_CORPUS_ID, SCITE_CITATIONS_ID]
  Tools: [SCITE_TOOL_ID, CONSENSUS_TOOL_ID]
  LLM override: null (default)
  Is public: true
  Display priority order: 3
  Opening questions:
    - "Paste your CONFIRMED claims and target section — I will draft the prose."
    - "Draft the Formalism section from the confirmed claims in the ledger."
    - "I need to respond to a referee concern about over-parameterization. Do I have confirmed claims to support a response?"
    - "Draft a one-paragraph abstract from confirmed claims only."

───────────────────────────────────────────────────────────
4d. arxiv-intake
───────────────────────────────────────────────────────────
  Name: "arxiv-intake"
  Description: "Triages newly uploaded arXiv papers. Reads the quarantine document set only. Outputs PROMOTE or DISCARD with proposed ledger amendments for Robert to approve."
  System prompt: [copy verbatim from docs/user-manual/onyx-setup-guide.md §Persona 4]
  Document sets: [ARXIV_QUARANTINE_ID]
  Tools: []   ← triage is corpus-only, no live queries
  LLM override: null (default)
  Is public: false   ← internal triage tool, not surfaced to Robert
  Display priority order: 4
  Opening questions:
    - "New paper uploaded: [paste title and DOI here]"
    - "Triage: arXiv:2501.12345 — does it affect any ledger claims?"
    - "Is there anything in the quarantine set that contradicts the η-integration claim?"

═══════════════════════════════════════════════════════════
STEP 5 — VERIFY
═══════════════════════════════════════════════════════════

For each of the four personas, confirm:
  GET /api/persona/{id}
  - name ✓
  - system_prompt length > 500 chars ✓ (short = was truncated or wrong)
  - document_sets contains expected IDs ✓
  - tools contains expected IDs ✓
  - llm_model_version_override is correct ✓
  - starter_messages contains 4 opening questions ✓

Also run a smoke test on physics-validator:
  POST /api/chat/send-message
  Body: { "persona_id": <physics-validator-id>, "message": "test" }
  → must return 200 (not 500 or tool-name error)

If any check fails, report exactly which field is wrong and what was set vs what
was expected. Do not guess — show the actual API response.

═══════════════════════════════════════════════════════════
STEP 6 — REPORT
═══════════════════════════════════════════════════════════

At the end, print a summary table:

| Step | Item | Status | ID |
|------|------|--------|----|
| 1 | LiteLLM provider | CREATED/UPDATED/OK | <id> |
| 2a | Robert Corpus docset | CREATED/OK | <id> |
| 2b | arXiv Quarantine docset | CREATED/OK | <id> |
| 2c | Scite Citations docset | CREATED/OK | <id> |
| 3a | Scite MCP tool | CREATED/OK | <id> |
| 3b | Consensus MCP tool | CREATED/OK | <id> |
| 3c | HEP tools | FOUND/MISSING | <ids> |
| 4a | physics-validator persona | CREATED/UPDATED/OK | <id> |
| 4b | evidence-auditor persona | CREATED/UPDATED/OK | <id> |
| 4c | referee-prep persona | CREATED/UPDATED/OK | <id> |
| 4d | arxiv-intake persona | CREATED/UPDATED/OK | <id> |
| 5 | Smoke test | PASS/FAIL | — |

Then write the final persona IDs to docs/ops/onyx-persona-ids.md in this format:

```
# Onyx Persona IDs
# Auto-generated by onyx-configure — do not edit manually
# Last updated: <date>

PHYSICS_VALIDATOR_ID=<id>
EVIDENCE_AUDITOR_ID=<id>
REFEREE_PREP_ID=<id>
ARXIV_INTAKE_ID=<id>

ROBERT_CORPUS_DOCSET_ID=<id>
ARXIV_QUARANTINE_DOCSET_ID=<id>
SCITE_CITATIONS_DOCSET_ID=<id>

SCITE_TOOL_ID=<id>
CONSENSUS_TOOL_ID=<id>
```

Commit this file: git add docs/ops/onyx-persona-ids.md && git commit -m "ops: record onyx persona and docset IDs after configure run"
```

---

## When to Re-Run This Prompt

- After any `docker compose down && docker compose up` that resets the Onyx database
- After adding a new persona to `onyx-setup-guide.md`
- After changing a system prompt (the PATCH path in Step 4 handles this idempotently)
- After rotating Scite or Consensus OAuth bearer tokens used by custom Onyx tools (Step 3 will update headers)
- If `docs/ops/onyx-persona-ids.md` is missing or stale

## What This Does NOT Configure

- File Upload connector cc_pairs — those are created via the Onyx UI at upload time
- arXiv web connector schedule — set in Onyx Admin → Connectors after the connector is added
- User accounts — managed separately via Onyx Auth settings
- The LiteLLM model list itself — that is in `deployment/onyx/litellm_config.yaml`,
  applied at container build/restart time, not via the Onyx API
