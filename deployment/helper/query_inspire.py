import urllib.request
import json
import urllib.parse

# Search for ALICE pp 13 TeV papers about multiplicity and transverse momentum
query = 'collaboration:ALICE AND "13 TeV" AND "multiplicity" AND "transverse momentum"'
url = f'https://inspirehep.net/api/literature?q={urllib.parse.quote(query)}&sort=mostrecent&size=20'

req = urllib.request.Request(url, headers={'Accept': 'application/json'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    
    for hit in data.get('hits', {}).get('hits', []):
        metadata = hit['metadata']
        title = metadata.get('titles', [{}])[0].get('title', '')
        arxiv = ''
        if 'arxiv_eprints' in metadata:
            arxiv = metadata['arxiv_eprints'][0].get('value', '')
            
        print(f"[{arxiv}] {title}")
