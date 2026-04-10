import ast
import json
from enum import Enum
from typing import AsyncIterator, Type

import httpx
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.tools import BaseTool
from langchain_openai.chat_models import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel

from research_agent.common.config import mari_config

http_client = httpx.Client(verify=False)
http_async_client = httpx.AsyncClient(verify=False)


def _create_ax_chat_model(
    api_key: str, endpoint: str, serving_name: str, callbacks: list, headers: dict
) -> ChatOpenAI:
    return ChatOpenAI(
        api_key=api_key,
        base_url=endpoint,
        model=serving_name,
        callbacks=callbacks,
        default_headers=headers,
        temperature=0,
        http_client=http_client,
        http_async_client=http_async_client,
    )


def _get_ax_llm_headers(api_key) -> dict[str, str]:
    return {
        "api-key": api_key,
        "Content-Type": "application/json",
    }


_llm_gpt_4o = _create_ax_chat_model(
    api_key=mari_config.LLM_API_KEY,
    endpoint=mari_config.LLM_ENDPOINT,
    serving_name=mari_config.LLM_MODEL_GPT_4o,
    callbacks=[],
    headers=_get_ax_llm_headers(mari_config.LLM_API_KEY),
)


_llm_gpt_4_1 = _create_ax_chat_model(
    api_key=mari_config.LLM_API_KEY,
    endpoint=mari_config.LLM_ENDPOINT,
    serving_name=mari_config.LLM_MODEL_GPT_4_1,
    callbacks=[],
    headers=_get_ax_llm_headers(mari_config.LLM_API_KEY),
)


class LlmClient(Enum):
    llm_gpt_4o = _llm_gpt_4o
    llm_gpt_4_1 = _llm_gpt_4_1

    def __call__(self):
        return self.value


async def ainvoke_llm(
    messages: list[BaseMessage],
    llm_client: LlmClient = LlmClient.llm_gpt_4_1,
    output_type: Type[BaseModel] | None = None,
) -> BaseModel | dict | str:
    """
    LLM 클라이언트와 메시지, 출력 타입을 받아 비동기로 LLM을 호출하고 결과를 반환합니다.

    Args:
        messages (list): LLM에 전달할 메시지 리스트
        llm_client (LlmClient): 사용할 LLM 클라이언트 Enum (기본: llm_gpt_4_1)
        output_type (Type[BaseModel] | None): 출력 모델 타입 (Pydantic BaseModel 등)

    Returns:
        output_type 인스턴스 또는 LLM의 일반 응답 결과
    """
    try:
        llm = llm_client()
        if output_type:
            llm = llm | PydanticOutputParser(pydantic_object=output_type)
        content = await llm.ainvoke(messages)
        if output_type and isinstance(content, str):
            return json.loads(content)
        return content

    except OutputParserException as e:
        if not getattr(e, "llm_output", None):
            raise RuntimeError(f"Empty llm_output: {e}") from e
        try:
            return json.loads(e.llm_output)
        except Exception:
            try:
                return ast.literal_eval(e.llm_output)
            except Exception:
                return e.llm_output
    except Exception as e:
        raise RuntimeError(f"LLM invocation failed: {e}") from e


async def astream_llm(
    messages: list[BaseMessage], llm_client: LlmClient = LlmClient.llm_gpt_4_1
) -> AsyncIterator[str]:
    try:
        llm = llm_client()
        async for chunk in llm.astream(messages):
            if hasattr(chunk, "content") and chunk.content:
                yield chunk.content
            elif isinstance(chunk, str):
                yield chunk

    except Exception as e:
        raise RuntimeError(f"LLM streaming failed: {e}") from e


async def ainvoke_react_agent(
    messages: list[BaseMessage],
    tools: list[BaseTool],
    llm_client: LlmClient = LlmClient.llm_gpt_4_1,
    output_type: Type[BaseModel] | None = None,
) -> dict | str:
    """
    ReAct 에이전트를 비동기로 호출합니다.

    Args:
        messages (list): LLM에 전달할 메시지 리스트
        tools (list): 에이전트에서 사용할 도구 리스트
        llm_client (LlmClient): 사용할 LLM 클라이언트 Enum (기본: llm_gpt_4_1)

    Returns:
        dict | str: 에이전트의 응답 결과
    """

    try:
        model = llm_client()
        agent = create_react_agent(model=model, tools=tools)
        result = await agent.ainvoke({"messages": messages})
        if (
            isinstance(result, dict)
            and "messages" in result
            and isinstance(result["messages"], list)
        ):
            latest_message = result["messages"][-1]
            content = json.loads(latest_message.content)
            return content

    except OutputParserException as e:
        if not getattr(e, "llm_output", None):
            raise RuntimeError(f"Empty llm_output: {e}") from e
        try:
            return json.loads(e.llm_output)
        except Exception:
            return ast.literal_eval(e.llm_output)
    except Exception as e:
        raise RuntimeError(f"ReAct Agent invocation failed: {e}") from e
