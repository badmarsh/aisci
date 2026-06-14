from __future__ import annotations
import os, sys, json, requests

BASE_URL = "http://localhost:3000"
API_KEY = (
    os.environ.get("ONYX_API_KEY")
    or "on_hLxHEO432IFLuDN3psKyxgLH3g35yvvZqOx21yP1Iw__GrPullG5YR0h4ZfJpkTZAvPPqhQ28mXd8cHYNWzThjWOCPGBaYO6vnC8G13FcNf3FAt-PDveEyj6slAKrWLZaBeTu-9inqY-Ty-sc0C5MBMSPPD2_z6DG-n8QCn9tjdmabNNFESJhQ9IH0CeoQZ9VycfU3-HyPUL8YO71LIrRFqs1DWh5vAH6tJsTpq6ybdZFY026gSkRsoRFAX3VJTA"
)
HEADERS_AUTH = {"Authorization": f"Bearer {API_KEY}"}

CONNECTOR_ID = 4

def main():
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
        print(f"Failed upload: {r.status_code} {r.text}")
        sys.exit(1)
        
    print("Success. Files uploaded and indexing triggered.")

if __name__ == "__main__":
    main()
