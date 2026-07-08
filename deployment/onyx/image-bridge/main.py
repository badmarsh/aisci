"""
OpenAI-compatible image generation bridge for Alibaba DashScope and OpenRouter.

Accepts:  POST /v1/images/generations   (OpenAI format)
          POST /v1/images/edits         (OpenAI format, multipart)
Returns:  OpenAI-format response

Hardened variant:
- Pydantic validation with bounds (n, size, prompt length) so invalid inputs
  are rejected at the FastAPI layer with a 422 before any upstream call.
- Every upstream httpx call is wrapped: timeouts, network errors, non-2xx
  responses, and malformed JSON all surface as structured 502/504 responses
  with a friendly `error` object, never a raw traceback or provider payload.
- File uploads (image / mask) are size-checked and content-type-checked
  before base64-encoding, to avoid loading unbounded bytes into memory.
- All logs go through the stdlib logger, never `print`, and never include
  API keys.
"""

from __future__ import annotations

import base64
import logging
import os
import re
import time
from typing import Any, Optional

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger("image_bridge")
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))

app = FastAPI(title="Onyx Image Bridge", version="1.1.0")

DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("QWEN_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

DASHSCOPE_URL = (
    "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/"
    "multimodal-generation/generation"
)
OPENROUTER_URL = "https://openrouter.ai/api/v1/images/generations"

DEFAULT_MODEL = os.environ.get(
    "IMAGE_GENERATION_MODEL", "google/gemini-3-pro-image-preview"
)

MAX_PROMPT_CHARS = 4000
MAX_N = 4
MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8 MiB
ALLOWED_IMAGE_MIME = {"image/png", "image/jpeg", "image/webp"}
SIZE_RE = re.compile(r"^\d{2,5}x\d{2,5}$")

UPSTREAM_TIMEOUT = 120.0
DOWNLOAD_TIMEOUT = 60.0


# --------------------------------------------------------------------------- #
# Validation                                                                  #
# --------------------------------------------------------------------------- #

class ImageRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=MAX_PROMPT_CHARS)
    model: Optional[str] = Field(None, max_length=200)
    n: Optional[int] = Field(1, ge=1, le=MAX_N)
    size: Optional[str] = Field("1024x1024")
    response_format: Optional[str] = Field("b64_json")
    quality: Optional[str] = None
    style: Optional[str] = None

    @field_validator("size")
    @classmethod
    def _size_shape(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not SIZE_RE.match(v):
            raise ValueError("size must look like '1024x1024'")
        return v

    @field_validator("response_format")
    @classmethod
    def _fmt(cls, v: Optional[str]) -> Optional[str]:
        if v not in (None, "b64_json", "url"):
            raise ValueError("response_format must be 'b64_json' or 'url'")
        return v


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #

def _error(status: int, code: str, message: str, **extra: Any) -> HTTPException:
    """Return an HTTPException whose detail is a structured, user-friendly payload."""
    detail: dict[str, Any] = {"error": {"code": code, "message": message}}
    if extra:
        detail["error"].update(extra)
    return HTTPException(status_code=status, detail=detail)


async def _post_json(url: str, *, headers: dict, payload: dict, provider: str) -> dict:
    """POST JSON with hardened error handling; returns parsed JSON dict."""
    try:
        async with httpx.AsyncClient(timeout=UPSTREAM_TIMEOUT) as client:
            resp = await client.post(url, json=payload, headers=headers)
    except httpx.TimeoutException:
        logger.warning("%s upstream timed out", provider)
        raise _error(504, "upstream_timeout",
                     f"{provider} did not respond within {UPSTREAM_TIMEOUT:.0f}s. Try again.")
    except httpx.HTTPError as exc:
        logger.warning("%s network error: %s", provider, exc)
        raise _error(502, "upstream_unavailable",
                     f"Could not reach {provider}. Please try again shortly.")

    if resp.status_code >= 500:
        logger.error("%s 5xx: %s", provider, resp.text[:500])
        raise _error(502, "upstream_error",
                     f"{provider} is temporarily unavailable.",
                     upstream_status=resp.status_code)
    if resp.status_code >= 400:
        # Surface client-side provider errors but strip anything that looks
        # like a leaked credential.
        safe = _scrub(resp.text)[:500]
        raise _error(resp.status_code, "upstream_rejected",
                     f"{provider} rejected the request.", upstream_body=safe)

    try:
        return resp.json()
    except ValueError:
        raise _error(502, "upstream_malformed",
                     f"{provider} returned a non-JSON response.")


def _scrub(text: str) -> str:
    """Best-effort removal of bearer tokens/keys from provider error bodies."""
    return re.sub(r"(sk-[A-Za-z0-9_-]{10,}|Bearer\s+\S+)", "***", text)


def _extract_dashscope_images(data: dict) -> list[str]:
    output = data.get("output") or {}
    if "results" in output:
        return [r["url"] for r in output["results"] if isinstance(r, dict) and r.get("url")]
    if "choices" in output:
        out: list[str] = []
        for choice in output["choices"]:
            for content in (choice or {}).get("message", {}).get("content", []):
                if isinstance(content, dict) and content.get("type") == "image" and content.get("image"):
                    out.append(content["image"])
        return out
    return []


async def _to_openai_images(
    urls: list[str], *, response_format: str, prompt: str
) -> list[dict]:
    if response_format != "b64_json":
        return [{"url": u, "revised_prompt": prompt} for u in urls]

    out: list[dict] = []
    async with httpx.AsyncClient(timeout=DOWNLOAD_TIMEOUT) as client:
        for url in urls:
            try:
                img_resp = await client.get(url)
                if img_resp.status_code == 200:
                    b64 = base64.b64encode(img_resp.content).decode("utf-8")
                    out.append({"b64_json": b64, "revised_prompt": prompt})
                else:
                    logger.warning("image download %s -> %s", url, img_resp.status_code)
                    out.append({"url": url, "revised_prompt": prompt})
            except httpx.HTTPError as exc:
                logger.warning("image download failed for %s: %s", url, exc)
                out.append({"url": url, "revised_prompt": prompt})
    return out


# --------------------------------------------------------------------------- #
# Routes                                                                      #
# --------------------------------------------------------------------------- #

@app.post("/images/generations")
@app.post("/v1/images/generations")
async def generate_image(req: ImageRequest) -> JSONResponse:
    model = req.model or DEFAULT_MODEL
    is_openrouter = any(x in model for x in ("google/", "openai/", "anthropic/", "gemini"))

    if is_openrouter:
        if not OPENROUTER_API_KEY:
            raise _error(503, "provider_not_configured",
                         "OpenRouter is not configured on this deployment.")
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
        data = await _post_json(OPENROUTER_URL, headers=headers, payload=payload,
                                provider="OpenRouter")
        return JSONResponse(data)

    # DashScope path
    if not DASHSCOPE_API_KEY:
        raise _error(503, "provider_not_configured",
                     "DashScope is not configured on this deployment.")

    payload = {
        "model": model,
        "input": {"messages": [{"role": "user", "content": [{"text": req.prompt}]}]},
        "parameters": {
            "size": (req.size or "1024x1024").replace("x", "*"),
            "n": req.n or 1,
            "prompt_extend": True,
            "watermark": False,
        },
    }
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }
    data = await _post_json(DASHSCOPE_URL, headers=headers, payload=payload,
                            provider="DashScope")

    images = _extract_dashscope_images(data)
    if not images:
        logger.error("DashScope returned no images: %s", str(data)[:500])
        raise _error(502, "upstream_empty",
                     "The image provider returned no images. Try a different prompt.")

    formatted = await _to_openai_images(
        images, response_format=req.response_format or "b64_json", prompt=req.prompt
    )
    return JSONResponse({"created": int(time.time()), "data": formatted})


