"""
DeerFlow Input Guardrails
==========================
Filters harmful or policy-violating research requests before they reach
the planner / coordinator.

Design
------
The guard runs in two passes:
1. Fast regex/keyword blocklist  — synchronous, near-zero latency
2. Optional LLM-based classifier — async, only invoked when pass-1 is
   ambiguous or when ``strict=True`` is set in the config.

Extend the BLOCKLIST and SENSITIVE_PATTERNS below for your threat model.
For production, replace the LLM classifier stub with NeMo Guardrails or
Llama Guard.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

class Verdict(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    WARN = "warn"  # allow but flag for review


@dataclass
class GuardResult:
    verdict: Verdict
    reason: str = ""
    matched_rule: str = ""
    original_query: str = ""
    sanitized_query: str = ""

    @property
    def allowed(self) -> bool:
        return self.verdict != Verdict.BLOCK


# ---------------------------------------------------------------------------
# Blocklist & pattern rules
# ---------------------------------------------------------------------------

# Exact-match phrases (lowercase).  Add more as needed.
BLOCKLIST: list[str] = [
    "how to make a bomb",
    "synthesize nerve agent",
    "create malware",
    "child sexual",
    "csam",
]

# Regex patterns (case-insensitive).  Groups are used for context in logs only.
SENSITIVE_PATTERNS: list[tuple[str, str, Verdict]] = [
    # (pattern, rule_name, verdict)
    (r"\b(weapon|explosive|bomb|ied)\s+(design|blueprint|schematic)", "weapons_design", Verdict.BLOCK),
    (r"\b(ransomware|rootkit|keylogger|trojan)\s+(source\s+code|how\s+to|tutorial)", "malware_tutorial", Verdict.BLOCK),
    (r"\b(dox|doxxing|personal\s+address)\s+(of|for)\b", "doxxing", Verdict.BLOCK),
    (r"\b(hack|crack|bypass)\s+(into|the)\s+\w+", "unauthorized_access", Verdict.WARN),
    (r"\b(suicide|self.harm)\s+(method|instructions|how\s+to)", "self_harm", Verdict.BLOCK),
]

_compiled_patterns = [
    (re.compile(pat, re.IGNORECASE | re.UNICODE), name, verdict)
    for pat, name, verdict in SENSITIVE_PATTERNS
]


# ---------------------------------------------------------------------------
# Guard function
# ---------------------------------------------------------------------------

def check_query(query: str, *, strict: bool = False) -> GuardResult:
    """
    Check a research query against the guardrails.

    Args:
        query:  The raw user query string.
        strict: If True, any WARN verdict is escalated to BLOCK.

    Returns:
        GuardResult with verdict, reason, and sanitized query.
    """
    q_lower = query.lower().strip()

    # Pass 1: exact blocklist
    for phrase in BLOCKLIST:
        if phrase in q_lower:
            logger.warning("[guardrails] BLOCKED query matched blocklist phrase %r", phrase)
            return GuardResult(
                verdict=Verdict.BLOCK,
                reason="Query matched a blocked phrase.",
                matched_rule=f"blocklist:{phrase}",
                original_query=query,
                sanitized_query="",
            )

    # Pass 2: regex patterns
    for pattern, rule_name, verdict in _compiled_patterns:
        match = pattern.search(query)
        if match:
            effective_verdict = Verdict.BLOCK if (strict and verdict == Verdict.WARN) else verdict
            if effective_verdict == Verdict.BLOCK:
                logger.warning(
                    "[guardrails] BLOCKED query matched pattern %r at %r",
                    rule_name, match.group(0)
                )
                return GuardResult(
                    verdict=Verdict.BLOCK,
                    reason=f"Query matched security pattern: {rule_name}.",
                    matched_rule=rule_name,
                    original_query=query,
                    sanitized_query="",
                )
            else:
                logger.info("[guardrails] WARN query matched pattern %r", rule_name)
                return GuardResult(
                    verdict=Verdict.WARN,
                    reason=f"Query may require additional review: {rule_name}.",
                    matched_rule=rule_name,
                    original_query=query,
                    sanitized_query=query,  # pass through with warning
                )

    return GuardResult(
        verdict=Verdict.ALLOW,
        reason="",
        original_query=query,
        sanitized_query=query,
    )


# ---------------------------------------------------------------------------
# Async wrapper (for use in async FastAPI endpoints)
# ---------------------------------------------------------------------------

async def async_check_query(query: str, *, strict: bool = False) -> GuardResult:
    """
    Async-compatible wrapper around check_query.
    If you later integrate NeMo Guardrails or Llama Guard (which are async),
    replace the body of this function with the async classifier call.
    """
    return check_query(query, strict=strict)


# ---------------------------------------------------------------------------
# LLM-based classifier stub (TODO: integrate NeMo Guardrails or Llama Guard)
# ---------------------------------------------------------------------------

async def llm_classify_query(
    query: str,
    *,
    model_name: str | None = None,
) -> GuardResult:
    """
    Stub for LLM-based content classification.

    TODO: replace with NeMo Guardrails or Llama Guard:
    - NeMo Guardrails: https://github.com/NVIDIA/NeMo-Guardrails
    - Llama Guard:     https://ai.meta.com/research/publications/llama-guard/

    Example NeMo Guardrails integration::

        from nemoguardrails import LLMRails, RailsConfig
        config = RailsConfig.from_path("./guardrails/nemo_config")
        rails = LLMRails(config)
        response = await rails.generate_async(messages=[{"role": "user", "content": query}])
        # parse response for block/allow signal
    """
    logger.debug("[guardrails] LLM classifier called (stub) for query %r", query[:60])
    # Fall back to fast check until LLM classifier is wired up
    return check_query(query)
