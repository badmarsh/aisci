import yaml

with open("/home/ubuntu/aisci/deployment/onyx/litellm_config.yaml", "r") as f:
    config = yaml.safe_load(f)

api_key = "sk-1bb271ee62cf4000857ed3c3009a43b7"
api_base = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

text_models = [
    "qwen3.6-plus",
    "qwen3-coder-plus",
    "qwen-turbo",
    "qwen-plus",
    "deepseek-v3.2",
    "qwen3.6-max-preview"
]

image_models = [
    "wan2.1-vace-plus",
    "happyhorse-1.0-video-edit",
    "wan2.7-videoedit",
    "wan2.5-i2v-preview",
    "wan2.1-kf2v-plus",
    "wan2.2-t2i-flash",
    "wan2.2-i2v-plus",
    "qwen-image-edit-plus",
    "wan2.2-t2i-plus",
    "qwen-image-edit-plus-2025-10-30",
    "wan2.2-i2v-flash",
    "qwen-image-2.0-2026-03-03",
    "wan2.6-image",
    "wan2.6-t2v",
    "qwen-image-edit-max",
    "qwen-image-max",
    "qwen-image-2.0-pro-2026-03-03",
    "qwen-image-edit",
    "wan2.5-i2i-preview",
    "qwen-image",
    "qwen-image-plus",
    "qwen-image-2.0-pro",
    "qwen-image-2.0",
    "qwen-image-plus-2026-01-09",
    "wan2.2-t2v-plus",
    "wan2.7-t2v",
    "wan2.1-i2v-plus",
    "z-image-turbo",
    "qwen-image-max-2025-12-30",
    "wan2.7-r2v",
    "wan2.2-animate-move",
    "wan2.7-image-pro",
    "wan2.1-t2i-plus",
    "wan2.2-animate-mix",
    "wan2.6-t2i",
    "qwen-image-edit-max-2026-01-16",
    "qwen-image-2.0-pro-2026-04-22",
    "wan2.5-t2v-preview",
    "wan2.1-t2v-plus",
    "happyhorse-1.0-t2v",
    "wan2.7-t2v-2026-04-25",
    "qwen-image-edit-plus-2025-12-15",
    "wan2.6-r2v-flash",
    "wan2.7-image",
    "wan2.5-t2i-preview",
    "wan2.1-t2v-turbo",
    "wan2.1-i2v-turbo",
    "wan2.1-t2i-turbo"
]

existing_models = {m.get('model_name') for m in config.get('model_list', [])}

for m in text_models + image_models:
    model_name = m
    # To avoid conflict with existing Qwen models, maybe append `-compatible` or just use the model name.
    # The existing models have names like `qwen-plus`, `qwen-turbo`...
    if m in ["qwen-turbo", "qwen-plus"]:
        model_name = m + "-compatible"
        
    config['model_list'].append({
        'model_name': model_name,
        'litellm_params': {
            'api_key': api_key,
            'model': f"openai/{m}",
            'api_base': api_base
        }
    })

with open("/home/ubuntu/aisci/deployment/onyx/litellm_config.yaml", "w") as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
