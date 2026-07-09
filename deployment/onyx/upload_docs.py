import os, sys, requests
BASE_URL = "http://localhost:3000"
session = requests.Session()
r = session.post(
    f"{BASE_URL}/api/auth/login",
    data={"username": "admin@example.com", "password": "password123!"}
)

CONNECTOR_ID = 2
docs_dir = "/home/ubuntu/aisci/docs"
md_files = []
for root, dirs, files in os.walk(docs_dir):
    for file in files:
        if file.endswith(".md"):
            md_files.append(os.path.join(root, file))

print(f"Found {len(md_files)} markdown files.")

file_handles = []
files_param = []
try:
    for md_path in md_files:
        name = os.path.relpath(md_path, docs_dir).replace("/", "_")
        fh = open(md_path, "rb")
        file_handles.append(fh)
        files_param.append(("files", (name, fh, "text/plain")))
        
    data = {"file_ids_to_remove": "[]"}
    print(f"Uploading files to connector {CONNECTOR_ID}...")
    r = session.post(
        f"{BASE_URL}/api/manage/admin/connector/{CONNECTOR_ID}/files/update",
        files=files_param,
        data=data,
    )
finally:
    for fh in file_handles:
        fh.close()

if r.status_code not in (200, 201):
    print(f"Failed upload: {r.status_code} {r.text}")
    sys.exit(1)
    
print("Success. Files uploaded and indexing triggered.")
