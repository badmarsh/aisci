#!/usr/bin/env python3
"""Monitor model quota status across all providers.

Checks quota/rate-limit status for DashScope, OpenRouter, NVIDIA, and Ollama models.
Alerts when approaching limits and recommends actions.

Usage:
    # Check all providers
    python3 deployment/helper/monitor_model_quotas.py

    # Alert if usage >80%
    python3 deployment/helper/monitor_model_quotas.py --alert-threshold 80

    # Check specific provider
    python3 deployment/helper/monitor_model_quotas.py --provider dashscope
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

import requests


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENV_FILE = REPO_ROOT / "deployment" / "onyx" / ".env"


def load_env_vars(env_file: Path) -> dict[str, str]:
    """Load environment variables from .env file."""
    env_vars = {}

    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                env_vars[key] = value

    # Override with actual environment variables
    for key in ["DASHSCOPE_API_KEY", "OPENROUTER_API_KEY", "NVIDIA_API_KEY"]:
        if key in os.environ:
            env_vars[key] = os.environ[key]

    return env_vars


def check_dashscope_quota(api_key: str) -> dict[str, Any]:
    """Check DashScope quota status."""
    if not api_key or api_key == "your-dashscope-key-here":
        return {
            "provider": "DashScope",
            "status": "not_configured",
            "message": "API key not configured",
        }

    try:
        # Test with a minimal request
        resp = requests.post(
            "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "qwen3.5-omni-flash",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1,
            },
            timeout=10,
        )

        if resp.status_code == 200:
            return {
                "provider": "DashScope",
                "status": "ok",
                "message": "Quota available",
            }
        elif resp.status_code == 429:
            return {
                "provider": "DashScope",
                "status": "rate_limited",
                "message": "Rate limit exceeded - quota exhausted",
                "recommendation": "Switch to paid tier or use local fallback",
            }
        elif resp.status_code == 403:
            return {
                "provider": "DashScope",
                "status": "quota_exhausted",
                "message": "Quota exhausted",
                "recommendation": "Upgrade to paid tier or wait for reset",
            }
        else:
            return {
                "provider": "DashScope",
                "status": "error",
                "message": f"HTTP {resp.status_code}: {resp.text[:200]}",
            }
    except requests.RequestException as exc:
        return {
            "provider": "DashScope",
            "status": "error",
            "message": f"{type(exc).__name__}: {exc}",
        }


def check_openrouter_quota(api_key: str) -> dict[str, Any]:
    """Check OpenRouter quota/credits."""
    if not api_key or api_key == "your-openrouter-key-here":
        return {
            "provider": "OpenRouter",
            "status": "not_configured",
            "message": "API key not configured",
        }

    try:
        # Check credits via API
        resp = requests.get(
            "https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )

        if resp.status_code == 200:
            data = resp.json().get("data", {})
            limit = data.get("limit")
            usage = data.get("usage")

            if limit and usage is not None:
                remaining = limit - usage
                percent_used = (usage / limit) * 100 if limit > 0 else 0

                status = "ok"
                if percent_used > 90:
                    status = "warning"
                elif percent_used > 80:
                    status = "caution"

                return {
                    "provider": "OpenRouter",
                    "status": status,
                    "message": f"${remaining:.2f} remaining (${usage:.2f}/${limit:.2f} used)",
                    "usage_percent": percent_used,
                }
            else:
                return {
                    "provider": "OpenRouter",
                    "status": "ok",
                    "message": "No usage limits (pay-as-you-go)",
                }
        elif resp.status_code == 401:
            return {
                "provider": "OpenRouter",
                "status": "auth_error",
                "message": "Invalid API key",
            }
        else:
            return {
                "provider": "OpenRouter",
                "status": "error",
                "message": f"HTTP {resp.status_code}",
            }
    except requests.RequestException as exc:
        return {
            "provider": "OpenRouter",
            "status": "error",
            "message": f"{type(exc).__name__}: {exc}",
        }


def check_nvidia_quota(api_key: str) -> dict[str, Any]:
    """Check NVIDIA NIM quota status."""
    if not api_key or api_key == "your-nvidia-key-here":
        return {
            "provider": "NVIDIA",
            "status": "not_configured",
            "message": "API key not configured",
        }

    try:
        # Test with a minimal request
        resp = requests.post(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "meta/llama-3.1-8b-instruct",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1,
            },
            timeout=10,
        )

        if resp.status_code == 200:
            return {
                "provider": "NVIDIA",
                "status": "ok",
                "message": "Quota available",
            }
        elif resp.status_code == 429:
            return {
                "provider": "NVIDIA",
                "status": "rate_limited",
                "message": "Rate limit exceeded",
                "recommendation": "Wait for cooldown or reduce request rate",
            }
        elif resp.status_code == 401:
            return {
                "provider": "NVIDIA",
                "status": "auth_error",
                "message": "Invalid API key",
            }
        else:
            return {
                "provider": "NVIDIA",
                "status": "error",
                "message": f"HTTP {resp.status_code}",
            }
    except requests.RequestException as exc:
        return {
            "provider": "NVIDIA",
            "status": "error",
            "message": f"{type(exc).__name__}: {exc}",
        }


def check_ollama_status() -> dict[str, Any]:
    """Check Ollama local models availability."""
    try:
        # Try onyx-ollama container first (via docker network)
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)

        if resp.status_code == 200:
            models = resp.json().get("models", [])
            model_names = [m.get("name", "") for m in models]

            # Just report what's available - don't enforce specific models
            # since different deployments may have different model sets
            if len(model_names) > 0:
                return {
                    "provider": "Ollama",
                    "status": "ok",
                    "message": f"{len(model_names)} models available",
                }
            else:
                return {
                    "provider": "Ollama",
                    "status": "warning",
                    "message": "No models found",
                    "recommendation": "Pull required models: docker exec onyx-ollama ollama pull gemma2:27b",
                }
        else:
            return {
                "provider": "Ollama",
                "status": "error",
                "message": f"HTTP {resp.status_code}",
            }
    except requests.RequestException as exc:
        return {
            "provider": "Ollama",
            "status": "unavailable",
            "message": f"Ollama not reachable: {type(exc).__name__}",
            "recommendation": "Check if onyx-ollama container is running",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--env-file",
        default=str(DEFAULT_ENV_FILE),
        help="Path to .env file with API keys",
    )
    parser.add_argument(
        "--provider",
        choices=["dashscope", "openrouter", "nvidia", "ollama", "all"],
        default="all",
        help="Check specific provider only",
    )
    parser.add_argument(
        "--alert-threshold",
        type=int,
        default=None,
        help="Alert if usage exceeds this percentage (e.g., 80)",
    )
    args = parser.parse_args()

    env_vars = load_env_vars(Path(args.env_file))

    print("Checking model quota status...\n")

    results = []

    # Check each provider
    if args.provider in ("dashscope", "all"):
        result = check_dashscope_quota(env_vars.get("DASHSCOPE_API_KEY", ""))
        results.append(result)

    if args.provider in ("openrouter", "all"):
        result = check_openrouter_quota(env_vars.get("OPENROUTER_API_KEY", ""))
        results.append(result)

    if args.provider in ("nvidia", "all"):
        result = check_nvidia_quota(env_vars.get("NVIDIA_API_KEY", ""))
        results.append(result)

    if args.provider in ("ollama", "all"):
        result = check_ollama_status()
        results.append(result)

    # Display results
    has_issues = False
    for result in results:
        provider = result["provider"]
        status = result["status"]
        message = result["message"]

        # Status emoji
        if status == "ok":
            emoji = "✅"
        elif status in ("warning", "caution"):
            emoji = "⚠️"
            has_issues = True
        elif status in ("rate_limited", "quota_exhausted"):
            emoji = "❌"
            has_issues = True
        elif status == "not_configured":
            emoji = "⚪"
        else:
            emoji = "❌"
            has_issues = True

        print(f"{emoji} {provider}: {message}")

        # Show recommendation if present
        if "recommendation" in result:
            print(f"   → {result['recommendation']}")

        # Alert on threshold
        if args.alert_threshold and "usage_percent" in result:
            if result["usage_percent"] > args.alert_threshold:
                print(f"   ⚠️  ALERT: Usage {result['usage_percent']:.1f}% exceeds threshold {args.alert_threshold}%")
                has_issues = True

        # Show missing models
        if "missing_models" in result:
            for model in result["missing_models"]:
                print(f"   - Missing: {model}")

    print()

    if has_issues:
        print("⚠️  Issues detected - review recommendations above")
        return 1
    else:
        print("✅ All providers operational")
        return 0


if __name__ == "__main__":
    sys.exit(main())
