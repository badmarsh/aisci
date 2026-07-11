from __future__ import annotations
import os
import boto3
from sqlalchemy import text
from onyx.db.engine import get_sqlalchemy_engine
from onyx.configs.app_configs import S3_AWS_ACCESS_KEY_ID, S3_AWS_SECRET_ACCESS_KEY

engine = get_sqlalchemy_engine()
with engine.connect() as conn:
    rows = conn.execute(text("SELECT file_id, display_name FROM file_record WHERE file_origin = 'CONNECTOR'")).fetchall()

# Map display_name to real path
real_paths = {}
for root, dirs, files in os.walk("/workspace/aisci/docs"):
    for file in files:
        if file.endswith(".md"):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, "/workspace/aisci/docs")
            display_name = rel_path.replace("/", "_")
            real_paths[display_name] = full_path

found = 0
missing = 0
s3 = boto3.client('s3', endpoint_url='http://onyx-minio:9000', aws_access_key_id=S3_AWS_ACCESS_KEY_ID, aws_secret_access_key=S3_AWS_SECRET_ACCESS_KEY)

for file_id, display_name in rows:
    if display_name in real_paths:
        full_path = real_paths[display_name]
        print(f"Found {display_name} -> {full_path}")
        # Upload to S3
        with open(full_path, "rb") as f:
            s3.put_object(Bucket='onyx-file-store-bucket', Key=f"onyx-files/public/{file_id}", Body=f.read())
        found += 1
    else:
        print(f"MISSING {display_name}")
        missing += 1

print(f"Uploaded {found} files. Missing {missing}")
