"""
Minimal OpenAI-compatible image generation bridge for Alibaba DashScope.
Accepts: POST /v1/images/generations (OpenAI format)
Calls:   DashScope multimodal-generation API (Singapore)
Returns: OpenAI-format response
"""

import os
import time
import httpx
from fastapi import FastAPI, HTTPException, Request, File, Form, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY") or os.environ["QWEN_API_KEY"]
DASHSCOPE_URL = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
DEFAULT_MODEL = os.environ.get("IMAGE_MODEL", "qwen-image-2.0-pro")


class ImageRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    n: Optional[int] = 1
    size: Optional[str] = "1024x1024"
    response_format: Optional[str] = "b64_json"
    quality: Optional[str] = None
    style: Optional[str] = None


@app.post("/images/generations")
@app.post("/v1/images/generations")
async def generate_image(req: ImageRequest):
    model = DEFAULT_MODEL

    # Convert OpenAI size (1024x1024) to DashScope size (1024*1024)
    size = req.size.replace("x", "*") if req.size else "1024*1024"

    payload = {
        "model": model,
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": req.prompt}]
                }
            ]
        },
        "parameters": {
            "size": size,
            "n": req.n or 1,
            "prompt_extend": True,
            "watermark": False,
        }
    }

    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(DASHSCOPE_URL, json=payload, headers=headers)

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    data = resp.json()

    # Extract image URLs from DashScope response
    try:
        images = []
        if "results" in data.get("output", {}):
            results = data["output"]["results"]
            images = [r["url"] for r in results]
        elif "choices" in data.get("output", {}):
            for choice in data["output"]["choices"]:
                for content in choice.get("message", {}).get("content", []):
                    if content.get("type") == "image":
                        images.append(content["image"])
        
        if not images:
            raise KeyError("No images found")
            
        formatted_images = []
        for url in images:
            if req.response_format == "b64_json":
                import base64
                async with httpx.AsyncClient(timeout=60.0) as img_client:
                    img_resp = await img_client.get(url)
                    if img_resp.status_code == 200:
                        b64 = base64.b64encode(img_resp.content).decode("utf-8")
                        formatted_images.append({"b64_json": b64, "revised_prompt": req.prompt})
                    else:
                        formatted_images.append({"url": url, "revised_prompt": req.prompt})
            else:
                formatted_images.append({"url": url, "revised_prompt": req.prompt})
                
    except (KeyError, TypeError):
        raise HTTPException(status_code=502, detail=f"Unexpected DashScope response: {data}")

    return JSONResponse({
        "created": int(time.time()),
        "data": formatted_images,
    })


@app.post("/images/edits")
@app.post("/v1/images/edits")
async def edit_image(
    image: UploadFile = File(...),
    mask: Optional[UploadFile] = File(None),
    prompt: str = Form(...),
    model: Optional[str] = Form(None),
    n: int = Form(1),
    size: str = Form("1024x1024"),
    response_format: str = Form("b64_json")
):
    target_model = model or "qwen-image-edit-plus"

    # Convert OpenAI size (1024x1024) to DashScope size (1024*1024)
    size_dashscope = size.replace("x", "*") if size else "1024*1024"

    import base64
    image_bytes = await image.read()
    b64_img = base64.b64encode(image_bytes).decode("utf-8")
    mime_type = image.content_type or "image/png"

    content_list = [{"image": f"data:{mime_type};base64,{b64_img}"}]
    if mask:
        mask_bytes = await mask.read()
        mask_b64 = base64.b64encode(mask_bytes).decode("utf-8")
        mask_mime = mask.content_type or "image/png"
        content_list.append({"image": f"data:{mask_mime};base64,{mask_b64}"})

    content_list.append({"text": prompt})

    payload = {
        "model": target_model,
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": content_list
                }
            ]
        },
        "parameters": {
            "size": size_dashscope,
            "n": n,
            "prompt_extend": True,
            "watermark": False,
        }
    }

    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(DASHSCOPE_URL, json=payload, headers=headers)

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    data = resp.json()

    # Extract image URLs from DashScope response
    try:
        images = []
        if "results" in data.get("output", {}):
            results = data["output"]["results"]
            images = [r["url"] for r in results]
        elif "choices" in data.get("output", {}):
            for choice in data["output"]["choices"]:
                for content in choice.get("message", {}).get("content", []):
                    if content.get("type") == "image":
                        images.append(content["image"])
        
        if not images:
            raise KeyError("No images found")
            
        formatted_images = []
        for url in images:
            if response_format == "b64_json":
                async with httpx.AsyncClient(timeout=60.0) as img_client:
                    img_resp = await img_client.get(url)
                    if img_resp.status_code == 200:
                        b64 = base64.b64encode(img_resp.content).decode("utf-8")
                        formatted_images.append({"b64_json": b64, "revised_prompt": prompt})
                    else:
                        formatted_images.append({"url": url, "revised_prompt": prompt})
            else:
                formatted_images.append({"url": url, "revised_prompt": prompt})
                
    except (KeyError, TypeError):
        raise HTTPException(status_code=502, detail=f"Unexpected DashScope response: {data}")

    return JSONResponse({
        "created": int(time.time()),
        "data": formatted_images,
    })


@app.get("/health")
async def health():
    return {"status": "ok"}
