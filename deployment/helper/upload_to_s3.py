from __future__ import annotations
import os
import boto3

from onyx.configs.app_configs import S3_AWS_ACCESS_KEY_ID, S3_AWS_SECRET_ACCESS_KEY

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

with open("/workspace/aisci/deployment/helper/file_records.txt", "r") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        file_id, display_name = line.split("|", 1)
        
        if display_name in real_paths:
            full_path = real_paths[display_name]
            print(f"Uploading {display_name} -> {full_path}")
            # Upload to S3
            with open(full_path, "rb") as fp:
                s3.put_object(Bucket='onyx-file-store-bucket', Key=f"onyx-files/public/{file_id}", Body=fp.read())
            found += 1
        else:
            missing += 1

print(f"Uploaded {found} files. Missing {missing}")
