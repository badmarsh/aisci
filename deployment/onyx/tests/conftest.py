"""Shared test fixtures for Onyx tests.

Provides common fixtures for database, OpenSearch, models, and test data.
"""

import pytest
from pathlib import Path
from typing import Any, Generator


# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def test_data_dir() -> Path:
    """Return path to test data directory."""
    return TEST_DATA_DIR


@pytest.fixture
def sample_document() -> dict[str, Any]:
    """Sample document for testing."""
    return {
        "document_id": "test_doc_001",
        "title": "Test Document",
        "content": "This is a test document about Blast-Wave fits in heavy ion collisions.",
        "metadata": {
            "author": "Test Author",
            "date": "2026-05-31",
            "source": "test",
        },
    }


@pytest.fixture
def sample_chunks() -> list[dict[str, Any]]:
    """Sample document chunks for testing."""
    return [
        {
            "chunk_id": "test_doc_001_chunk_000",
            "document_id": "test_doc_001",
            "content": "This is a test document about Blast-Wave fits.",
            "chunk_index": 0,
            "metadata": {
                "section": "Introduction",
                "page": 1,
            },
        },
        {
            "chunk_id": "test_doc_001_chunk_001",
            "document_id": "test_doc_001",
            "content": "Blast-Wave fits are used in heavy ion collisions.",
            "chunk_index": 1,
            "metadata": {
                "section": "Methods",
                "page": 2,
            },
        },
    ]


@pytest.fixture
def sample_embedding() -> list[float]:
    """Sample embedding vector for testing."""
    # 1536-dimensional vector (matching Alibaba-NLP model)
    return [0.1] * 1536


@pytest.fixture
def mock_opensearch_response() -> dict[str, Any]:
    """Mock OpenSearch search response."""
    return {
        "hits": {
            "total": {"value": 2},
            "hits": [
                {
                    "_id": "test_doc_001_chunk_000",
                    "_score": 0.95,
                    "_source": {
                        "content": "This is a test document about Blast-Wave fits.",
                        "document_id": "test_doc_001",
                        "metadata": {"section": "Introduction"},
                    },
                },
                {
                    "_id": "test_doc_001_chunk_001",
                    "_score": 0.87,
                    "_source": {
                        "content": "Blast-Wave fits are used in heavy ion collisions.",
                        "document_id": "test_doc_001",
                        "metadata": {"section": "Methods"},
                    },
                },
            ],
        }
    }


@pytest.fixture
def sample_connector() -> dict[str, Any]:
    """Sample connector configuration."""
    return {
        "name": "Test Connector",
        "source": "file",
        "connector_specific_config": {
            "file_locations": ["/tmp/test_docs"],
        },
        "refresh_freq": 3600,
        "disabled": False,
    }


@pytest.fixture
def sample_persona() -> dict[str, Any]:
    """Sample persona configuration."""
    return {
        "name": "Test Persona",
        "description": "Test persona for unit tests",
        "system_prompt": "You are a test assistant.",
        "document_set_ids": [1, 2],
        "tool_ids": [1, 2, 3],
        "llm_model_name": "gemini-flash",
    }


@pytest.fixture
def sample_search_query() -> dict[str, Any]:
    """Sample search query."""
    return {
        "query": "Blast-Wave parameters",
        "persona_id": 2,
        "limit": 5,
        "filters": {
            "document_set_ids": [2],
        },
    }


# Markers for test categorization
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, no I/O)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (moderate speed)"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests (slow)"
    )
    config.addinivalue_line(
        "markers", "smoke: Smoke tests (basic health checks)"
    )
    config.addinivalue_line(
        "markers", "regression: Regression tests (prevent known bugs)"
    )
