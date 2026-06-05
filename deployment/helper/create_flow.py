import requests
import json

jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjEifQ.eyJpZCI6ImFWVlF2VmVCc0tNdE95SWFGd09NSCIsInR5cGUiOiJVU0VSIiwicGxhdGZvcm0iOnsiaWQiOiI2ZkFVcWdKNVg4aWtHZFZ2WlhoczcifSwidG9rZW5WZXJzaW9uIjoiX2xNekFWWVBiNU92WUNtMVM4cE9CIiwiaWF0IjoxNzgwNjAyMDc3LCJleHAiOjE3ODEyMDY4NzcsImlzcyI6ImFjdGl2ZXBpZWNlcyJ9._FQx8_hPaJEABg2X29emrRbv5hSUPjDnPE7G8wsVRmU"
project_id = "KaLdcxpzcwALFF8CAGyfr"
headers = {"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"}

payload = {
    "displayName": "Weekly ArXiv Scan",
    "projectId": project_id
}

res = requests.post("http://localhost:8082/api/v1/flows", json=payload, headers=headers)
print(res.status_code)
print(res.text)
