from __future__ import annotations
import yaml
import os

YAML_PATH = "/home/ubuntu/aisci/deployment/onyx/onyx-litellm_config.yaml"

with open(YAML_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

for model in config.get("model_list", []):
    if model["model_name"] in ("qwen-cloud-fast", "qwen-rag-fast", "qwen-rag-balanced", "qwen-omni-flash", "qwen-max"):
        model["model_info"] = {
            "max_input_tokens": 128000,
            "max_tokens": 8192
        }

with open(YAML_PATH, "w", encoding="utf-8") as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print("Patched litellm config with max_input_tokens = 128000")
