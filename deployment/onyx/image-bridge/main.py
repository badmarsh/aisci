"""
OpenAI-compatible image generation bridge for Alibaba DashScope and OpenRouter.
Accepts: POST /v1/images/generations (OpenAI format)
Returns: OpenAI-format response
"""

import os
import time
import httpx
import base64
from fastapi import FastAPI, HTTPException, Request, File, Form, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Union

app = FastAPI()

DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("QWEN_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

DASHSCOPE_URL = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
OPENROUTER_URL = "https://openrouter.ai/api/v1/images/generations"

DEFAULT_MODEL = os.environ.get("IMAGE_GENERATION_MODEL", "google/gemini-3-pro-image-preview")

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
    model = req.model or DEFAULT_MODEL
    
    # Provider detection
    is_dashscope = any(x in model for x in ["qwen-image", "wan2", "z-image"])
    is_openrouter = any(x in model for x in ["google/", "openai/", "anthropic/", "gemini"])
    
    if is_openrouter:
        if not OPENROUTER_API_KEY:
             raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY not configured")
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://onyx.app",
            "X-Title": "Onyx Image Bridge",
        }
        payload = {
            "model": model,
            "prompt": req.prompt,
            "n": req.n or 1,
            "size": req.size or "1024x1024",
            "response_format": req.response_format or "b64_json",
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(OPENROUTER_URL, json=payload, headers=headers)
            
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
            
        return JSONResponse(resp.json())

    else:
        # Default to DashScope for the free models provided
        if not DASHSCOPE_API_KEY:
            raise HTTPException(status_code=500, detail="DASHSCOPE_API_KEY not configured")
            
        size_dashscope = req.size.replace("x", "*") if req.size else "1024*1024"
        payload = {
            "model": model,
            "input": {
                "messages": [{"role": "user", "content": [{"text": req.prompt}]}]
            },
            "parameters": {
                "size": size_dashscope,
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
    
    # Only DashScope supported for edits in this bridge currently
    if not DASHSCOPE_API_KEY:
        raise HTTPException(status_code=500, detail="DASHSCOPE_API_KEY not configured")

    size_dashscope = size.replace("x", "*") if size else "1024*1024"
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
            "messages": [{"role": "user", "content": content_list}]
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
    try:
        images = []
        if "results" in data.get("output", {}):
            images = [r["url"] for r in data["output"]["results"]]
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
