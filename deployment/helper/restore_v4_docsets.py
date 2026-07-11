from __future__ import annotations
"""
restore_v4_docsets.py  (v2 — uses exact DB values from inspect run 2026-06-04)
==============================================================================
State coming in:
  connector 14  Manuscript-File-Connector  FILE  — exists, no CC pair yet
  CC pair  4    connector 3 / credential 1 — Literature PDFs (Khuntia + Rath)
  DS  7         HEP Phenomenology References — linked to CC pair 4  ✅
  DS missing    Robert Boson Draft
  persona 2     physics-validator — currently 0 doc sets attached

What this script does:
  1. Create CC pair for connector 14 (using credential 1, same as literature)
  2. Upload manuscript PDF to connector 14 → triggers indexing
  3. Create "Robert Boson Draft" doc set → link to new CC pair
  4. Patch physics-validator (id=2) → add DS 7 + new Robert Boson Draft DS
  5. Rewrite docs/ops/onyx-persona-ids.md (resolves merge conflict)

Run from repo root:
    python3 deployment/helper/restore_v4_docsets.py
"""

import os
import sys
import json
import subprocess
import requests

# ── Hard constants from DB inspection ────────────────────────────────────────
BASE_URL              = "http://localhost:3000"
REPO_ROOT             = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", ".."))

MANUSCRIPT_PDF        = os.path.join(
    REPO_ROOT, "research", "robert", "manuscript",
    "boson-probability-function-moving-system.pdf")

MANUSCRIPT_CONNECTOR_ID = 14   # created in previous run, no CC pair yet
LITERATURE_CC_PAIR_ID   = 4    # connector 3 / Literature PDFs Pair
LITERATURE_CREDENTIAL_ID = 1   # "PDF" credential used by literature connector
HEP_DOC_SET_ID          = 7    # already created ✅
PHYSICS_VALIDATOR_ID    = 2    # persona to patch

# ── Auth ──────────────────────────────────────────────────────────────────────

def load_api_key() -> str:
    key = os.environ.get("ONYX_API_KEY", "").strip()
    if key:
        return key
    env_path = os.path.join(REPO_ROOT, "deployment", "onyx", ".env")
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("ONYX_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"\'')
    raise SystemExit("ONYX_API_KEY not found")

API_KEY      = load_api_key()
AUTH_HEADERS = {"Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"}

def check_auth():
    r = requests.get(f"{BASE_URL}/api/me", headers=AUTH_HEADERS)
    if r.status_code != 200 or r.json().get("role") != "admin":
        raise SystemExit(f"Auth failed: {r.status_code} {r.text}")
    print("  Auth OK — admin confirmed")

# ── DB helpers ────────────────────────────────────────────────────────────────

def run_sql(query: str) -> str:
    out = subprocess.check_output(
        ["docker", "exec", "-i", "onyx-db", "psql",
         "-U", "postgres", "-d", "postgres", "-c", query],
        stderr=subprocess.STDOUT,
    )
    return out.decode("utf-8")

def cc_pair_exists_for_connector(connector_id: int) -> int | None:
    """Return CC pair ID if one exists for connector_id, else None."""
    rows = run_sql(
        f"SELECT id FROM connector_credential_pair "
        f"WHERE connector_id = {connector_id};"
    )
    for line in rows.splitlines():
        line = line.strip()
        if line.isdigit():
            return int(line)
    return None

# ── Step 1: create CC pair for manuscript connector ───────────────────────────

