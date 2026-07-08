"""
Startup .env Validator
======================
Validates all required and optional API keys at startup with clear, coloured
error messages instead of failing silently mid-research.

Call at application startup:
    from src.env_validator import validate_env
    validate_env()
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Literal


@dataclass
class EnvVar:
    name: str
    level: Literal["required", "warn", "info"]
    description: str
    group: str


ENV_SPEC: list[EnvVar] = [
    EnvVar("TAVILY_API_KEY",    "warn",  "Tavily search (parallel engine 1)",        "search"),
    EnvVar("BRAVE_API_KEY",     "warn",  "Brave search (parallel engine 2)",          "search"),
    EnvVar("SERPER_API_KEY",    "warn",  "Google via Serper (parallel engine 3)",     "search"),
    EnvVar("EXA_API_KEY",       "info",  "Exa neural search (optional engine 4)",     "search"),
    EnvVar("JINA_API_KEY",      "info",  "Jina AI reader / web-fetch",                "search"),
    EnvVar("OPENROUTER_API_KEY", "warn", "OpenRouter LLM gateway",                   "llm"),
    EnvVar("NVIDIA_API_KEY",    "info",  "NVIDIA NIM provider",                       "llm"),
    EnvVar("DASHSCOPE_API_KEY", "info",  "Alibaba DashScope (Qwen models)",           "llm"),
    EnvVar("ONYX_API_KEY",      "info",  "AiSci Onyx LiteLLM proxy",                 "llm"),
    EnvVar("CODEX_API_KEY",     "info",  "Codex CLI authenticated endpoint",          "llm"),
    EnvVar("VECTOR_STORE_BACKEND", "info", "chroma | qdrant | disabled",              "memory"),
    EnvVar("CHROMA_HOST",       "info",  "Chroma host (if backend=chroma)",           "memory"),
    EnvVar("QDRANT_URL",        "info",  "Qdrant URL (if backend=qdrant)",            "memory"),
    EnvVar("TASK_QUEUE_ENABLED", "info", "Enable ARQ async task queue",               "queue"),
    EnvVar("REDIS_URL",         "info",  "Redis URL (required if queue enabled)",     "queue"),
    EnvVar("GITHUB_TOKEN",      "info",  "GitHub MCP server auth token",              "integrations"),
    EnvVar("NOTION_API_KEY",    "info",  "Notion MCP server auth",                   "integrations"),
]


def validate_env(exit_on_required: bool = True) -> bool:
    RESET  = "\033[0m"
    RED    = "\033[31m"
    YELLOW = "\033[33m"
    CYAN   = "\033[36m"
    GREEN  = "\033[32m"

    errors: list[str] = []
    by_group: dict[str, list[EnvVar]] = {}
    for v in ENV_SPEC:
        by_group.setdefault(v.group, []).append(v)

    print(f"\n{CYAN}=== DeerFlow Environment Validation ==={RESET}")
    for group, vars_ in by_group.items():
        print(f"\n  [{group.upper()}]")
        group_present = False
        for v in vars_:
            val = os.getenv(v.name, "")
            present = bool(val and "your-" not in val)
            if present:
                group_present = True
                print(f"  {GREEN}ok{RESET}  {v.name:<32} {v.description}")
            else:
                mark  = "ERR" if v.level == "required" else ("WRN" if v.level == "warn" else "---")
                color = RED   if v.level == "required" else (YELLOW if v.level == "warn" else "")
                print(f"  {color}{mark}{RESET}  {v.name:<32} {v.description}")
                if v.level == "required":
                    errors.append(v.name)

    if errors:
        print(f"\n{RED}ERROR: Missing required vars: {', '.join(errors)}{RESET}")
        print(f"{RED}Copy .env.example to .env and fill in the missing values.{RESET}\n")
        if exit_on_required:
            sys.exit(1)
        return False

    print(f"\n{GREEN}Environment OK.{RESET}\n")
    return True


if __name__ == "__main__":
    validate_env(exit_on_required=False)
