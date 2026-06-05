import yaml
import os
import requests
import re
from dotenv import load_dotenv

load_dotenv('/home/ubuntu/aisci/deployment/deer-flow/.env')

with open('/home/ubuntu/aisci/deployment/deer-flow/config.yaml', 'r') as f:
    live = f.read()

config = yaml.safe_load(live)
models = config.get('models', [])

working_models = []

for m in models:
    api_key_env = m.get('api_key', '')
    base_url_env = m.get('base_url', '')
    
    # resolve env vars
    if str(api_key_env).startswith('$'):
        api_key = os.environ.get(api_key_env[1:], api_key_env)
    else:
        api_key = api_key_env
        
    if str(base_url_env).startswith('$'):
        base_url = os.environ.get(base_url_env[1:], base_url_env)
    else:
        base_url = base_url_env
        
    if not base_url:
        base_url = "https://api.openai.com/v1"
        
    print(f"Testing model {m['name']} ({m.get('model')}) at {base_url} ...")
    
    if api_key:
        api_key = api_key.strip("'").strip('"')
    if base_url:
        base_url = base_url.strip("'").strip('"')
        
    # Replace docker network hostnames with localhost for testing
    test_base_url = base_url.replace("onyx-litellm", "localhost").replace("host.docker.internal", "localhost")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": m.get('model', m['name']),
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 10
    }
    
    try:
        url = test_base_url.rstrip('/') + '/chat/completions'
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if resp.status_code == 200:
            print(f"  -> SUCCESS")
            working_models.append(m)
        else:
            print(f"  -> FAILED: {resp.status_code} {resp.text[:100]}")
    except Exception as e:
        print(f"  -> ERROR: {e}")

print(f"\nKept {len(working_models)} out of {len(models)} models.")

class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

models_yaml = yaml.dump({'models': working_models}, Dumper=MyDumper, default_flow_style=False, sort_keys=False)

new_live = re.sub(r"\nmodels:\n.*?(?=\ntool_groups:)", "\n" + models_yaml, live, flags=re.DOTALL)

with open('/home/ubuntu/aisci/deployment/deer-flow/config.yaml', 'w') as f:
    f.write(new_live)