def create_manuscript_cc_pair() -> int:
    existing = cc_pair_exists_for_connector(MANUSCRIPT_CONNECTOR_ID)
    if existing:
        print(f"  CC pair for connector {MANUSCRIPT_CONNECTOR_ID} already exists — ID {existing}")
        return existing

    print(f"  Linking connector {MANUSCRIPT_CONNECTOR_ID} to credential {LITERATURE_CREDENTIAL_ID}...")
    r = requests.put(
        f"{BASE_URL}/api/manage/connector/{MANUSCRIPT_CONNECTOR_ID}"
        f"/credential/{LITERATURE_CREDENTIAL_ID}",
        headers=AUTH_HEADERS,
        json={"name": "Manuscript CC Pair", "is_public": False},
    )
    if r.status_code not in (200, 201, 204):
        # Fall back: try credential 0
        print(f"  API returned {r.status_code}, trying credential 0...")
        r = requests.put(
            f"{BASE_URL}/api/manage/connector/{MANUSCRIPT_CONNECTOR_ID}/credential/0",
            headers=AUTH_HEADERS,
            json={"name": "Manuscript CC Pair", "is_public": False},
        )
    if r.status_code not in (200, 201, 204):
        # Last resort: insert directly into DB
        print(f"  API still failing ({r.status_code}), inserting CC pair via SQL...")
        run_sql(
            f"INSERT INTO connector_credential_pair "
            f"(connector_id, credential_id, name, status, access_type, total_docs_indexed) "
            f"VALUES ({MANUSCRIPT_CONNECTOR_ID}, {LITERATURE_CREDENTIAL_ID}, "
            f"'Manuscript CC Pair', 'not_started', 'private', 0) "
            f"ON CONFLICT DO NOTHING;"
        )

    cc_id = cc_pair_exists_for_connector(MANUSCRIPT_CONNECTOR_ID)
    if not cc_id:
        raise SystemExit("Could not create CC pair for manuscript connector")
    print(f"  Manuscript CC pair ID: {cc_id}")
    return cc_id

# ── Step 2: upload manuscript PDF ─────────────────────────────────────────────

def upload_manuscript(connector_id: int):
    if not os.path.exists(MANUSCRIPT_PDF):
        raise SystemExit(f"Manuscript PDF not found: {MANUSCRIPT_PDF}")
    pdf_name = os.path.basename(MANUSCRIPT_PDF)
    size_kb = os.path.getsize(MANUSCRIPT_PDF) // 1024
    print(f"  Uploading {pdf_name} ({size_kb} KB) to connector {connector_id}...")
    with open(MANUSCRIPT_PDF, "rb") as fh:
        r = requests.post(
            f"{BASE_URL}/api/manage/admin/connector/{connector_id}/files/update",
            headers={"Authorization": f"Bearer {API_KEY}"},
            files=[("files", (pdf_name, fh, "application/pdf"))],
            data={"file_ids_to_remove": "[]"},
        )
    if r.status_code not in (200, 201):
        raise SystemExit(f"Upload failed: {r.status_code} {r.text}")
    print(f"  Upload OK → indexing triggered")
    print(f"  Response: {json.dumps(r.json(), indent=2)}")

# ── Step 3: create Robert Boson Draft doc set ─────────────────────────────────

def get_existing_doc_sets() -> dict:
    r = requests.get(f"{BASE_URL}/api/manage/document-set", headers=AUTH_HEADERS)
    r.raise_for_status()
    return {ds["name"]: ds["id"] for ds in r.json()}

def create_doc_set(name: str, description: str, cc_pair_ids: list,
                   is_public: bool) -> int:
    existing = get_existing_doc_sets()
    if name in existing:
        print(f"  Doc set '{name}' already exists — ID {existing[name]}")
        return existing[name]
    payload = {
        "name": name,
        "description": description,
        "cc_pair_ids": cc_pair_ids,
        "is_public": is_public,
        "is_up_to_date": True,
    }
    r = requests.post(
        f"{BASE_URL}/api/manage/admin/document-set",
        headers=AUTH_HEADERS, json=payload)
    if r.status_code not in (200, 201):
        raise SystemExit(f"Failed to create doc set '{name}': {r.status_code} {r.text}")
    resp = r.json()
    ds_id = resp.get("id") if isinstance(resp, dict) else int(resp)
    print(f"  Created doc set '{name}' — ID {ds_id}")
    return ds_id

