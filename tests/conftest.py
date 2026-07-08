"""
AISCI Test Suite Configuration
pytest configuration for comprehensive testing
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "physics" / "src"))

# Markers for test categorization
def pytest_configure(config):
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "performance: Performance benchmarks")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "smoke: Quick smoke tests")
    config.addinivalue_line("markers", "physics: Physics pipeline tests")
    config.addinivalue_line("markers", "onyx: Onyx RAG tests")
    config.addinivalue_line("markers", "deerflow: DeerFlow orchestration tests")
    config.addinivalue_line("markers", "skills: Agent skills tests")
    config.addinivalue_line("markers", "slow: Slow running tests")

# Fixtures
import pytest
try:
    import requests
except ImportError:
    requests = None

@pytest.fixture(scope="session")
def onyx_url():
    """Onyx RAG API endpoint"""
    return os.getenv("ONYX_URL", "http://localhost:3000/api")

@pytest.fixture(scope="session")
def deerflow_url():
    """DeerFlow API endpoint"""
    return os.getenv("DEERFLOW_URL", "http://localhost:2026")

@pytest.fixture(scope="session")
def multica_url():
    """Multica API endpoint"""
    return os.getenv("MULTICA_URL", "http://localhost:8100")

@pytest.fixture
def onyx_client(onyx_url):
    """HTTP client for Onyx API"""
    if requests is None:
        pytest.skip("requests library is not installed")
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture
def deerflow_client(deerflow_url):
    """HTTP client for DeerFlow API"""
    if requests is None:
        pytest.skip("requests library is not installed")
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture(scope="session")
def test_data_dir():
    """Test data directory"""
    return Path(__file__).parent / "fixtures" / "test_data"

@pytest.fixture(scope="session")
def physics_test_data(test_data_dir):
    """Physics test data fixtures"""
    return test_data_dir / "physics"
