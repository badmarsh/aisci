from __future__ import annotations
import json
with open("deployment/helper/openapi.json", "r") as f:
    data = json.load(f)
for path, methods in data.get("paths", {}).items():
    if "send-message" in path or "chat" in path:
        print(path)
