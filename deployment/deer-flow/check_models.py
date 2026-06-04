import urllib.request, json
resp = urllib.request.urlopen("http://localhost:2026/api/models")
d = json.loads(resp.read())
print(f"Models: {len(d)}")
for m in d:
    print(" -", m.get("name","?"))
