import json

with open("deployment/helper/openapi.json", "r") as f:
    schema = json.load(f)

for path in schema.get("paths", {}).keys():
    if "search" in path.lower() or "query" in path.lower() or "chat" in path.lower():
        print(path)
