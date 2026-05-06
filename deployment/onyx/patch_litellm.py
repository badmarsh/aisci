import yaml

with open('/home/ubuntu/aisci/deployment/onyx/litellm_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

for model_def in config.get('model_list', []):
    params = model_def.get('litellm_params', {})
    model_str = params.get('model', '')
    if model_str.startswith('dashscope/') and 'embedding' not in model_str:
        # Change dashscope/qwen-turbo to openai/qwen-turbo
        new_model_str = model_str.replace('dashscope/', 'openai/')
        params['model'] = new_model_str
        params['api_base'] = 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1'

with open('/home/ubuntu/aisci/deployment/onyx/litellm_config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)
