"""
Physics Pipeline Smoke Tests

Ensures physics validation scripts import and run without errors.
Does not require fit_input.csv - skips data-dependent tests gracefully.
"""

import pytest
from pathlib import Path
import importlib.util
import sys


@pytest.fixture
def physics_root():
    """Physics module root directory"""
    return Path(__file__).parent.parent


def import_module_from_path(module_name: str, file_path: Path):
    """Import a Python module from a file path"""
    if not file_path.exists():
        pytest.skip(f"{file_path.name} not found at {file_path}")

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_boson_paper_analysis_imports(physics_root):
    """boson_paper_analysis.py should import without error"""
    file_path = physics_root / "boson_paper_analysis.py"
    try:
        module = import_module_from_path("boson_paper_analysis", file_path)
        assert module is not None
    except Exception as e:
        pytest.fail(f"boson_paper_analysis.py failed to import: {e}")


def test_sympy_validation_agent_imports(physics_root):
    """sympy_validation_agent.py should import without error"""
    file_path = physics_root / "sympy_validation_agent.py"
    try:
        module = import_module_from_path("sympy_validation_agent", file_path)
        assert module is not None
    except Exception as e:
        pytest.fail(f"sympy_validation_agent.py failed to import: {e}")


def test_tsallis_physics_validation_imports(physics_root):
    """tsallis_physics_validation.py should import without error"""
    file_path = physics_root / "tsallis_physics_validation.py"
    try:
        module = import_module_from_path("tsallis_physics_validation", file_path)
        assert module is not None
    except Exception as e:
        pytest.fail(f"tsallis_physics_validation.py failed to import: {e}")


def test_fitting_pipeline_imports(physics_root):
    """src/fitting_pipeline.py should import without error"""
    file_path = physics_root / "src" / "fitting_pipeline.py"
    try:
        module = import_module_from_path("fitting_pipeline", file_path)
        assert module is not None
    except Exception as e:
        pytest.fail(f"fitting_pipeline.py failed to import: {e}")


def test_data_loader_imports(physics_root):
    """src/data_loader.py should import without error"""
    file_path = physics_root / "src" / "data_loader.py"
    try:
        module = import_module_from_path("data_loader", file_path)
        assert module is not None
    except Exception as e:
        pytest.fail(f"data_loader.py failed to import: {e}")


def test_sympy_validation_entry_point(physics_root):
    """SymPy validation should have a callable entry point"""
    file_path = physics_root / "sympy_validation_agent.py"
    try:
        module = import_module_from_path("sympy_validation_agent_test", file_path)

        # Look for common entry point patterns
        has_entry_point = (
            hasattr(module, "validate") or
            hasattr(module, "run_validation") or
            hasattr(module, "main") or
            hasattr(module, "check_formula")
        )

        assert has_entry_point, "No validation entry point found"
    except Exception as e:
        pytest.fail(f"Failed to check entry point: {e}")


def test_sympy_validation_returns_result_dict(physics_root):
    """SymPy validation should return a result dict with status and checks"""
    file_path = physics_root / "sympy_validation_agent.py"

    # This test requires a minimal mock input
    # Skip if the module structure doesn't support it
    pytest.skip("Requires mock input structure - manual verification needed")


def test_velocity_subluminal_in_boson_analysis(physics_root):
    """Velocity U should stay subluminal (v < 1c) in boson_paper_analysis"""
    file_path = physics_root / "boson_paper_analysis.py"

    # This test requires running the analysis with parameter grid
    # Skip if fit_input.csv doesn't exist
    fit_input_path = physics_root / "fit_input.csv"
    if not fit_input_path.exists():
        pytest.skip("fit_input.csv not found - skipping data-dependent test")

    # Would need to actually run the analysis and check velocity bounds
    pytest.skip("Requires full analysis run - manual verification needed")


def test_fitting_pipeline_has_main_function(physics_root):
    """fitting_pipeline.py should have a main or run function"""
    file_path = physics_root / "src" / "fitting_pipeline.py"
    try:
        module = import_module_from_path("fitting_pipeline_test", file_path)

        has_main = (
            hasattr(module, "main") or
            hasattr(module, "run") or
            hasattr(module, "run_pipeline") or
            hasattr(module, "fit")
        )

        assert has_main, "No main/run function found in fitting_pipeline"
    except Exception as e:
        pytest.fail(f"Failed to check main function: {e}")


def test_data_loader_has_load_function(physics_root):
    """data_loader.py should have a load or read function"""
    file_path = physics_root / "src" / "data_loader.py"
    try:
        module = import_module_from_path("data_loader_test", file_path)

        has_load = (
            hasattr(module, "load_data") or
            hasattr(module, "load") or
            hasattr(module, "read_data") or
            hasattr(module, "read")
        )

        assert has_load, "No load/read function found in data_loader"
    except Exception as e:
        pytest.fail(f"Failed to check load function: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
