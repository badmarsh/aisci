# AISCI Test Suite

Comprehensive test suite for the AISCI physics validation platform.

## Quick Start

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-docker pytest-benchmark requests

# Run all tests
pytest

# Run smoke tests only (quick validation)
pytest -m smoke

# Run specific component tests
pytest -m physics
pytest -m onyx
pytest -m deerflow

# Run with coverage
pytest --cov=physics/src --cov-report=html
```

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests
│   ├── physics/            # Physics pipeline unit tests
│   │   └── test_smoke.py   # Quick smoke tests
│   ├── onyx/               # Onyx RAG unit tests
│   │   └── test_smoke.py
│   └── deerflow/           # DeerFlow unit tests
│       └── test_smoke.py
├── integration/            # Integration tests
│   ├── test_agent_run.py
│   ├── test_deerflow_api.py
│   ├── test_rag_fixed.py
│   └── test_rag_queries.py
├── e2e/                    # End-to-end tests
│   └── (to be implemented)
├── performance/            # Performance benchmarks
│   └── (to be implemented)
└── fixtures/               # Test data and mocks
    └── test_data/
```

## Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.smoke` - Quick smoke tests (< 5s each)
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.performance` - Performance benchmarks
- `@pytest.mark.security` - Security tests
- `@pytest.mark.physics` - Physics pipeline tests
- `@pytest.mark.onyx` - Onyx RAG tests
- `@pytest.mark.deerflow` - DeerFlow tests
- `@pytest.mark.skills` - Agent skills tests
- `@pytest.mark.slow` - Slow running tests (> 30s)

## Running Tests

### By Category
```bash
# Smoke tests (fastest)
pytest -m smoke

# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# All tests except slow ones
pytest -m "not slow"
```

### By Component
```bash
# Physics tests
pytest -m physics

# Onyx tests
pytest -m onyx

# DeerFlow tests
pytest -m deerflow

# Skills tests
pytest -m skills
```

### Specific Test Files
```bash
# Run specific file
pytest tests/unit/physics/test_smoke.py

# Run specific test
pytest tests/unit/physics/test_smoke.py::test_imports

# Run with verbose output
pytest -v tests/unit/physics/
```

## Coverage

Generate coverage reports:

```bash
# HTML report (opens in browser)
pytest --cov=physics/src --cov-report=html
open htmlcov/index.html

# Terminal report
pytest --cov=physics/src --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=physics/src --cov-fail-under=70
```

## Prerequisites

### Services Required

Some tests require running services:

**Onyx RAG:**
```bash
cd deployment/onyx
docker compose up -d
```

**DeerFlow:**
```bash
cd deployment/deer-flow
make start
```

**Multica:**
```bash
multica daemon start
```

Tests will skip automatically if services are not running.

## Writing Tests

### Test Structure

```python
import pytest

@pytest.mark.smoke
@pytest.mark.physics
def test_something(test_data_dir):
    """Test description"""
    # Arrange
    data = load_test_data(test_data_dir)
    
    # Act
    result = process_data(data)
    
    # Assert
    assert result is not None
    assert result.status == "success"
```

### Using Fixtures

```python
def test_onyx_search(onyx_url, onyx_client):
    """Test using onyx_client fixture"""
    response = onyx_client.post(
        f"{onyx_url}/api/search",
        json={"query": "test"}
    )
    assert response.status_code == 200
```

### Skipping Tests

```python
@pytest.mark.skipif(not service_available(), reason="Service not running")
def test_requires_service():
    pass

def test_conditional_skip():
    if not prerequisite_met():
        pytest.skip("Prerequisite not met")
```

## CI/CD Integration

Tests run automatically in GitHub Actions:

- **Unit tests:** Every commit
- **Integration tests:** Every PR
- **E2E tests:** Before merge to main
- **Performance tests:** Nightly
- **Security scans:** Weekly

See `.github/workflows/tests.yml` for configuration.

## Test Data

Test fixtures are in `tests/fixtures/test_data/`:

- `physics/` - Physics test data (pT spectra, fit results)
- `onyx/` - RAG test queries and expected results
- `deerflow/` - DeerFlow test scenarios

## Troubleshooting

### Tests Failing

```bash
# Run with verbose output
pytest -vv

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf
```

### Service Connection Issues

```bash
# Check service status
curl http://localhost:8095/health  # Onyx
curl http://localhost:2026/health  # DeerFlow
multica daemon status              # Multica

# View service logs
docker compose logs -f             # Onyx/DeerFlow
tail -f ~/.multica/daemon.log      # Multica
```

### Import Errors

```bash
# Ensure project root in PYTHONPATH
export PYTHONPATH=/home/ubuntu/aisci:$PYTHONPATH

# Or install in development mode
pip install -e .
```

## Related Documentation

- **Test Plan:** `docs/testing/test-plan.md`
- **Audit Report:** `AUDIT_REPORT.md`
- **Multica Issues:** AIS-13 (comprehensive testing)

## Contributing

When adding new tests:

1. Follow existing test structure
2. Add appropriate markers
3. Include docstrings
4. Update this README if adding new categories
5. Ensure tests pass locally before committing

## Status

**Current Coverage:**
- Physics: Smoke tests implemented
- Onyx: Smoke tests implemented
- DeerFlow: Smoke tests implemented
- Skills: Not yet implemented
- Integration: Existing tests moved to tests/integration/
- E2E: Not yet implemented
- Performance: Not yet implemented

**Next Steps:** See Multica issue AIS-13 for full implementation plan.
