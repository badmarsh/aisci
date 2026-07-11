import urllib.request
import json

for arxiv in ['2603.13203', '2310.10236']:
    url = f'https://inspirehep.net/api/literature?q=arxiv:{arxiv}'
    req = urllib.request.Request(url, headers={'Accept': 'application/json'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        for hit in data.get('hits', {}).get('hits', []):
            metadata = hit['metadata']
            print(f"--- {arxiv} ---")
            print(f"Title: {metadata.get('titles', [{}])[0].get('title', '')}")
            abstract = metadata.get('abstracts', [{}])[0].get('value', '')
            print(f"Abstract snippet: {abstract[:200]}...")
            for ext in metadata.get('external_system_identifiers', []):
                print(f"- {ext.get('schema')}: {ext.get('value')}")
