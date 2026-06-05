import json
with open('id5_config.json') as f:
    text = f.read().strip()
    if not text:
        print('EMPTY FILE')
        exit(0)
    data = json.loads(text)
    
    # We want to identify the fallbacks
    for model in data:
        if 'qwen-fast' in str(model) or 'gemini' in str(model) or 'fallback' in str(model):
            print(f"Model: {model.get('model_name', model.get('name'))}")
            # check if fallback is present anywhere in this dict
            print(json.dumps(model, indent=2))
