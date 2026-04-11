import ast
import json
from enum import Enum
from typing import AsyncIterator, Type

import httpx
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel

from <%project_name%>.common.config import mari_config
from src.utils.connectors.llm.llm_client import get_langchain_chat_model

http_client = httpx.Client(verify=False)
http_async_client = httpx.AsyncClient(verify=False)


def _create_ax_chat_model(model_name: str) -> any:
    # Use framework's get_langchain_chat_model for proper provider support
    return get_langchain_chat_model(model_name=model_name, settings=mari_config)


_llm_gpt_4o = _create_ax_chat_model(mari_config.LLM_MODEL_GPT_4o)
_llm_gpt_4_1 = _create_ax_chat_model(mari_config.LLM_MODEL_GPT_4_1)


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
    """
    try:
        llm = llm_client()

        # Gemini-specific fix: Ensure at least one HumanMessage exists
        if mari_config.llm_provider.lower() in ["gemini", "google"]:
            has_human = any(isinstance(m, HumanMessage) for m in messages)
            if not has_human:
                if len(messages) == 1 and isinstance(messages[0], SystemMessage):
                    # Convert single SystemMessage to HumanMessage
                    messages = [HumanMessage(content=messages[0].content)]
                else:
                    # Append empty HumanMessage
                    messages.append(HumanMessage(content="Please proceed."))

        if output_type:
            # Use native structured output if available, else fallback to parser
            try:
                llm = llm.with_structured_output(output_type)
            except Exception:
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

        # Gemini-specific fix: Ensure at least one HumanMessage exists
        if mari_config.llm_provider.lower() in ["gemini", "google"]:
            has_human = any(isinstance(m, HumanMessage) for m in messages)
            if not has_human:
                if len(messages) == 1 and isinstance(messages[0], SystemMessage):
                    messages = [HumanMessage(content=messages[0].content)]
                else:
                    messages.append(HumanMessage(content="Please proceed."))

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
