import os
import httpx
from PIL import Image
import io

API_KEY = os.environ.get("QWEN_API_KEY")

img = Image.new('RGB', (1024, 1024), color = 'red')
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='PNG')
img_byte_arr.seek(0)

url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/images/edits"
files = {
    'image': ('image.png', img_byte_arr, 'image/png')
}
data = {
    'prompt': 'A blue sky',
    'model': 'qwen-image-edit-plus'
}
headers = {
    'Authorization': f'Bearer {API_KEY}'
}

with httpx.Client() as client:
    res = client.post(url, data=data, files=files, headers=headers)
    print(res.status_code)
    print(res.text)
