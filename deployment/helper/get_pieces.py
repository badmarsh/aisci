from __future__ import annotations
import requests

jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjEifQ.eyJpZCI6ImFWVlF2VmVCc0tNdE95SWFGd09NSCIsInR5cGUiOiJVU0VSIiwicGxhdGZvcm0iOnsiaWQiOiI2ZkFVcWdKNVg4aWtHZFZ2WlhoczcifSwidG9rZW5WZXJzaW9uIjoiX2xNekFWWVBiNU92WUNtMVM4cE9CIiwiaWF0IjoxNzgwNjAyMDc3LCJleHAiOjE3ODEyMDY4NzcsImlzcyI6ImFjdGl2ZXBpZWNlcyJ9._FQx8_hPaJEABg2X29emrRbv5hSUPjDnPE7G8wsVRmU"
headers = {"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"}

# Try to list pieces
try:
    res = requests.get("http://localhost:8082/api/v1/pieces", headers=headers)
    print("Pieces status:", res.status_code)
    pieces = res.json()
    # Print the name and version of the http piece
    for p in pieces:
        if "http" in p["name"].lower() or "webhook" in p["name"].lower():
            print(p["name"], p["version"])
except Exception as e:
    print(e)
