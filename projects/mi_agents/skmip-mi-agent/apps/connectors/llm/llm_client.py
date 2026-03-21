import os
from typing import Any

import httpx
from openai import OpenAI

from apps.common.configs.settings import BaseSettings, get_settings
from apps.common.logging.decorators import log_connector, time_logger
from apps.common.values.enums import ModelPreference


def _resolve_model_name(
    model_name: str | None,
    preference: ModelPreference | None,
) -> str:
    settings: BaseSettings = get_settings()
    if model_name:
        return model_name
    if preference is ModelPreference.QUALITY:
        return settings.deeply_thinking_model_api_deployment_name or settings.model_api_deployment_name
    if preference is ModelPreference.SPEED:
        return settings.lightly_thinking_model_api_deployment_name or settings.model_api_deployment_name
    return settings.model_api_deployment_name


@log_connector
@time_logger
def invoke_llm_function_call(
    messages: list[dict[str, str]],
    model_name: str | None = None,
    *,
    preference: ModelPreference | None = None,
    functions: list | None = None,
    function_call: dict | None = None,
    temperature: float = 0.7,
    max_retries: int = 2,
) -> dict[str, Any]:
    settings: BaseSettings = get_settings()
    client = OpenAI(
        base_url=settings.model_endpoint,
        api_key=settings.api_key,
        http_client=httpx.Client(verify=False, timeout=settings.llm_timeout_sec),
        max_retries=max_retries,
    )
    model = _resolve_model_name(model_name, preference)
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        functions=functions,
        function_call=function_call,
        temperature=temperature,
    )
    choice = resp.choices[0]
    return {
        "id": resp.id,
        "content": choice.message.content,
        "finish_reason": choice.finish_reason,
        "usage": (resp.usage.model_dump() if resp.usage else None),
        "model": model,
    }
