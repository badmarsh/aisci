import requests
BASE_URL = "http://localhost:3000"
session = requests.Session()
session.post(
    f"{BASE_URL}/api/auth/login",
    data={"username": "admin@example.com", "password": "password123!"}
)
payload = {
    "name": "DashScope",
    "provider": "dashscope",
    "api_key": "sk-aaf258f793c14578b719a68e4d6f3403",
    "api_base": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    "custom_config": {},
    "is_default_provider": True,
    "is_default_vision_provider": False,
    "default_model_name": "qwen-turbo",
    "fast_default_model_name": "qwen-turbo",
    "model_configurations": [
        {
            "name": "qwen-turbo",
            "model_name": "qwen-turbo",
            "display_name": "Qwen Turbo",
            "is_visible": True,
            "max_input_tokens": 8192,
            "supports_image_input": False
        },
        {
            "name": "qwen-plus",
            "model_name": "qwen-plus",
            "display_name": "Qwen Plus",
            "is_visible": True,
            "max_input_tokens": 8192,
            "supports_image_input": False
        }
    ]
}
r = session.post(f"{BASE_URL}/api/admin/llm/provider", json=payload)
print("Create LLM:", r.status_code, r.text)

r = session.post(f"{BASE_URL}/api/admin/llm/default", json={"provider_name": "DashScope", "model_name": "qwen-turbo"})
r = session.post(f"{BASE_URL}/api/admin/llm/default?is_fast=true", json={"provider_name": "DashScope", "model_name": "qwen-turbo"})

