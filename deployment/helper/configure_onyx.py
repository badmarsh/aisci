import os
import requests
import json
import sys

BASE_URL = "http://localhost:3000"

# Load API key from env file
env_path = "deployment/onyx/.env"
api_key = None
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            if line.startswith("ONYX_API_KEY="):
                api_key = line.strip().split("=", 1)[1].strip('"\'')
                break

if not api_key:
    print("Could not find ONYX_API_KEY in .env")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

print("STEP 0 - Verifying connectivity")
resp = requests.get(f"{BASE_URL}/api/me", headers=HEADERS)
if resp.status_code != 200 or resp.json().get("role") != "admin":
    print(f"Auth failed. Status: {resp.status_code}, Response: {resp.text}")
    sys.exit(1)
print("Auth OK")

# We resolve tools dynamically based on DB to be extremely robust
try:
    import subprocess
    db_tools_out = subprocess.check_output([
        "docker", "exec", "-i", "onyx-db", "psql", "-U", "postgres", "-d", "postgres", "-c", 
        "SELECT id, name FROM tool;"
    ]).decode('utf-8')
    db_tools = {}
    for line in db_tools_out.splitlines():
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 2 and parts[0].isdigit():
            db_tools[parts[1]] = int(parts[0])
    
    internal_search_id = db_tools.get("internal_search", 1)
    read_file_id = db_tools.get("read_file", 9)
    scite_tool_id = db_tools.get("search_literature", 14)
    consensus_tool_id = db_tools.get("search", 13)
    print(f"Dynamically resolved tool IDs from DB:")
    print(f"  internal_search: {internal_search_id}")
    print(f"  read_file: {read_file_id}")
    print(f"  scite (search_literature): {scite_tool_id}")
    print(f"  consensus (search): {consensus_tool_id}")
except Exception as e:
    print(f"Warning: Failed to dynamically resolve tool IDs: {e}. Falling back to default mappings.")
    internal_search_id = 1
    read_file_id = 9
    scite_tool_id = 14
    consensus_tool_id = 13

print("\nSTEP 2 - Document Sets")
resp = requests.get(f"{BASE_URL}/api/manage/document-set", headers=HEADERS)
doc_sets = resp.json()

doc_set_configs = [
    {
        "name": "Robert Corpus",
        "description": "Robert's manuscript, Tsallis baselines, and all papers listed in research/robert/evidence-ledger.md. Upload source: File connector. Tag: source:robert-corpus.",
        "cc_pair_ids": [2],
        "is_public": True,
        "is_up_to_date": True
    },
    {
        "name": "arXiv Auto \u2014 Quarantine",
        "description": "New arXiv papers ingested by the scheduled web connector. NOT directly visible to research personas. Triage via arxiv-intake persona before promoting to Robert Corpus.",
        "cc_pair_ids": [2],
        "is_public": False,
        "is_up_to_date": True
    },
    {
        "name": "Scite Citations",
        "description": "Live citation snippets retrieved on-demand from Scite MCP. Not an indexed document set \u2014 this label is used in persona prompts to tag the evidence origin.",
        "cc_pair_ids": [2],
        "is_public": True,
        "is_up_to_date": True
    }
]

doc_set_ids = {}

for ds_conf in doc_set_configs:
    existing = next((ds for ds in doc_sets if ds["name"] == ds_conf["name"]), None)
    if existing:
        print(f"Document set {ds_conf['name']} already exists with ID {existing['id']}")
        doc_set_ids[ds_conf["name"]] = existing["id"]
    else:
        print(f"Creating document set {ds_conf['name']}...")
        create_resp = requests.post(f"{BASE_URL}/api/manage/admin/document-set", headers=HEADERS, json=ds_conf)
        if create_resp.status_code in [200, 201]:
            resp_data = create_resp.json()
            if isinstance(resp_data, dict):
                ds_id = resp_data.get("id")
            else:
                ds_id = resp_data
            doc_set_ids[ds_conf["name"]] = ds_id
            print(f"Created with ID {ds_id}")
        else:
            print(f"Failed to create document set: {create_resp.text}")

