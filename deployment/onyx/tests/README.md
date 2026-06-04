# Onyx Test Suite

Comprehensive test suite for Onyx RAG system covering unit tests, integration tests, and end-to-end tests.

---

## Structure

```
deployment/onyx/tests/
├── conftest.py              # Shared fixtures
├── pytest.ini               # Pytest configuration
├── unit/                    # Unit tests (fast, no I/O)
│   ├── test_connector_db.py
│   └── test_document_index.py
├── integration/             # Integration tests
│   └── test_indexing_pipeline.py
└── fixtures/                # Test data
    └── sample_data.py
```

---

## Running Tests

### All Tests

```bash
pytest deployment/onyx/tests/
```

### Unit Tests Only (Fast)

```bash
pytest deployment/onyx/tests/ -m unit
```

### Integration Tests

```bash
pytest deployment/onyx/tests/ -m integration
```

### With Coverage

```bash
pytest deployment/onyx/tests/ --cov=deployment/onyx --cov-report=html
```

### Specific Test File

```bash
pytest deployment/onyx/tests/unit/test_connector_db.py
```

### Specific Test

```bash
pytest deployment/onyx/tests/unit/test_connector_db.py::TestConnectorCreation::test_create_connector_with_valid_data_succeeds
```

---

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
- Fast execution (< 1s per test)
- No external dependencies
- Mock all I/O operations
- Target: 80%+ coverage

**Examples:**
- Connector CRUD operations
- Document chunk conversion
- Embedding generation
- ACL generation

### Integration Tests (`@pytest.mark.integration`)
- Moderate execution (1-10s per test)
- Real database/search engine (test instances)
- Limited external API calls
- Focus on component interactions

**Examples:**
- Full indexing pipeline
- Search with real OpenSearch
- Connector-triggered indexing
- Bulk operations

### End-to-End Tests (`@pytest.mark.e2e`)
- Slower execution (10s-5min per test)
- Real services in test environment
- User-facing scenarios
- Critical path coverage

**Examples:**
- Upload → Index → Search → Retrieve
- Multi-document search
- Cross-connector search

---

## Test Markers

Use markers to categorize and filter tests:

```python
@pytest.mark.unit
def test_fast_unit_test():
    pass

@pytest.mark.integration
@pytest.mark.requires_opensearch
def test_with_opensearch():
    pass

@pytest.mark.e2e
@pytest.mark.slow
def test_full_workflow():
    pass
```

**Available Markers:**
- `unit` - Unit tests (fast, no I/O)
- `integration` - Integration tests (moderate speed)
- `e2e` - End-to-end tests (slow)
- `smoke` - Smoke tests (basic health checks)
- `regression` - Regression tests (prevent known bugs)
- `slow` - Tests that take > 10s
- `requires_onyx` - Requires Onyx service running
- `requires_opensearch` - Requires OpenSearch running
- `requires_network` - Requires network access

---

## Fixtures

### Common Fixtures (from conftest.py)

```python
def test_example(sample_document, sample_chunks, sample_embedding):
    """Use fixtures in your tests."""
    assert sample_document["document_id"] == "test_doc_001"
    assert len(sample_chunks) == 2
    assert len(sample_embedding) == 1536
```

**Available Fixtures:**
- `sample_document` - Sample document for testing
- `sample_chunks` - Sample document chunks
- `sample_embedding` - Sample 1536-dim embedding vector
- `mock_opensearch_response` - Mock OpenSearch response
- `sample_connector` - Sample connector configuration
- `sample_persona` - Sample persona configuration
- `sample_search_query` - Sample search query

---

## Writing New Tests

### 1. Choose Test Type

- **Unit Test**: Testing a single function/class
- **Integration Test**: Testing component interaction
- **E2E Test**: Testing full workflow

### 2. Create Test File

