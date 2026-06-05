#!/usr/bin/env python3
"""
Fix script:
1. Delete index_attempt rows for bad cc_pairs (blocks connector deletion)
2. Delete bad FileConnectors via API (purges Vespa docs)
3. Sync document-set connector associations via API (DS2→cc1+cc4, DS3→cc1)
4. Smoke-test physics-validator with correct endpoint
"""
import subprocess
import requests
import json

BASE_URL = "http://localhost:3000"
API_KEY = (
    "on_hLxHEO432IFLuDN3psKyxgLH3g35yvvZqOx21yP1Iw__GrPullG5YR0h4ZfJpk"
    "TZAvPPqhQ28mXd8cHYNWzThjWOCPGBaYO6vnC8G13FcNf3FAt-PDveEyj6slAKrWLZ"
    "aBeTu-9inqY-Ty-sc0C5MBMSPPD2_z6DG-n8QCn9tjdmabNNFESJhQ9IH0CeoQZ9Vy"
    "cfU3-HyPUL8YO71LIrRFqs1DWh5vAH6tJsTpq6ybdZFY026gSkRsoRFAX3VJTA"
)
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def psql(sql):
    result = subprocess.run(
        ["docker", "exec", "onyx-db", "psql", "-U", "postgres", "-d", "postgres", "-c", sql],
        capture_output=True, text=True
    )
    return result.stdout + result.stderr

# --- verify auth ---
resp = requests.get(f"{BASE_URL}/api/me", headers=HEADERS)
print(f"Auth: {resp.status_code} role={resp.json().get('role')}")

# ---------------------------------------------------------------
# STEP 1: Clear index_attempt rows blocking connector deletion
# ---------------------------------------------------------------
print("\n--- STEP 1: Clear index_attempt rows for cc_pair 2 and 3 ---")
out = psql("DELETE FROM index_attempt WHERE connector_credential_pair_id IN (2, 3); SELECT 'deleted index_attempts'")
print(out.strip())

# ---------------------------------------------------------------
# STEP 2: Delete bad connectors via API
# ---------------------------------------------------------------
print("\n--- STEP 2: Delete bad connectors ---")
for cid in [1, 2]:
    r = requests.delete(f"{BASE_URL}/api/manage/admin/connector/{cid}", headers=HEADERS)
    print(f"  DELETE connector/{cid}: HTTP {r.status_code} {r.text[:150]}")

# ---------------------------------------------------------------
# STEP 3: Update document-set associations via API
# ---------------------------------------------------------------
print("\n--- STEP 3: Update document-set associations via API ---")
r = requests.get(f"{BASE_URL}/api/manage/document-set", headers=HEADERS)
doc_sets = {ds["name"]: ds["id"] for ds in r.json()}
print(f"  Found doc sets: {doc_sets}")

# Robert Corpus → cc_pair 1 (Ingestion API) + cc_pair 4 (PhD Thesis)
if "Robert Corpus" in doc_sets:
    ds_id = doc_sets["Robert Corpus"]
    payload = {"cc_pair_ids": [1, 4], "is_public": True}
    r = requests.patch(f"{BASE_URL}/api/manage/admin/document-set/{ds_id}", headers=HEADERS, json=payload)
    print(f"  PATCH DS {ds_id} 'Robert Corpus' → cc_pairs [1,4]: HTTP {r.status_code} {r.text[:200]}")

# arXiv Auto — Quarantine → cc_pair 1 (Ingestion API only)
quarantine_name = "arXiv Auto \u2014 Quarantine"
if quarantine_name in doc_sets:
    ds_id = doc_sets[quarantine_name]
    payload = {"cc_pair_ids": [1], "is_public": False}
    r = requests.patch(f"{BASE_URL}/api/manage/admin/document-set/{ds_id}", headers=HEADERS, json=payload)
    print(f"  PATCH DS {ds_id} 'arXiv Quarantine' → cc_pairs [1]: HTTP {r.status_code} {r.text[:200]}")

# Scite Citations and Chemistry → empty (no file connectors)
for ds_name in ["Scite Citations", "Chemistry"]:
    if ds_name in doc_sets:
        ds_id = doc_sets[ds_name]
        payload = {"cc_pair_ids": [], "is_public": True}
        r = requests.patch(f"{BASE_URL}/api/manage/admin/document-set/{ds_id}", headers=HEADERS, json=payload)
        print(f"  PATCH DS {ds_id} '{ds_name}' → cc_pairs []: HTTP {r.status_code} {r.text[:200]}")

# Verify
print("\n  Verification:")
r = requests.get(f"{BASE_URL}/api/manage/document-set", headers=HEADERS)
for ds in r.json():
    cc_names = [cc.get("name", "?") for cc in ds.get("cc_pair_descriptors", [])]
    print(f"    DS {ds['id']} '{ds['name']}' → {cc_names}")

# ---------------------------------------------------------------
# STEP 4: Smoke-test physics-validator with correct endpoint
# ---------------------------------------------------------------
print("\n--- STEP 4: Smoke test physics-validator ---")
sess = requests.post(
    f"{BASE_URL}/api/chat/create-chat-session",
    headers=HEADERS,
    json={"persona_id": 2, "description": "smoke"},
)
print(f"  Create session: {sess.status_code}")
if sess.status_code == 200:
    session_id = sess.json()["chat_session_id"]
    msg = requests.post(
        f"{BASE_URL}/api/chat/send-chat-message",
        headers=HEADERS,
        json={
            "chat_session_id": session_id,
            "message": "What is the Tsallis distribution? Reply in one sentence.",
            "prompt_id": None,
            "search_doc_ids": [],
            "file_descriptors": [],
            "parent_message_id": None,
            "stream": False,
        },
    )
    print(f"  Send message: {msg.status_code}")
    if msg.status_code == 200:
        data = msg.json()
        answer = data.get("answer") or str(data)[:500]
        print(f"  Answer: {answer[:400]}")
    else:
        print(f"  Error: {msg.text[:400]}")
else:
    print(f"  Session creation failed: {sess.text[:200]}")
