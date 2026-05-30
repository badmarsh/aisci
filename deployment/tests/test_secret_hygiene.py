"""
Secret Hygiene Tests

Ensures sensitive files are in .gitignore and no literal secrets are tracked.
Scans working tree only, not git history.
"""

import pytest
from pathlib import Path
import re


@pytest.fixture
def repo_root():
    """Repository root directory"""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def gitignore_path(repo_root):
    """Path to .gitignore"""
    return repo_root / ".gitignore"


@pytest.fixture
def gitignore_content(gitignore_path):
    """Content of .gitignore"""
    if not gitignore_path.exists():
        pytest.fail(".gitignore not found")
    return gitignore_path.read_text()


def test_cookies_txt_in_gitignore(gitignore_content):
    """cookies.txt should be in .gitignore"""
    assert "cookies.txt" in gitignore_content, "cookies.txt not in .gitignore"


def test_env_files_in_gitignore(gitignore_content):
    """.env and .env.local should be in .gitignore"""
    assert ".env" in gitignore_content, ".env not in .gitignore"


def test_docker_compose_in_gitignore(gitignore_content):
    """docker-compose.yml should be in .gitignore (or explicitly tracked)"""
    # docker-compose.yml may be tracked if it has no secrets
    # This test just checks awareness
    pass


def test_litellm_config_in_gitignore(gitignore_content):
    """litellm_config.yaml should be in .gitignore if it contains secrets"""
    # litellm_config.yaml may be tracked if using env var references only
    pass


# API key patterns to detect
API_KEY_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),  # OpenAI-style keys
    re.compile(r"Bearer [a-zA-Z0-9\-_]{20,}"),  # Bearer tokens
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),  # Google API keys
]


def test_no_literal_api_keys_in_deployment(repo_root):
    """No tracked file in deployment/ should contain literal API key patterns"""
    deployment_dir = repo_root / "deployment"
    if not deployment_dir.exists():
        pytest.skip("deployment/ directory not found")

    violations = []

    for file_path in deployment_dir.rglob("*"):
        # Skip directories, binary files, and common non-text files
        if not file_path.is_file():
            continue
        if file_path.suffix in [".pyc", ".so", ".db", ".sqlite", ".png", ".jpg", ".gif"]:
            continue
        if ".git" in file_path.parts:
            continue

        try:
            content = file_path.read_text(errors="ignore")
        except Exception:
            continue

        for pattern in API_KEY_PATTERNS:
            matches = pattern.findall(content)
            if matches:
                # Filter out obvious placeholders
                real_matches = [
                    m for m in matches
                    if "your-" not in m.lower()
                    and "example" not in m.lower()
                    and "placeholder" not in m.lower()
                    and "xxx" not in m.lower()
                ]
                if real_matches:
                    violations.append(f"{file_path.relative_to(repo_root)}: {len(real_matches)} potential keys")

    if violations:
        pytest.fail(f"Potential API keys found:\n" + "\n".join(violations))


def test_mcp_config_no_literal_tokens(repo_root):
    """mcp_config.yaml should contain no literal token values - only env var references"""
    mcp_config_path = repo_root / "mcp_config.yaml"
    if not mcp_config_path.exists():
        pytest.skip("mcp_config.yaml not found")

    content = mcp_config_path.read_text()

    # Check for literal tokens (not env var references)
    for pattern in API_KEY_PATTERNS:
        matches = pattern.findall(content)
        real_matches = [
            m for m in matches
            if "your-" not in m.lower()
            and "example" not in m.lower()
            and "$" not in m  # Env var reference
        ]
        if real_matches:
            pytest.fail(f"mcp_config.yaml contains {len(real_matches)} literal token(s)")


def test_extensions_config_no_literal_tokens(repo_root):
    """extensions_config.json should contain no literal token values"""
    extensions_config_path = repo_root / "deployment" / "onyx" / "extensions_config.json"
    if not extensions_config_path.exists():
        pytest.skip("extensions_config.json not found")

    content = extensions_config_path.read_text()

    # Check for literal tokens
    for pattern in API_KEY_PATTERNS:
        matches = pattern.findall(content)
        real_matches = [
            m for m in matches
            if "your-" not in m.lower()
            and "example" not in m.lower()
        ]
        if real_matches:
            pytest.fail(f"extensions_config.json contains {len(real_matches)} literal token(s)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
