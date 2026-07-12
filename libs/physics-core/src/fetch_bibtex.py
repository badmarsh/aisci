import requests
import json
import time

papers = [
    "1110.5526",
    "1808.02383",
    "1908.04208",
    "1407.4087",
    "2406.12029",
    "1611.08391",
    "2407.09207",
    "2508.00989",
    "2510.09692",
    "nucl-th/9307020"
]

bibtex_entries = []

for arxiv_id in papers:
    print(f"Fetching {arxiv_id}...")
    try:
        # Search for the paper by arxiv id
        res = requests.get(f"https://inspirehep.net/api/literature?q=arxiv:{arxiv_id}")
        data = res.json()
        if data.get('hits', {}).get('total', 0) > 0:
            # Get the first hit's bibtex
            bibtex_url = data['hits']['hits'][0]['links']['bibtex']
            bibtex_res = requests.get(bibtex_url)
            bibtex_entries.append(bibtex_res.text)
        else:
            print(f"Not found: {arxiv_id}")
    except Exception as e:
        print(f"Error fetching {arxiv_id}: {e}")
    time.sleep(1)

with open('/home/ubuntu/aisci/research/robert/bibliography.bib', 'w') as f:
    f.write('\n\n'.join(bibtex_entries))

print("Done. Saved to bibliography.bib")
