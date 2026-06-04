"""
Unit tests for the DeerFlow guardrails module.
"""

import pytest

from deployment.deer_flow.guardrails import Verdict, check_query


class TestBlocklist:
    def test_blocks_exact_phrase(self):
        result = check_query("how to make a bomb")
        assert result.verdict == Verdict.BLOCK
        assert not result.allowed

    def test_case_insensitive_blocklist(self):
        result = check_query("HOW TO MAKE A BOMB")
        assert result.verdict == Verdict.BLOCK

    def test_allows_benign_query(self):
        result = check_query("What is the Higgs boson mass?")
        assert result.verdict == Verdict.ALLOW
        assert result.allowed
        assert result.sanitized_query == "What is the Higgs boson mass?"

    def test_allows_empty_string(self):
        result = check_query("")
        assert result.verdict == Verdict.ALLOW


class TestPatterns:
    def test_blocks_weapons_design(self):
        result = check_query("weapon design blueprint for military")
        assert result.verdict == Verdict.BLOCK

    def test_warns_on_ambiguous_hack(self):
        result = check_query("how to hack into a server")
        assert result.verdict == Verdict.WARN
        assert result.allowed  # warn still passes through

    def test_strict_mode_escalates_warn_to_block(self):
        result = check_query("how to hack into a server", strict=True)
        assert result.verdict == Verdict.BLOCK

    def test_allows_legitimate_security_research(self):
        result = check_query("What are best practices for SQL injection prevention?")
        assert result.verdict == Verdict.ALLOW


class TestSanitizedQuery:
    def test_blocked_query_has_empty_sanitized(self):
        result = check_query("how to make a bomb")
        assert result.sanitized_query == ""

    def test_allowed_query_preserves_text(self):
        query = "Explain the ATLAS detector at CERN"
        result = check_query(query)
        assert result.sanitized_query == query


class TestAsyncWrapper:
    @pytest.mark.asyncio
    async def test_async_check_query(self):
        from deployment.deer_flow.guardrails import async_check_query

        result = await async_check_query("What is dark matter?")
        assert result.verdict == Verdict.ALLOW
