"""
DeerFlow Smoke Tests
Quick validation that DeerFlow is accessible and responding
"""

import pytest
import requests


@pytest.mark.smoke
@pytest.mark.deerflow
def test_deerflow_health(deerflow_url, deerflow_client):
    """Test that DeerFlow health endpoint responds"""
    try:
        response = deerflow_client.get(f"{deerflow_url}/health", timeout=5)
        assert response.status_code == 200, f"DeerFlow health check failed: {response.status_code}"

        data = response.json()
        assert "status" in data, "Health response missing status field"
        assert data["status"] == "healthy", f"DeerFlow not healthy: {data}"
    except requests.exceptions.ConnectionError:
        pytest.skip("DeerFlow not running - start with: cd deployment/deer-flow && make start")


@pytest.mark.smoke
@pytest.mark.deerflow
def test_deerflow_api_accessible(deerflow_url, deerflow_client):
    """Test that DeerFlow API is accessible"""
    try:
        response = deerflow_client.get(f"{deerflow_url}/api/v1/health", timeout=5)
        # May return 404 if endpoint doesn't exist, but should not be connection error
        assert response.status_code < 500, f"Server error: {response.status_code}"
    except requests.exceptions.ConnectionError:
        pytest.skip("DeerFlow not running")


@pytest.mark.smoke
@pytest.mark.deerflow
def test_deerflow_gateway_running(deerflow_url):
    """Test that DeerFlow gateway is running"""
    try:
        response = requests.get(f"{deerflow_url}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert data["service"] == "deer-flow-gateway"
    except requests.exceptions.ConnectionError:
        pytest.skip("DeerFlow not running")
