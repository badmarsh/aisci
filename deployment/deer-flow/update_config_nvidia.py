import yaml

with open('/home/ubuntu/aisci/deployment/deer-flow/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Keep non-NVIDIA models
new_models = [m for m in config.get('models', []) if not m['name'].startswith('nvidia-')]

# Add the working NVIDIA models
working_nvidia = [
    {
        'name': 'nvidia-llama-3-3-70b-instruct',
        'display_name': 'Llama 3.3 70B (NVIDIA)',
        'use': 'langchain_openai:ChatOpenAI',
        'model': 'meta/llama-3.3-70b-instruct',
        'api_key': '',
        'base_url': 'https://integrate.api.nvidia.com/v1',
        'max_tokens': 32768
    },
    {
        'name': 'nvidia-llama-3-1-70b-instruct',
        'display_name': 'Llama 3.1 70B (NVIDIA)',
        'use': 'langchain_openai:ChatOpenAI',
        'model': 'meta/llama-3.1-70b-instruct',
        'api_key': '',
        'base_url': 'https://integrate.api.nvidia.com/v1',
        'max_tokens': 32768
    },
    {
        'name': 'nvidia-llama-3-1-8b-instruct',
        'display_name': 'Llama 3.1 8B (NVIDIA)',
        'use': 'langchain_openai:ChatOpenAI',
        'model': 'meta/llama-3.1-8b-instruct',
        'api_key': '',
        'base_url': 'https://integrate.api.nvidia.com/v1',
        'max_tokens': 32768
    }
]

config['models'] = new_models + working_nvidia

with open('/home/ubuntu/aisci/deployment/deer-flow/config.yaml', 'w') as f:
    yaml.dump(config, f, sort_keys=False, default_flow_style=False)

print('Updated config.yaml')