print("\nSTEP 4 - Personas")

prompts = {
    "physics-validator": """You are physics-validator, a retrieval-only assistant for the AiSci physics research
pipeline.

YOUR ONLY JOB is to find and quote exact passages from the indexed document corpus.
You do not reason, derive, explain, or generate. You retrieve and quote.

RULES — follow every rule on every response, no exceptions:

1. Every claim you make must be backed by a direct quote from a retrieved chunk.
   Format: > "[exact quote]" — [document title], [section/page if available]

2. If the corpus contains no chunk relevant to the query, respond with exactly:
   NOT FOUND IN CORPUS — no relevant chunk retrieved for this query.
   Do not attempt to answer from training knowledge.

3. If a query asks you to confirm a mathematical formula, quote the chunk that
   contains it. Do not rewrite or simplify the formula. Quote it exactly as it
   appears in the document, including any notation differences from the query.

4. Append this warning to EVERY response until explicitly told the issue is resolved:
   ⚠ χ²/ndf STATUS: No chunk confirming goodness-of-fit methodology has been
   retrieved from the indexed corpus. This is a standing open concern in the
   evidence ledger.

5. Never write "based on my knowledge" or "typically in physics" or any phrase
   that draws on training data rather than retrieved chunks.

6. Never propose amendments to the evidence ledger. Your output is read-only
   evidence. science-ledger-manager handles all ledger writes.""",

    "evidence-auditor": """You are evidence-auditor, a consistency-checking assistant for the AiSci physics
research pipeline.

YOUR ONLY JOB is to compare a provided list of ledger claims against the indexed
corpus and report the status of each claim as CONFIRMED, WEAKENED, or MISSING.

INPUT FORMAT — the user will paste a list of claims from evidence-ledger.md.
Each claim is a single sentence or equation statement.

OUTPUT FORMAT — for each claim, respond with exactly this structure:

CLAIM: [paste the claim verbatim]
STATUS: CONFIRMED | WEAKENED | MISSING
EVIDENCE: > "[exact chunk quote]" — [document, section/page]
NOTE: [one sentence only, explaining any qualification — omit if STATUS is CONFIRMED
      with no caveats]

RULES:

1. CONFIRMED means a retrieved chunk directly supports the claim with no
   material difference in formulation.

2. WEAKENED means a retrieved chunk addresses the same topic but introduces
   a qualification, alternative formulation, or scope limitation not present
   in the claim as written.

3. MISSING means no relevant chunk was retrieved. Do not speculate about
   whether the claim is true. State MISSING and stop.

4. Do not merge, reorder, or rewrite claims. Process them in the order given.

5. Do not add new claims. Do not suggest what claims should say. Audit only.

6. If Scite citation data is available, append after the EVIDENCE line:
   CITATION SIGNAL: [supporting/contrasting/mentioning] — "[scite snippet]"

7. Append to the final line of your entire response:
   AUDIT COMPLETE — [N] claims checked: [x] CONFIRMED, [y] WEAKENED, [z] MISSING""",

    "referee-prep": """You are referee-prep, a drafting assistant for the AiSci physics research pipeline.

YOUR ONLY JOB is to assemble claims that are already CONFIRMED in the evidence
ledger into draft referee-report prose. You do not verify claims — that is
evidence-auditor's job. You write only what has already been verified.

BEFORE WRITING ANYTHING, the user must provide:
- A list of CONFIRMED ledger claims (copy from evidence-ledger.md)
- The target section (Abstract / Formalism / Numerical Results / Comparison /
  Conclusion)

OUTPUT RULES:

1. Write in standard physics paper register — third person, past tense for
   experimental results, present tense for theoretical claims.

2. Every sentence in your draft must trace to at least one CONFIRMED claim
   from the provided list. If you cannot trace it, do not write it.

3. If a claim would require bridging logic not present in the confirmed list,
   insert: [BRIDGE NEEDED — add supporting claim to ledger before completing
   this sentence]

4. If the user asks you to include a claim that is not in the provided
   CONFIRMED list, respond:
   BLOCKED — "[claim]" is not in the provided confirmed claims list.
   Run evidence-auditor first, then add to ledger before drafting.

5. Do not invent citations. If a citation is needed, insert:
   [CITE NEEDED — query physics-validator for the relevant passage]

6. χ²/ndf caveat: if drafting any section that discusses fit quality, insert:
   [χ²/ndf UNRESOLVED — this sentence cannot be completed until goodness-of-fit
   methodology is confirmed in corpus]""",

    "arxiv-intake": """You are arxiv-intake, a triage assistant for the AiSci physics research pipeline.

YOUR ONLY JOB is to read a newly uploaded paper and determine whether it has
material relevance to Robert's current research claims. You produce a structured
triage report. You do not update the ledger — you propose amendments that Robert
must approve.

INPUT: the user provides the title and DOI of the newly uploaded paper.

OUTPUT FORMAT — always this exact structure, no additions:

PAPER: [title] ([DOI])
RELEVANCE: HIGH | MEDIUM | LOW | NONE
SUMMARY: [2–3 sentences maximum, describing only what the paper does — not
          whether it is correct]

LEDGER IMPACT:
  [For each affected ledger claim, one entry:]
  - CLAIM: [paste claim verbatim from ledger]
    SIGNAL: SUPPORTS | CONTRADICTS | EXTENDS | UNRELATED
    EVIDENCE: > "[exact quote from paper chunk]" — [section/page]

PROPOSED ACTION:
  PROMOTE to robert-corpus and add the following ledger amendment:
    [paste proposed amendment in ledger format]
  OR
  DISCARD — paper has no material ledger impact. Do not promote to robert-corpus.

RULES:

1. If RELEVANCE is NONE or LOW, the LEDGER IMPACT section must be empty and
   PROPOSED ACTION must be DISCARD.

2. Never promote a paper to robert-corpus yourself. Write the PROPOSED ACTION
   and wait for Robert to confirm.

3. Never generate a ledger amendment that introduces a new scientific claim
   not directly supported by a retrieved chunk from this paper.

4. Do not compare this paper to other papers in the corpus. Triage this paper
   in isolation against the ledger claims only."""
}