@app.post("/images/edits")
@app.post("/v1/images/edits")
async def edit_image(
    image: UploadFile = File(...),
    mask: Optional[UploadFile] = File(None),
    prompt: str = Form(..., min_length=1, max_length=MAX_PROMPT_CHARS),
    model: Optional[str] = Form(None),
    n: int = Form(1, ge=1, le=MAX_N),
    size: str = Form("1024x1024"),
    response_format: str = Form("b64_json"),
) -> JSONResponse:
    if not DASHSCOPE_API_KEY:
        raise _error(503, "provider_not_configured",
                     "DashScope is not configured on this deployment.")
    if not SIZE_RE.match(size):
        raise _error(422, "invalid_size", "size must look like '1024x1024'")
    if response_format not in ("b64_json", "url"):
        raise _error(422, "invalid_response_format",
                     "response_format must be 'b64_json' or 'url'")

    target_model = model or "qwen-image-edit-plus"

    async def _read_bounded(upload: UploadFile, field: str) -> tuple[bytes, str]:
        mime = upload.content_type or "image/png"
        if mime not in ALLOWED_IMAGE_MIME:
            raise _error(415, "unsupported_media_type",
                         f"{field} must be one of {sorted(ALLOWED_IMAGE_MIME)}",
                         received=mime)
        data = await upload.read()
        if len(data) > MAX_UPLOAD_BYTES:
            raise _error(413, "payload_too_large",
                         f"{field} exceeds {MAX_UPLOAD_BYTES // (1024 * 1024)} MiB",
                         received_bytes=len(data))
        if not data:
            raise _error(422, "empty_upload", f"{field} is empty")
        return data, mime

    image_bytes, image_mime = await _read_bounded(image, "image")
    content_list: list[dict] = [
        {"image": f"data:{image_mime};base64,{base64.b64encode(image_bytes).decode()}"}
    ]
    if mask is not None:
        mask_bytes, mask_mime = await _read_bounded(mask, "mask")
        content_list.append(
            {"image": f"data:{mask_mime};base64,{base64.b64encode(mask_bytes).decode()}"}
        )
    content_list.append({"text": prompt})

    payload = {
        "model": target_model,
        "input": {"messages": [{"role": "user", "content": content_list}]},
        "parameters": {
            "size": size.replace("x", "*"),
            "n": n,
            "prompt_extend": True,
            "watermark": False,
        },
    }
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }
    data = await _post_json(DASHSCOPE_URL, headers=headers, payload=payload,
                            provider="DashScope")

    images = _extract_dashscope_images(data)
    if not images:
        logger.error("DashScope edit returned no images: %s", str(data)[:500])
        raise _error(502, "upstream_empty",
                     "The image provider returned no images. Try a different prompt.")

    formatted = await _to_openai_images(images, response_format=response_format, prompt=prompt)
    return JSONResponse({"created": int(time.time()), "data": formatted})


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "providers": {
            "dashscope": bool(DASHSCOPE_API_KEY),
            "openrouter": bool(OPENROUTER_API_KEY),
        },
    }