# ── Step 4: patch physics-validator ──────────────────────────────────────────

def get_persona(persona_id: int) -> dict:
    r = requests.get(f"{BASE_URL}/api/persona/{persona_id}", headers=AUTH_HEADERS)
    r.raise_for_status()
    return r.json()

def patch_persona_doc_sets(persona_id: int, doc_set_ids: list[int]):
    persona = get_persona(persona_id)
    current_ds = [ds["id"] for ds in persona.get("document_sets", [])]
    merged = sorted(set(current_ds) | set(doc_set_ids))
    print(f"  Current doc sets on persona {persona_id}: {current_ds}")
    print(f"  Will set to: {merged}")

    payload = {
        "name":                      persona["name"],
        "description":               persona.get("description", ""),
        "system_prompt":             persona.get("system_prompt", ""),
        "task_prompt":               persona.get("task_prompt", ""),
        "document_set_ids":          merged,
        "tool_ids":                  [t["id"] for t in persona.get("tools", [])],
        "is_public":                 persona.get("is_public", True),
        "display_priority":          persona.get("display_priority"),
        "num_chunks":                persona.get("num_chunks", 10),
        "llm_model_version_override": persona.get("llm_model_version_override"),
        "llm_relevance_filter":      persona.get("llm_relevance_filter", False),
        "datetime_aware":            persona.get("datetime_aware", False),
        "starter_messages":          persona.get("starter_messages", []),
    }
    r = requests.patch(
        f"{BASE_URL}/api/persona/{persona_id}",
        headers=AUTH_HEADERS, json=payload)
    if r.status_code != 200:
        raise SystemExit(f"PATCH persona {persona_id} failed: {r.status_code} {r.text}")
    updated = sorted(ds["id"] for ds in r.json().get("document_sets", []))
    print(f"  Persona {persona_id} doc sets confirmed: {updated}")

# ── Step 5: rewrite onyx-persona-ids.md ──────────────────────────────────────

