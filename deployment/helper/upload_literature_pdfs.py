"""
Upload Khuntia 2019 and Rath 2020 baseline literature PDFs to the
existing Onyx file connector (connector_id=3, cc_pair_id=4) using the
atomic /admin/connector/{id}/files/update endpoint, which adds files
AND triggers re-indexing in one call.

Run from repo root:
  python3 deployment/helper/upload_literature_pdfs.py
"""
import os, sys, json, requests

BASE_URL = "http://localhost:3000"


def load_api_key() -> str:
    key = os.environ.get("ONYX_API_KEY", "").strip()
    if key:
        return key
    env_path = os.path.join(os.path.dirname(__file__), "..", "onyx", ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("ONYX_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("ONYX_API_KEY not in env and not in deployment/onyx/.env")


API_KEY = load_api_key()
HEADERS_AUTH = {"Authorization": f"Bearer {API_KEY}"}

CONNECTOR_ID = 3

PDFS = [
    "/home/ubuntu/aisci/literature/Khuntia_2019_1808.02383.pdf",
    "/home/ubuntu/aisci/literature/Rath_2020_1908.04208.pdf",
]

# ── 0. verify auth ─────────────────────────────────────────────────────────
print("STEP 0 – Auth check")
r = requests.get(f"{BASE_URL}/api/me", headers={**HEADERS_AUTH, "Content-Type": "application/json"})
if r.status_code != 200 or r.json().get("role") != "admin":
    print(f"  AUTH FAILED: {r.status_code} {r.text}")
    sys.exit(1)
print("  Auth OK")

# ── 1. confirm PDFs exist ──────────────────────────────────────────────────
print("\nSTEP 1 – Checking files")
for p in PDFS:
    if not os.path.exists(p):
        print(f"  MISSING: {p}")
        sys.exit(1)
    print(f"  OK: {p} ({os.path.getsize(p)//1024} KB)")

# ── 2. open all files and call the atomic update endpoint ──────────────────
print(f"\nSTEP 2 – Uploading to connector {CONNECTOR_ID} (atomic update + re-index)")

file_handles = []
files_param  = []
try:
    for pdf_path in PDFS:
        name = os.path.basename(pdf_path)
        fh = open(pdf_path, "rb")
        file_handles.append(fh)
        files_param.append(("files", (name, fh, "application/pdf")))

    data = {"file_ids_to_remove": "[]"}

    r = requests.post(
        f"{BASE_URL}/api/manage/admin/connector/{CONNECTOR_ID}/files/update",
        headers=HEADERS_AUTH,
        files=files_param,
        data=data,
    )
finally:
    for fh in file_handles:
        fh.close()

if r.status_code not in (200, 201):
    print(f"  FAILED: {r.status_code} {r.text}")
    sys.exit(1)

resp = r.json()
print(f"  Success: {json.dumps(resp, indent=2)}")
print("\nDone. Indexing triggered automatically. Wait ~2–5 min then re-run run_rag_tests.py")
