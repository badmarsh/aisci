from pathlib import Path


MCP_TOOL_PATH = Path("/app/onyx/tools/tool_implementations/mcp/mcp_tool.py")
LITELLM_FACTORY_PATH = Path(
    "/usr/local/lib/python3.11/site-packages/litellm/litellm_core_utils/prompt_templates/factory.py"
)
LITELLM_OPENAI_PATH = Path(
    "/usr/local/lib/python3.11/site-packages/litellm/llms/openai/openai.py"
)
MULTI_LLM_PATH = Path("/app/onyx/llm/multi_llm.py")
OPENSEARCH_INDEX_PATH = Path(
    "/app/onyx/document_index/opensearch/opensearch_document_index.py"
)
OPENSEARCH_CLIENT_PATH = Path("/app/onyx/document_index/opensearch/client.py")


def patch_mcp_tool_names() -> None:
    text = MCP_TOOL_PATH.read_text()
    if "_build_safe_llm_tool_name" in text:
        return

    import_block = "import json\nfrom typing import Any\n"
    # craft-latest dropped the schema helper above MCPTool; use the class line as anchor
    helper_anchor = "    return schema\n\n\nclass MCPTool(Tool[None]):\n"
    class_anchor = "\nclass MCPTool(Tool[None]):\n"
    original_llm_name = '        self._llm_name = f"mcp:{mcp_server.name}:{tool_name}"\n'
    name_property = "    def name(self) -> str:\n        return self._name\n"
    tool_def_name = '                "name": self._name,\n'

    helper_funcs = """\n\ndef _sanitize_tool_name_segment(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_]+", "_", value.strip().lower())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "tool"


def _build_safe_llm_tool_name(server_name: str, tool_name: str, tool_id: int) -> str:
    server_segment = _sanitize_tool_name_segment(server_name)
    tool_segment = _sanitize_tool_name_segment(tool_name)
    llm_name = f"mcp_{tool_id}_{server_segment}_{tool_segment}"
    return llm_name[:64].rstrip("_")

"""

    import_replacement = "import json\nimport re\nfrom typing import Any\n"

    # Step 1: always patch the import block
    if import_block not in text:
        raise RuntimeError("Unexpected MCP tool import block")
    text = text.replace(import_block, import_replacement, 1)

    # Step 2: inject helper functions — prefer old anchor, fall back to bare class line
    if helper_anchor in text:
        text = text.replace(
            helper_anchor,
            "    return schema\n" + helper_funcs + "class MCPTool(Tool[None]):\n",
            1,
        )
    elif class_anchor in text:
        text = text.replace(class_anchor, helper_funcs + "class MCPTool(Tool[None]):\n", 1)
    else:
        raise RuntimeError("Cannot find MCPTool class definition to inject helpers")

    # Step 3: patch _llm_name assignment
    if original_llm_name not in text:
        raise RuntimeError("Unexpected MCP llm_name assignment")
    text = text.replace(
        original_llm_name,
        "        self._llm_name = _build_safe_llm_tool_name(\n"
        "            mcp_server.name, tool_name, tool_id\n"
        "        )\n",
        1,
    )

    # Step 4: patch name property (may already return _llm_name in newer images — skip if so)
    if name_property in text:
        text = text.replace(
            name_property,
            "    def name(self) -> str:\n        return self._llm_name\n",
            1,
        )

    # Step 5: patch tool_def name field (may already use self.name — skip if so)
    if tool_def_name in text:
        text = text.replace(tool_def_name, '                "name": self.name,\n', 1)

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


def patch_litellm_empty_tool_payloads() -> None:
    text = LITELLM_OPENAI_PATH.read_text()
    marker = "patched to omit empty tool payloads for OpenAI-compatible endpoints"
    if marker in text:
        return

    old = """        raw_response = None
        try:
            raw_response = openai_client.chat.completions.with_raw_response.create(
                **data, timeout=timeout
            )
"""
    new = """        raw_response = None
        try:
            if data.get("tools") == []:
                data = dict(data)
                data.pop("tools", None)
                data.pop("tool_choice", None)
                # patched to omit empty tool payloads for OpenAI-compatible endpoints

            raw_response = openai_client.chat.completions.with_raw_response.create(
                **data, timeout=timeout
            )
"""
    if old not in text:
        raise RuntimeError("Unexpected LiteLLM OpenAI request block")
    text = text.replace(old, new, 1)
    LITELLM_OPENAI_PATH.write_text(text)


def patch_onyx_empty_tool_kwargs() -> None:
    text = MULTI_LLM_PATH.read_text()
    marker = "Only pass tool-related kwargs when tools are present"
    if marker in text:
        return

    comment_old = "Only pass tool_choice when tools are present — some providers (e.g. Fireworks)"
    comment_new = "Only pass tool-related kwargs when tools are present — some providers"
    rationale_old = "reject requests where tool_choice is explicitly null."
    rationale_new = "reject empty tool arrays or explicit null tool_choice values."
    tool_choice_old = (
        'if tools and tool_choice is not None:\n'
        '                    optional_kwargs["tool_choice"] = tool_choice'
    )
    tool_choice_new = (
        'if tools:\n'
        '                    optional_kwargs["tools"] = tools\n'
        '                    if tool_choice is not None:\n'
        '                        optional_kwargs["tool_choice"] = tool_choice'
    )
    tools_kwarg_old = """                    messages=messages,
                    tools=tools,
                    stream=stream,
"""
    tools_kwarg_new = """                    messages=messages,
                    stream=stream,
"""
    if (
        comment_old not in text
        or rationale_old not in text
        or tool_choice_old not in text
        or tools_kwarg_old not in text
    ):
        return
    text = text.replace(comment_old, comment_new, 1)
    text = text.replace(rationale_old, rationale_new, 1)
    text = text.replace(tool_choice_old, tool_choice_new, 1)
    text = text.replace(tools_kwarg_old, tools_kwarg_new, 1)
    MULTI_LLM_PATH.write_text(text)


def patch_opensearch_missing_update_logging() -> None:
    text = OPENSEARCH_INDEX_PATH.read_text()
    # Already patched?
    if "Skipping update for now... Error:" in text:
        return
    # v4.0.3+ refactored the update method to use typed exceptions
    # (ChunkCountNotFoundError) instead of catching NotFoundError.
    if "except NotFoundError" not in text:
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


def patch_opensearch_search_source_hydration() -> None:
    if "patched to hydrate OpenSearch search sources by id" in OPENSEARCH_CLIENT_PATH.read_text():
        return
    # v4.0.3+ restructured the search method; the _source exclusion
    # workaround is no longer needed because the upstream code
    # does not strip _source from the search body. Skip.
    print("patch_opensearch_search_source_hydration: no longer needed in v4.0.3+")


if __name__ == "__main__":
    patch_mcp_tool_names()
    patch_vertex_gemini_tool_results()
    patch_litellm_empty_tool_payloads()
    patch_onyx_empty_tool_kwargs()
    patch_opensearch_missing_update_logging()
    patch_opensearch_search_source_hydration()
