import urllib.request
import json
import urllib.parse

# Get specific paper metadata
url = 'https://inspirehep.net/api/literature?q=arxiv:2603.13203'

req = urllib.request.Request(url, headers={'Accept': 'application/json'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    
    for hit in data.get('hits', {}).get('hits', []):
        metadata = hit['metadata']
        abstract = metadata.get('abstracts', [{}])[0].get('value', '')
        print(f"Abstract: {abstract}")
        
        # also look for HEPData links
        print("\nExternal identifiers:")
        for ext in metadata.get('external_system_identifiers', []):
            print(f"- {ext.get('schema')}: {ext.get('value')}")
