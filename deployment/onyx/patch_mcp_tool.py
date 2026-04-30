from pathlib import Path


MCP_TOOL_PATH = Path("/app/onyx/tools/tool_implementations/mcp/mcp_tool.py")
LITELLM_FACTORY_PATH = Path(
    "/usr/local/lib/python3.11/site-packages/litellm/litellm_core_utils/prompt_templates/factory.py"
)
OPENSEARCH_INDEX_PATH = Path(
    "/app/onyx/document_index/opensearch/opensearch_document_index.py"
)


def patch_mcp_tool_names() -> None:
    text = MCP_TOOL_PATH.read_text()
    if "_build_safe_llm_tool_name" in text:
        return

    import_block = "import json\nfrom typing import Any\n"
    helper_anchor = "    return schema\n\n\nclass MCPTool(Tool[None]):\n"
    original_llm_name = '        self._llm_name = f"mcp:{mcp_server.name}:{tool_name}"\n'
    name_property = "    def name(self) -> str:\n        return self._name\n"
    tool_def_name = '                "name": self._name,\n'

    replacements = (
        (
            import_block,
            "import json\nimport re\nfrom typing import Any\n",
            "MCP tool import block",
        ),
        (
            helper_anchor,
            """    return schema


def _sanitize_tool_name_segment(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_]+", "_", value.strip().lower())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "tool"


def _build_safe_llm_tool_name(server_name: str, tool_name: str, tool_id: int) -> str:
    server_segment = _sanitize_tool_name_segment(server_name)
    tool_segment = _sanitize_tool_name_segment(tool_name)
    llm_name = f"mcp_{tool_id}_{server_segment}_{tool_segment}"
    return llm_name[:64].rstrip("_")


class MCPTool(Tool[None]):
""",
            "MCP tool helper anchor",
        ),
        (
            original_llm_name,
            "        self._llm_name = _build_safe_llm_tool_name(\n"
            "            mcp_server.name, tool_name, tool_id\n"
            "        )\n",
            "MCP llm_name assignment",
        ),
        (
            name_property,
            "    def name(self) -> str:\n        return self._llm_name\n",
            "MCP name property",
        ),
        (
            tool_def_name,
            '                "name": self.name,\n',
            "MCP tool definition name field",
        ),
    )

    for old, new, label in replacements:
        if old not in text:
            raise RuntimeError(f"Unexpected {label}")
        text = text.replace(old, new, 1)

    MCP_TOOL_PATH.write_text(text)


def patch_vertex_gemini_tool_results() -> None:
    text = LITELLM_FACTORY_PATH.read_text()
    marker = "response_data = {\"content\": content_str}  # patched for Vertex/Gemini URL-safe tool responses"
    if marker in text:
        return

    old = """    # Parse response data - support both JSON string and plain string
    # For Computer Use, the response should contain structured data like {"url": "..."}
    response_data: dict
    try:
        if content_str.strip().startswith("{") or content_str.strip().startswith("["):
            # Try to parse as JSON (for Computer Use structured responses)
            parsed = json.loads(content_str)
            if isinstance(parsed, dict):
                response_data = parsed  # Use the parsed JSON directly
            else:
                response_data = {"content": content_str}
        else:
            response_data = {"content": content_str}
    except (json.JSONDecodeError, ValueError):
        # Not valid JSON, wrap in content field
        response_data = {"content": content_str}
"""
    new = """    # Vertex/Gemini rejects some structured tool-response payloads when nested
    # URLs are interpreted as named file references without matching parts.
    # Preserve the exact tool output, but send it as plain text content.
    response_data: dict
    response_data = {"content": content_str}  # patched for Vertex/Gemini URL-safe tool responses
"""
    if old not in text:
        raise RuntimeError("Unexpected LiteLLM Gemini tool response block")
    text = text.replace(old, new, 1)
    LITELLM_FACTORY_PATH.write_text(text)


def patch_opensearch_missing_update_logging() -> None:
    text = OPENSEARCH_INDEX_PATH.read_text()
    marker = "This is likely due to it not having been indexed yet. Skipping update for now... Error: {e!r}\""
    if marker in text:
        return

    old = """        except NotFoundError:
            logger.exception(
                f"Tried to update document {doc_id} but at least one of its chunks was not found in OpenSearch. "
                "This is likely due to it not having been indexed yet. Skipping update for now..."
            )
            return
"""
    new = """        except NotFoundError as e:
            logger.warning(
                f"Tried to update document {doc_id} but at least one of its chunks was not found in OpenSearch. "
                f"This is likely due to it not having been indexed yet. Skipping update for now... Error: {e!r}"
            )
            return
"""
    if old not in text:
        raise RuntimeError("Unexpected OpenSearch missing-update logging block")
    text = text.replace(old, new, 1)
    OPENSEARCH_INDEX_PATH.write_text(text)


if __name__ == "__main__":
    patch_mcp_tool_names()
    patch_vertex_gemini_tool_results()
    patch_opensearch_missing_update_logging()
