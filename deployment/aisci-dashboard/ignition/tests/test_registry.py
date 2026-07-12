import os
import pytest
from project_registry import ProjectRegistry, ProjectSpec

def test_registry_loads_robert_project():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    registry_file = os.path.join(repo_root, "research", "projects.toml")
    registry = ProjectRegistry(registry_file)

    spec = registry.get_project("robert-boson-manuscript")
    assert spec is not None
    assert spec.owner == "Robert"
    assert "evidence" in spec.capabilities

def test_project_spec_path_containment():
    # Should be valid
    spec = ProjectSpec(
        id="test-project",
        title="Test",
        owner="Test",
        research_type="test",
        root="research/test",
        sensitivity="private",
        capabilities=[]
    )
    assert "test" in spec.get_absolute_root()

def test_project_spec_escapes_repo():
    with pytest.raises(ValueError, match="escapes repository root"):
        ProjectSpec(
            id="test-project",
            title="Test",
            owner="Test",
            research_type="test",
            root="../../etc/passwd",
            sensitivity="private",
            capabilities=[]
        )