```python
"""Tests for my_module.

Brief description of what this module tests.
"""

import pytest
from unittest.mock import Mock, patch


@pytest.mark.unit
class TestMyFeature:
    """Tests for my feature."""

    def test_feature_works(self):
        """Test that feature works as expected."""
        # Arrange
        input_data = "test"

        # Act
        result = my_function(input_data)

        # Assert
        assert result == "expected"
```

### 3. Use AAA Pattern

- **Arrange**: Set up test data
- **Act**: Execute code under test
- **Assert**: Verify outcome

### 4. Add Markers

```python
@pytest.mark.unit
@pytest.mark.regression
def test_bug_fix():
    """Regression test for bug #123."""
    pass
```

---

## Current Status

### Test Coverage

| Component | Unit Tests | Integration Tests | Coverage |
|-----------|-----------|-------------------|----------|
| Connector DB | 20 tests (template) | 3 tests (template) | 0% |
| Document Index | 25 tests (template) | 5 tests (template) | 0% |
| Search | 0 tests | 3 tests (template) | 0% |
| **Total** | **45 tests** | **11 tests** | **0%** |

**Note:** Current tests are templates showing structure. Actual implementation needed.

---

## Implementation Roadmap

### Phase 1: Unit Tests (Week 1-2)

**Priority P0 - Critical Path:**
1. ✅ Test structure created
2. ⏳ Implement connector CRUD tests
3. ⏳ Implement document indexing tests
4. ⏳ Implement embedding tests
5. ⏳ Implement ACL tests

**Target:** 50+ unit tests, 60% coverage

### Phase 2: Integration Tests (Week 3-4)

**Priority P1 - Core Features:**
1. ⏳ Implement indexing pipeline tests
2. ⏳ Implement search flow tests
3. ⏳ Implement connector indexing tests
4. ⏳ Implement bulk operation tests

**Target:** 20+ integration tests, 70% coverage

### Phase 3: E2E Tests (Week 5-6)

**Priority P1 - User Workflows:**
1. ⏳ Implement document lifecycle tests
2. ⏳ Implement multi-document search tests
3. ⏳ Implement cross-connector tests

**Target:** 10+ E2E tests, critical path coverage

---

## Best Practices

### 1. Test Naming

```python
# Good
def test_create_connector_with_valid_data_succeeds():
    pass

# Bad
def test_connector():
    pass
```

### 2. One Assertion Per Test

```python
# Good
def test_connector_has_name():
    connector = create_connector({"name": "Test"})
    assert connector.name == "Test"

def test_connector_has_source():
    connector = create_connector({"source": "file"})
    assert connector.source == "file"

# Avoid
def test_connector():
    connector = create_connector({"name": "Test", "source": "file"})
    assert connector.name == "Test"
    assert connector.source == "file"
    assert connector.disabled is False
```

### 3. Use Fixtures

```python
# Good
def test_with_fixture(sample_document):
    result = process(sample_document)
    assert result is not None

# Avoid
def test_without_fixture():
    document = {"document_id": "test", "content": "..."}
    result = process(document)
    assert result is not None
```

### 4. Mock External Dependencies

```python
@patch('module.external_api_call')
def test_with_mock(mock_api):
    mock_api.return_value = {"status": "ok"}
    result = my_function()
    assert result["status"] == "ok"
```

---

## Troubleshooting

### Issue: Tests Not Discovered

**Solution:**
```bash
# Check pytest can find tests
pytest --collect-only deployment/onyx/tests/
```

### Issue: Import Errors

**Solution:**
```bash
# Add project root to PYTHONPATH
export PYTHONPATH=/home/ubuntu/aisci:$PYTHONPATH
pytest deployment/onyx/tests/
```

### Issue: Fixture Not Found

**Solution:**
- Check fixture is defined in `conftest.py`
- Check fixture name matches usage
- Check `conftest.py` is in correct location

---

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Feature Matrix](../../../docs/workflows/feature-matrix.md)
- [Onyx RAG Workflow](../../../docs/workflows/onyx-rag-workflow.md)

---

**Last Updated:** 2026-05-31  
**Status:** Test infrastructure created, implementation pending  
**Maintainer:** Platform Operations
