from __future__ import annotations

import json

from deerflow.config.extensions_config import ExtensionsConfig


def test_extensions_config_expands_embedded_env_vars(monkeypatch, tmp_path):
    monkeypatch.setenv("MCP_TOKEN", "token-value")
    config_path = tmp_path / "extensions_config.json"
    config_path.write_text(
        json.dumps(
            {
                "mcpServers": {
                    "example": {
                        "enabled": True,
                        "type": "http",
                        "url": "http://example.invalid/mcp",
                        "headers": {"Authorization": "Bearer $MCP_TOKEN"},
                    }
                },
                "skills": {},
            }
        ),
        encoding="utf-8",
    )

    config = ExtensionsConfig.from_file(str(config_path))

    assert config.mcp_servers["example"].headers["Authorization"] == "Bearer token-value"


def test_extensions_config_expands_file_placeholders(tmp_path):
    token_path = tmp_path / "access_token"
    token_path.write_text("file-token\n", encoding="utf-8")
    config_path = tmp_path / "extensions_config.json"
    config_path.write_text(
        json.dumps(
            {
                "mcpServers": {
                    "example": {
                        "enabled": True,
                        "type": "http",
                        "url": "http://example.invalid/mcp",
                        "headers": {"Authorization": f"Bearer $file:{token_path}"},
                    }
                },
                "skills": {},
            }
        ),
        encoding="utf-8",
    )

    config = ExtensionsConfig.from_file(str(config_path))

    assert config.mcp_servers["example"].headers["Authorization"] == "Bearer file-token"
