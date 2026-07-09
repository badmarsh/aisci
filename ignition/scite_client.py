import os
import json
import urllib.request
from database import get_db

def query_scite_for_doi(doi: str):
    api_key = os.environ.get("SCITE_API_KEY")
    
    if not api_key:
        print(f"[Scite.ai] Skipped citation lookup for {doi}: No SCITE_API_KEY in environment.")
        return None
        
    url = f"https://api.scite.ai/tallies/{doi}"
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {api_key}'})
    
    try:
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read())
        return data
    except Exception as e:
        print(f"[Scite.ai] Failed to fetch tallies for {doi}: {e}")
        return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        res = query_scite_for_doi(sys.argv[1])
        print(json.dumps(res, indent=2))
    else:
        print("Usage: python3 scite_client.py <DOI>")