persona_configs = {
    "physics-validator": {
        "description": "Retrieval-only corpus checker. Finds and quotes exact passages. Never reasons or derives \u2014 only retrieves and cites.",
        "system_prompt": prompts["physics-validator"],
        "document_set_ids": [doc_set_ids.get("Robert Corpus")],
        "tool_ids": [internal_search_id],
        "num_chunks": 10,
        "llm_model_version_override": None,
        "is_public": True,
        "display_priority": 1,
        "starter_messages": [
            {"name": "Does my formula reduce to Cooper-Frye at U=0? Quote the exact chunk.", "description": "", "message": "Does my formula reduce to Cooper-Frye at U=0? Quote the exact chunk."},
            {"name": "What does the corpus say about \u03c7\u00b2/ndf methodology?", "description": "", "message": "What does the corpus say about \u03c7\u00b2/ndf methodology? Quote every relevant chunk."},
            {"name": "Find and quote the normalization derivation from the manuscript.", "description": "", "message": "Find and quote the normalization derivation from the manuscript."},
            {"name": "Is the \u03b7-cut condition stated verbatim in the corpus?", "description": "", "message": "Is the \u03b7-cut condition stated verbatim in the corpus? Show me the exact text."}
        ]
    },
    "evidence-auditor": {
        "description": "Consistency checker. Audits a pasted list of ledger claims against the corpus and Scite citations. Returns CONFIRMED / WEAKENED / MISSING per claim.",
        "system_prompt": prompts["evidence-auditor"],
        "document_set_ids": [ds_id for ds_id in [doc_set_ids.get("Robert Corpus"), doc_set_ids.get("Scite Citations")] if ds_id is not None],
        "tool_ids": [internal_search_id, scite_tool_id, consensus_tool_id],
        "num_chunks": 10,
        "llm_model_version_override": "qwen2.5:32b",
        "is_public": True,
        "display_priority": 2,
        "starter_messages": [
            {"name": "Paste your current evidence-ledger.md claim list \u2014 I will audit every claim.", "description": "", "message": "Paste your current evidence-ledger.md claim list \u2014 I will audit every claim."},
            {"name": "Which claims are currently MISSING from the corpus?", "description": "", "message": "Which claims are currently MISSING from the corpus?"},
            {"name": "Check whether external papers support or contradict the \u03b7-integration step.", "description": "", "message": "Check whether external papers support or contradict the \u03b7-integration step."},
            {"name": "Run a Consensus signal on the J\u00fcttner distribution describing heavy-ion pT spectra.", "description": "", "message": "Run a Consensus signal on: 'Does the J\u00fcttner distribution describe heavy-ion pT spectra at LHC energies?'"}
        ]
    },
    "referee-prep": {
        "description": "Drafts referee-report prose from pre-verified CONFIRMED ledger claims only. Blocks any unconfirmed claim with an explicit placeholder.",
        "system_prompt": prompts["referee-prep"],
        "document_set_ids": [ds_id for ds_id in [doc_set_ids.get("Robert Corpus"), doc_set_ids.get("Scite Citations")] if ds_id is not None],
        "tool_ids": [tid for tid in [internal_search_id, scite_tool_id, consensus_tool_id] if tid is not None],
        "num_chunks": 5,
        "llm_model_version_override": None,
        "is_public": True,
        "display_priority": 3,
        "starter_messages": [
            {"name": "Paste your CONFIRMED claims and target section \u2014 I will draft the prose.", "description": "", "message": "Paste your CONFIRMED claims and target section \u2014 I will draft the prose."},
            {"name": "Draft the Formalism section from the confirmed claims in the ledger.", "description": "", "message": "Draft the Formalism section from the confirmed claims in the ledger."},
            {"name": "Do I have confirmed claims to support a response regarding over-parameterization?", "description": "", "message": "I need to respond to a referee concern about over-parameterization. Do I have confirmed claims to support a response?"},
            {"name": "Draft a one-paragraph abstract from confirmed claims only.", "description": "", "message": "Draft a one-paragraph abstract from confirmed claims only."}
        ]
    },
    "arxiv-intake": {
        "description": "Triages newly uploaded arXiv papers. Reads the quarantine document set only. Outputs PROMOTE or DISCARD with proposed ledger amendments for Robert to approve.",
        "system_prompt": prompts["arxiv-intake"],
        "document_set_ids": [doc_set_ids.get("arXiv Auto \u2014 Quarantine")] if doc_set_ids.get("arXiv Auto \u2014 Quarantine") else [],
        "tool_ids": [],
        "num_chunks": 10,
        "llm_model_version_override": None,
        "is_public": False,
        "display_priority": 4,
        "starter_messages": [
            {"name": "New paper uploaded: [paste title and DOI here]", "description": "", "message": "New paper uploaded: [paste title and DOI here]"},
            {"name": "Triage: arXiv:2501.12345 \u2014 does it affect any ledger claims?", "description": "", "message": "Triage: arXiv:2501.12345 \u2014 does it affect any ledger claims?"},
            {"name": "Is there anything in the quarantine set that contradicts the \u03b7-integration claim?", "description": "", "message": "Is there anything in the quarantine set that contradicts the \u03b7-integration claim?"},
            {"name": "Triage newest quarantine paper.", "description": "", "message": "Triage newest quarantine paper."}
        ]
    }
}

