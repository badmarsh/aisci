"""
Onyx RAG Smoke Tests
Quick validation that Onyx is accessible and responding
"""

import pytest
import requests


@pytest.mark.smoke
@pytest.mark.onyx
def test_onyx_health(onyx_url, onyx_client):
    """Test that Onyx health endpoint responds"""
    try:
        response = onyx_client.get(f"{onyx_url}/health", timeout=5)
        assert response.status_code == 200, f"Onyx health check failed: {response.status_code}"
    except requests.exceptions.ConnectionError:
        pytest.skip("Onyx not running - start with: cd deployment/onyx && docker compose up -d")


@pytest.mark.smoke
@pytest.mark.onyx
def test_onyx_api_accessible(onyx_url, onyx_client):
    """Test that Onyx API is accessible"""
    try:
        response = onyx_client.get(f"{onyx_url}/manage/admin/connector", timeout=5)
        # May return 401 if not authenticated, but should not be connection error
        assert response.status_code in [200, 401, 403], f"Unexpected status: {response.status_code}"
    except requests.exceptions.ConnectionError:
        pytest.skip("Onyx not running")


@pytest.mark.smoke
@pytest.mark.onyx
def test_onyx_search_endpoint_exists(onyx_url, onyx_client):
    """Test that Onyx search endpoint exists"""
    try:
        # This will likely fail auth, but endpoint should exist
        response = onyx_client.post(
            f"{onyx_url}/query/stream-query-validation",
            json={"query": "test"},
            timeout=5
        )
        # Accept any response that's not a connection error
        assert response.status_code < 500, f"Server error: {response.status_code}"
    except requests.exceptions.ConnectionError:
        pytest.skip("Onyx not running")
