import sys, os
sys.path.append("/app/onyx/server")
from onyx.db.engine import get_session_context_manager
from onyx.server.manage.llm.models import LLMProviderUpsertRequest, FullModelVersionResponse
from onyx.db.llm import upsert_llm_provider

request = LLMProviderUpsertRequest(
    name="DashScope",
    provider="dashscope",
    api_key="sk-aaf258f793c14578b719a68e4d6f3403",
    api_base="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    custom_config={},
    is_default_provider=True,
    is_default_vision_provider=False,
    default_model_name="qwen-turbo",
    fast_default_model_name="qwen-turbo",
    model_configurations=[
        FullModelVersionResponse(
            name="qwen-turbo",
            model_name="qwen-turbo",
            display_name="Qwen Turbo",
            is_visible=True,
            max_input_tokens=8192,
            supports_image_input=False
        )
    ]
)

with get_session_context_manager() as session:
    res = upsert_llm_provider(request, session)
    print("Success:", res.id)
