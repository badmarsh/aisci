import urllib.request
import json
import urllib.parse

# Get HEPData record details for ins2711421
url = 'https://www.hepdata.net/record/ins2711421?format=json'

req = urllib.request.Request(url, headers={'Accept': 'application/json'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print(f"HEPData Record ID: {data.get('record', {}).get('inspire_id')}")
        print("Data Tables:")
        for table in data.get('data_tables', []):
            print(f"- {table.get('name')}: {table.get('description')}")
except Exception as e:
    print(f"Error fetching HEPData: {e}")
