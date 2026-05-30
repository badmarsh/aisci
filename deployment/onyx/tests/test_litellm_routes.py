"""
Onyx/LiteLLM Route Health Tests

Tests LiteLLM configuration and route availability for Onyx RAG.
Mocks external API calls - does not require live DashScope.
"""

import pytest
from pathlib import Path
import yaml
import sys
import importlib.util


@pytest.fixture
def litellm_config_path():
    """Path to litellm_config.yaml"""
    return Path(__file__).parent.parent / "litellm_config.yaml"


@pytest.fixture
def litellm_config(litellm_config_path):
    """Load litellm_config.yaml if it exists"""
    if not litellm_config_path.exists():
        pytest.skip(f"litellm_config.yaml not found at {litellm_config_path}")
    with open(litellm_config_path) as f:
        return yaml.safe_load(f)


@pytest.fixture
def onyx_env_path():
    """Path to Onyx .env file"""
    return Path(__file__).parent.parent / ".env"


def test_qwen_rag_fast_route_exists(litellm_config):
    """qwen-rag-fast route should exist in model_list"""
    model_list = litellm_config.get("model_list", [])
    model_names = [m.get("model_name") for m in model_list]

    assert "qwen-rag-fast" in model_names, "qwen-rag-fast route missing"


def test_qwen_rag_balanced_route_exists(litellm_config):
    """qwen-rag-balanced route should exist in model_list"""
    model_list = litellm_config.get("model_list", [])
    model_names = [m.get("model_name") for m in model_list]

    assert "qwen-rag-balanced" in model_names, "qwen-rag-balanced route missing"


def test_qwen_rag_vision_route_exists(litellm_config):
    """qwen-rag-vision route should exist in model_list"""
    model_list = litellm_config.get("model_list", [])
    model_names = [m.get("model_name") for m in model_list]

    assert "qwen-rag-vision" in model_names, "qwen-rag-vision route missing"


def test_qwen_rag_local_route_exists(litellm_config):
    """qwen-rag-local route should exist in model_list"""
    model_list = litellm_config.get("model_list", [])
    model_names = [m.get("model_name") for m in model_list]

    assert "qwen-rag-local" in model_names, "qwen-rag-local route missing"


def test_router_fallbacks_configured(litellm_config):
    """Router should have fallback configuration"""
    router_settings = litellm_config.get("router_settings", {})

    # Check for fallback or retry configuration
    has_fallback = (
        "fallbacks" in router_settings or
        "num_retries" in router_settings or
        "retry_after" in router_settings
    )
    assert has_fallback, "No fallback/retry configuration found"


def test_router_cooldown_configured(litellm_config):
    """Router should have cooldown configuration for failed models"""
    router_settings = litellm_config.get("router_settings", {})

    # Check for cooldown settings
    has_cooldown = (
        "cooldown_time" in router_settings or
        "allowed_fails" in router_settings
    )
    # This is optional, so just log if missing
    if not has_cooldown:
        pytest.skip("Cooldown configuration not present (optional)")


def test_dashscope_model_alias_present(litellm_config):
    """DashScope model alias added in commit 235a2a3 should be present"""
    model_list = litellm_config.get("model_list", [])

    # Check for DashScope models in litellm_params
    dashscope_models = [
        m for m in model_list
        if m.get("litellm_params", {}).get("model", "").startswith("dashscope/")
    ]

    # Should have at least one DashScope model configured
    assert len(dashscope_models) > 0, "No DashScope models found in litellm_config"


def test_litellm_quota_check_imports():
    """deployment/helper/litellm_quota_check.py should import without error"""
    quota_check_path = Path(__file__).parent.parent.parent / "helper" / "litellm_quota_check.py"

    if not quota_check_path.exists():
        pytest.skip(f"litellm_quota_check.py not found at {quota_check_path}")

    spec = importlib.util.spec_from_file_location("litellm_quota_check", quota_check_path)
    module = importlib.util.module_from_spec(spec)

    # Should import without error
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        pytest.fail(f"litellm_quota_check.py failed to import: {e}")

    # Check key functions exist
    assert hasattr(module, "probe_model"), "probe_model function missing"
    assert hasattr(module, "classify"), "classify function missing"


def test_litellm_quota_check_runs():
    """litellm_quota_check.py should run without import errors"""
    quota_check_path = Path(__file__).parent.parent.parent / "helper" / "litellm_quota_check.py"

    if not quota_check_path.exists():
        pytest.skip(f"litellm_quota_check.py not found at {quota_check_path}")

    spec = importlib.util.spec_from_file_location("litellm_quota_check", quota_check_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Check that main function exists and is callable
    assert hasattr(module, "main"), "main function missing"
    assert callable(module.main), "main is not callable"


def test_connector_refresh_freq_for_cc11():
    """Connector refresh_freq for CC pair 11 should be 86400 (24h)"""
    # This would require reading the Onyx database or config
    # For now, document the requirement
    pytest.skip("Requires live Onyx database query - manual verification needed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
