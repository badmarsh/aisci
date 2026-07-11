import urllib.request
import json
import urllib.parse

# Search for ALICE pp 13 TeV papers using V0M estimator
query = 'collaboration:ALICE AND "13 TeV" AND ("V0M" OR "V0M multiplicity" OR "VZERO") AND ("multiplicity dependence" OR "high multiplicity")'
url = f'https://inspirehep.net/api/literature?q={urllib.parse.quote(query)}&sort=mostrecent&size=10'

req = urllib.request.Request(url, headers={'Accept': 'application/json'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    
    for hit in data.get('hits', {}).get('hits', []):
        metadata = hit['metadata']
        title = metadata.get('titles', [{}])[0].get('title', '')
        arxiv = ''
        if 'arxiv_eprints' in metadata:
            arxiv = metadata['arxiv_eprints'][0].get('value', '')
        recid = metadata.get('control_number', '')
        print(f"[{recid}] arXiv:{arxiv} - {title}")
