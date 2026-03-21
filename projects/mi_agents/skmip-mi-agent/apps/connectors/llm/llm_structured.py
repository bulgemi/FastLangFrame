# llm_structured.py
import os

import httpx
from langchain_openai import ChatOpenAI
from pydantic import BaseModel


def _httpx_client(*, verify: bool = True, timeout: float = 30.0) -> httpx.Client:
    return httpx.Client(verify=verify, timeout=timeout)


def _resolve_model_name(explicit: str | None) -> str:
    # 명시 모델이 있으면 우선, 없으면 환경변수 사용
    return explicit or os.getenv("MODEL_API_DEPLOYMENT_NAME") or "gpt-4o"


def build_chat_with_structured_output(
    schema: type[BaseModel],
    *,
    model_name: str | None = None,
    temperature: float = 0.0,
    max_retries: int = 2,
    verify_tls: bool = True,
):
    """LangChain ChatOpenAI에 with_structured_output 적용한 Runnable을 반환."""
    chat = ChatOpenAI(
        model=_resolve_model_name(model_name),
        base_url=os.getenv("MODEL_ENDPOINT"),
        api_key=os.getenv("MODEL_API_KEY"),
        temperature=temperature,
        max_retries=max_retries,
        http_client=_httpx_client(verify=verify_tls),
    )
    return chat.with_structured_output(schema)


# gpt4o = build_chat_with_structured_output(TimeSeriesResult)