resp = requests.get(f"{BASE_URL}/api/persona", headers=HEADERS)
existing_personas = resp.json()

persona_ids = {}

for name, config in persona_configs.items():
    existing = next((p for p in existing_personas if p["name"] == name), None)
    
    payload = {
        "name": name,
        "description": config["description"],
        "system_prompt": config["system_prompt"],
        "task_prompt": "",
        "document_set_ids": config["document_set_ids"],
        "tool_ids": config["tool_ids"],
        "llm_model_version_override": config["llm_model_version_override"],
        "is_public": config["is_public"],
        "display_priority": config["display_priority"],
        "starter_messages": config["starter_messages"],
        "num_chunks": config["num_chunks"],
        "llm_relevance_filter": False,
        "datetime_aware": False
    }

    if existing:
        print(f"Updating persona {name} (ID: {existing['id']})...")
        p_resp = requests.patch(f"{BASE_URL}/api/persona/{existing['id']}", headers=HEADERS, json=payload)
        if p_resp.status_code == 200:
            persona_ids[name] = p_resp.json().get("id")
            print("OK")
        else:
            print(f"Failed to update persona: {p_resp.text}")
    else:
        print(f"Creating persona {name}...")
        p_resp = requests.post(f"{BASE_URL}/api/persona", headers=HEADERS, json=payload)
        if p_resp.status_code in [200, 201]:
            persona_ids[name] = p_resp.json().get("id")
            print("OK")
        else:
            print(f"Failed to create persona: {p_resp.text}")

