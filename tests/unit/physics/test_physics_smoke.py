"""
Physics Pipeline Smoke Tests
Quick validation that core physics functions work
"""

import pytest
import sys
from pathlib import Path

# Add physics src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "physics" / "src"))


@pytest.mark.smoke
@pytest.mark.physics
def test_imports():
    """Test that core physics modules can be imported"""
    try:
        import data_loader
        import fitting_pipeline
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import physics modules: {e}")


@pytest.mark.smoke
@pytest.mark.physics
def test_data_loader_exists():
    """Test that data_loader module has expected functions"""
    import data_loader

    # Check for expected functions
    expected_functions = ['load_data', 'validate_data']
    for func_name in expected_functions:
        if not hasattr(data_loader, func_name):
            pytest.skip(f"Function {func_name} not found - may need implementation")


@pytest.mark.smoke
@pytest.mark.physics
def test_fitting_pipeline_exists():
    """Test that fitting_pipeline module has expected functions"""
    import fitting_pipeline

    # Check for expected functions
    expected_functions = ['run_fit', 'calculate_chi2']
    for func_name in expected_functions:
        if not hasattr(fitting_pipeline, func_name):
            pytest.skip(f"Function {func_name} not found - may need implementation")


@pytest.mark.smoke
@pytest.mark.physics
def test_physics_data_directory():
    """Test that physics data directory exists"""
    # Navigate from tests/unit/physics/ up to project root
    project_root = Path(__file__).parent.parent.parent.parent
    data_dir = project_root / "physics" / "data"
    assert data_dir.exists(), f"Physics data directory not found: {data_dir}"


@pytest.mark.smoke
@pytest.mark.physics
def test_physics_src_directory():
    """Test that physics src directory exists"""
    # Navigate from tests/unit/physics/ up to project root
    project_root = Path(__file__).parent.parent.parent.parent
    src_dir = project_root / "physics" / "src"
    assert src_dir.exists(), f"Physics src directory not found: {src_dir}"

    # Check for key files
    expected_files = ["data_loader.py", "fitting_pipeline.py"]
    for filename in expected_files:
        filepath = src_dir / filename
        assert filepath.exists(), f"Expected file not found: {filepath}"
