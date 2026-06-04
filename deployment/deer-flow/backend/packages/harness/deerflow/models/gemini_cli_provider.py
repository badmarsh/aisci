"""Gemini CLI credential loader and ChatModel provider.

Loads credentials from (in priority order):
1. ~/.gemini/oauth_creds.json  (Gemini CLI access_token)
2. /root/.gemini/oauth_creds.json  (Docker mount of host ~/.gemini)
3. ~/.config/gcloud/application_default_credentials.json  (ADC refresh_token)
4. /home/ubuntu/.config/gcloud/application_default_credentials.json  (Docker mount fallback)
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import model_validator
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

GOOGLE_OAUTH_TOKEN_URI = "https://oauth2.googleapis.com/token"

# Standard gcloud ADC client_id/secret (public, as shipped in gcloud SDK)
GCLOUD_CLIENT_ID = "764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com"
GCLOUD_CLIENT_SECRET = "d-FL95Q19q7MQmFpd7hHD0Ty"


def load_gemini_cli_credentials() -> Credentials | None:
    """Try loading credentials from Gemini CLI or ADC files."""
    home = os.getenv("HOME", "/root")

    # --- Attempt 1: Gemini CLI oauth_creds.json (access_token style) ---
    gemini_paths = [
        Path(home) / ".gemini/oauth_creds.json",
        Path("/root/.gemini/oauth_creds.json"),
    ]
    for p in gemini_paths:
        if p.exists():
            try:
                data = json.loads(p.read_text())
                token = data.get("access_token")
                if token:
                    expiry = data.get("expiry_date", 0)
                    if expiry > 0 and time.time() * 1000 > expiry - 60_000:
                        logger.warning(f"Gemini CLI token at {p} is expired. Run 'gemini' CLI to refresh.")
                    else:
                        logger.info(f"Loaded Gemini CLI OAuth token from {p}")
                        return Credentials(token=token)
            except Exception as e:
                logger.warning(f"Failed to read Gemini CLI creds at {p}: {e}")

    # --- Attempt 2: ADC application_default_credentials.json (refresh_token style) ---
    adc_paths = [
        Path(home) / ".config/gcloud/application_default_credentials.json",
        Path("/home/ubuntu/.config/gcloud/application_default_credentials.json"),
        Path("/root/.config/gcloud/application_default_credentials.json"),
        Path("/app/backend/.deer-flow/data/adc_credentials.json"),  # Mounted Docker fallback
    ]
    for p in adc_paths:
        if p.exists():
            try:
                data = json.loads(p.read_text())
                refresh_token = data.get("refresh_token")
                client_id = data.get("client_id", GCLOUD_CLIENT_ID)
                client_secret = data.get("client_secret", GCLOUD_CLIENT_SECRET)
                if refresh_token:
                    # Build credentials WITHOUT quota_project_id to avoid suspended project billing
                    creds = Credentials(
                        token=None,
                        refresh_token=refresh_token,
                        token_uri=GOOGLE_OAUTH_TOKEN_URI,
                        client_id=client_id,
                        client_secret=client_secret,
                    )
                    # Eagerly refresh to get a valid access token
                    try:
                        creds.refresh(Request())
                        logger.info(f"Loaded and refreshed ADC credentials from {p}")
                    except Exception as e:
                        logger.warning(f"ADC token refresh failed from {p}: {e} — will pass creds anyway")
                    return creds
            except Exception as e:
                logger.warning(f"Failed to read ADC creds at {p}: {e}")

    logger.warning("No Gemini CLI token or ADC credentials found.")
    return None


class GeminiCliChatModel(ChatGoogleGenerativeAI):
    """ChatGoogleGenerativeAI variant that uses Gemini CLI OAuth or ADC credentials."""

    @model_validator(mode="before")
    @classmethod
    def load_credentials(cls, data: dict[str, Any]) -> dict[str, Any]:
        creds = load_gemini_cli_credentials()
        if creds:
            data["credentials"] = creds
            logger.info("Loaded Google credentials for model authentication")
            # Remove api_key since we use OAuth credentials
            data.pop("api_key", None)
        else:
            logger.warning("No Google credentials found — falling back to API key if set.")

        # Ensure we don't pass OpenAI-specific kwargs to Google GenAI
        data.pop("base_url", None)

        return data