print("\nSTEP 5 - Verify & Smoke Test")
if "physics-validator" in persona_ids:
    pv_id = persona_ids["physics-validator"]
    print(f"Running smoke test on physics-validator ({pv_id})...")
    smoke_payload = {
        "persona_id": pv_id,
        "message": "test",
        "new_session_is_public": False,
        "alternate_assistant_id": None,
        "prompt_id": None
    }
    # Create new session
    sess_resp = requests.post(f"{BASE_URL}/api/chat/create-chat-session", headers=HEADERS, json={"persona_id": pv_id, "description": "Smoke test"})
    if sess_resp.status_code == 200:
        session_id = sess_resp.json().get("chat_session_id")
        msg_payload = {
            "chat_session_id": session_id,
            "message": "test",
            "parent_message_id": None,
            "file_descriptors": [],
            "prompt_id": None,
            "search_doc_ids": [],
            "query_override": None
        }
        msg_resp = requests.post(f"{BASE_URL}/api/chat/send-message", headers=HEADERS, json=msg_payload)
        if msg_resp.status_code == 200:
            print("Smoke test: PASS")
        else:
            print(f"Smoke test: FAIL (Status {msg_resp.status_code}, {msg_resp.text})")
    else:
        print(f"Smoke test session creation failed: {sess_resp.status_code} {sess_resp.text}")

print("\nSTEP 6 - Report")
with open("docs/ops/onyx-persona-ids.md", "w") as f:
    f.write("# Onyx Persona IDs\n\n")
    f.write(f"- physics-validator: {persona_ids.get('physics-validator')}\n")
    f.write(f"- evidence-auditor: {persona_ids.get('evidence-auditor')}\n")
    f.write(f"- referee-prep: {persona_ids.get('referee-prep')}\n")
    f.write(f"- arxiv-intake: {persona_ids.get('arxiv-intake')}\n\n")
    
    f.write("## Doc Sets\n")
    f.write(f"- Robert Corpus: {doc_set_ids.get('Robert Corpus')}\n")
    f.write(f"- arXiv Auto — Quarantine: {doc_set_ids.get('arXiv Auto — Quarantine')}\n")
    f.write(f"- Scite Citations: {doc_set_ids.get('Scite Citations')}\n")

print("Done. Saved IDs to docs/ops/onyx-persona-ids.md.")
