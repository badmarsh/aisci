import os
import httpx
from PIL import Image
import io
import base64

API_KEY = os.environ.get("QWEN_API_KEY")

img = Image.new('RGB', (1024, 1024), color = 'red')
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='PNG')
img_byte_arr.seek(0)
b64_img = base64.b64encode(img_byte_arr.read()).decode('utf-8')

url = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
payload = {
    "model": "qwen-image-edit-plus",
    "input": {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"image": f"data:image/png;base64,{b64_img}"},
                    {"text": "Make it blue"}
                ]
            }
        ]
    },
    "parameters": {}
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

with httpx.Client() as client:
    res = client.post(url, json=payload, headers=headers)
    print(res.status_code)
    print(res.text)