def write_persona_ids_file(rbd_ds_id: int, manuscript_cc_pair_id: int):
    out_path = os.path.join(REPO_ROOT, "docs", "ops", "onyx-persona-ids.md")

    # Fetch live persona IDs
    r = requests.get(f"{BASE_URL}/api/persona", headers=AUTH_HEADERS)
    r.raise_for_status()
    personas = {p["name"]: p["id"] for p in r.json()}

    phys_id = personas.get("physics-validator", 2)
    ea_id   = personas.get("evidence-auditor", 5)
    rp_id   = personas.get("referee-prep", 6)
    ai_id   = personas.get("arxiv-intake", 3)
    sr_id   = personas.get("Scientific Researcher", 1)

    content = f"""\
# Onyx Persona IDs

> **Authoritative** persona/doc-set map.  
> Last updated: 2026-06-04 by `restore_v4_docsets.py`.  
> Re-run after any persona import, Onyx upgrade, or `POST /api/persona` change.

---

## Active Personas

| ID | Name | Public | Doc Sets | Notes |
|----|------|--------|----------|-------|
| {phys_id} | **physics-validator** | ✅ Yes | Robert Corpus · HEP Phenomenology References · Robert Boson Draft | Restored 2026-06-04 |
| {ea_id} | **evidence-auditor** | ❌ No | Robert Corpus · Scite Citations | |
| {rp_id} | **referee-prep** | ❌ No | Robert Corpus · Scite Citations | |
| {ai_id} | **arxiv-intake** | ❌ No | arXiv Auto — Quarantine | |
| {sr_id} | **Scientific Researcher** | ❌ No | Chemistry | Has Scite + Consensus MCP |
| 0 | **Assistant** | ✅ Yes | none | |

> ⚠️ **physics-validator** does NOT have Scite/Consensus MCP.  
> Use **Scientific Researcher** (id={sr_id}) for external MCP literature queries.

---

## Active Document Sets

| DS ID | Name | Public | CC Pair | Contents |
|-------|------|--------|---------|----------|
| 2 | **Robert Corpus** | ❌ Private | CC pair 6 + 1 | Baseline literature + Ingestion API |
| {HEP_DOC_SET_ID} | **HEP Phenomenology References** | ❌ Private | CC pair {LITERATURE_CC_PAIR_ID} | Khuntia 2019 · Rath 2020 |
| {rbd_ds_id} | **Robert Boson Draft** | ❌ Private | CC pair {manuscript_cc_pair_id} | Pre-publication manuscript PDF |
| 3 | **arXiv Auto — Quarantine** | ❌ Private | CC pair 1 | arxiv-intake triage queue |
| 4 | **Scite Citations** | ✅ Public | CC pair 1 | Live citation snippets label |

---

## physics-validator Guardrails (id={phys_id})

**Has:** Robert Corpus (DS 2) · HEP Phenomenology References (DS {HEP_DOC_SET_ID}) · Robert Boson Draft (DS {rbd_ds_id})  
**Tools:** `internal_search`, `read_file`  
**Model:** `qwen-omni-flash`  
**Must NOT have:** Scite/Consensus MCP → route those to Scientific Researcher (id={sr_id})

---

## Connector / Credential Map

| Connector ID | Name | CC Pair ID | Credential ID |
|---|---|---|---|
| 0 | Ingestion API | 1 | 0 (DefaultCCPair) |
| 3 | Literature PDFs | 4 | 1 (PDF) |
| 4 | AiSci-System-Docs | 6 | 0 |
| 14 | Manuscript-File-Connector | {manuscript_cc_pair_id} | {LITERATURE_CREDENTIAL_ID} |

---

## Verification

```bash
python3 deployment/helper/inspect_connectors.py
python3 deployment/helper/run_rag_tests.py --persona-id {phys_id} --label post-v4-restore
```
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Wrote clean onyx-persona-ids.md → {out_path}")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("STEP 0 — Auth")
    check_auth()

    print("\nSTEP 1 — Create CC pair for manuscript connector")
    manuscript_cc_pair_id = create_manuscript_cc_pair()

    print("\nSTEP 2 — Upload manuscript PDF")
    upload_manuscript(MANUSCRIPT_CONNECTOR_ID)

    print("\nSTEP 3 — Create 'Robert Boson Draft' doc set")
    rbd_ds_id = create_doc_set(
        name="Robert Boson Draft",
        description=(
            "Pre-publication manuscript: 'Boson probability function for the moving system'. "
            "Private. Source: research/robert/manuscript/. "
            "Treat as the SUBJECT OF VALIDATION, not ground truth."
        ),
        cc_pair_ids=[manuscript_cc_pair_id],
        is_public=False,
    )

    print(f"\nSTEP 4 — Patch physics-validator (id={PHYSICS_VALIDATOR_ID})")
    patch_persona_doc_sets(PHYSICS_VALIDATOR_ID, [HEP_DOC_SET_ID, rbd_ds_id])

    print("\nSTEP 5 — Rewrite onyx-persona-ids.md")
    write_persona_ids_file(rbd_ds_id, manuscript_cc_pair_id)

    print("\n" + "=" * 60)
    print("DONE")
    print(f"  HEP Phenomenology References  DS {HEP_DOC_SET_ID}  (CC pair {LITERATURE_CC_PAIR_ID}) — already existed")
    print(f"  Robert Boson Draft            DS {rbd_ds_id}  (CC pair {manuscript_cc_pair_id})")
    print()
    print("Next steps:")
    print("  1. Wait 2–5 min for manuscript indexing to complete")
    print("  2. python3 deployment/helper/run_rag_tests.py --persona-id 2 --label post-v4-restore")
    print("  3. git add docs/ops/onyx-persona-ids.md && git commit -m 'ops: restore v4 doc sets, resolve merge conflict'")

if __name__ == "__main__":
    main()
