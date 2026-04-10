"""
LangGraph 워크플로우 기본 노드 클래스 및 주요 입출력 노드 정의 모듈.

이 모듈은 리서치 에이전트의 핵심 노드들을 정의합니다.

주요 내용:
- WorkflowNode: 모든 노드의 추상 기반 클래스.
- ResearchPlannerNode: 연구 계획을 수립하고 작업을 분할하는 노드.
- ResearchSearchNode: 각 연구 작업에 대해 검색(Mock)을 수행하는 노드.
- ResearchSynthesisNode: 검색 결과를 종합하여 최종 리포트를 작성하는 노드.

"""

import asyncio
import functools
import logging
import traceback
from abc import ABC, abstractmethod
from typing import Any, Callable, Generic

from langchain_core.runnables import RunnableConfig
from langgraph.config import get_stream_writer
from langgraph.types import StreamWriter
from pydantic import BaseModel, ConfigDict

from <%project_name%>.common.types.nodes import (
    InputT,
    OutputT,
    ResearchPlannerNodeInput,
    ResearchPlannerNodeOutput,
    ResearchSearchNodeInput,
    ResearchSearchNodeOutput,
    ResearchSynthesisNodeInput,
    ResearchSynthesisNodeOutput,
)
from <%project_name%>.common.types.schemas import (
    StreamData,
    StreamInfo,
    StreamStatus,
)
from <%project_name%>.graph.llms import ainvoke_llm, LlmClient
from <%project_name%>.graph.prompts.prompt_manager import (
    build_formatted_prompts,
)
from <%project_name%>.graph.state import ResearchGraphState

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def workflow_node_handler(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(
        self,
        state: ResearchGraphState,
        config: RunnableConfig | None = None,
        writer: StreamWriter | None = None,
    ) -> ResearchGraphState:
        logger.info(f"Progress: {self.name}")
        self._stream_write_value(writer)

        try:
            return await func(self, state, config, writer)
        except Exception as e:
            logger.error(f"{self.name} failed: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            stream_info = StreamInfo(state=StreamStatus.error, data=StreamData.message)
            self._stream_write_value(writer, stream_info, value=str(e))
            raise

    return wrapper


class WorkflowNode(ABC, BaseModel, Generic[InputT, OutputT]):
    name: str
    description: str
    input_type: type[InputT]
    output_type: type[OutputT]
    model_config = ConfigDict(
        extra="ignore",
        arbitrary_types_allowed=True,
    )

    def validate_output(self, data: Any) -> OutputT:
        return self.output_type.model_validate(data)

    def _stream_write_value(
        self,
        writer: StreamWriter,
        stream_info: StreamInfo = StreamInfo(),
        node_name: str | None = None,
        value: str | None = None,
    ):
        chunk_data = {
            **stream_info.to_dict(),
            "node": node_name or self.name,
            "value": value or self.description,
        }
        writer = writer or get_stream_writer()
        writer(chunk_data)

    @abstractmethod
    async def __call__(
        self,
        state: ResearchGraphState,
        config: RunnableConfig | None = None,
        writer: StreamWriter | None = None,
    ) -> ResearchGraphState:
        pass


class ResearchPlannerNode(
    WorkflowNode[ResearchPlannerNodeInput, ResearchPlannerNodeOutput]
):
    name: str = "ResearchPlannerNode"
    description: str = "Planning research tasks... 📝"
    input_type: type[ResearchPlannerNodeInput] = ResearchPlannerNodeInput
    output_type: type[ResearchPlannerNodeOutput] = ResearchPlannerNodeOutput

    @workflow_node_handler
    async def __call__(
        self,
        state: ResearchGraphState,
        config: RunnableConfig | None = None,
        writer: StreamWriter | None = None,
    ) -> ResearchGraphState:
        prompts = await build_formatted_prompts(
            company_code=state.req_input.company_code,
            node_name=self.name,
            query=state.req_input.query,
            histories=state.req_input.histories,
            output_type=self.output_type,
        )
        llm_response = await ainvoke_llm(
            messages=prompts,
            llm_client=LlmClient.llm_gpt_4o,
            output_type=self.output_type,
        )
        state.planner = self.validate_output(llm_response)
        return state


class ResearchSearchNode(
    WorkflowNode[ResearchSearchNodeInput, ResearchSearchNodeOutput]
):
    name: str = "ResearchSearchNode"
    description: str = "Searching for information... 🔍"
    input_type: type[ResearchSearchNodeInput] = ResearchSearchNodeInput
    output_type: type[ResearchSearchNodeOutput] = ResearchSearchNodeOutput

    @workflow_node_handler
    async def __call__(
        self,
        state: ResearchGraphState,
        config: RunnableConfig | None = None,
        writer: StreamWriter | None = None,
    ) -> ResearchGraphState:
        # Simplified Search Logic: In a real agent, this would call web/doc search tools.
        # Here we mock it by asking LLM to summarize what it knows for each task.
        prompts = await build_formatted_prompts(
            company_code=state.req_input.company_code,
            node_name=self.name,
            tasks=state.planner.research_tasks,
            output_type=self.output_type,
        )
        llm_response = await ainvoke_llm(
            messages=prompts,
            llm_client=LlmClient.llm_gpt_4o,
            output_type=self.output_type,
        )
        state.search = self.validate_output(llm_response)
        return state


class ResearchSynthesisNode(
    WorkflowNode[ResearchSynthesisNodeInput, ResearchSynthesisNodeOutput]
):
    name: str = "ResearchSynthesisNode"
    description: str = "Synthesizing research results... 🧠"
    input_type: type[ResearchSynthesisNodeInput] = ResearchSynthesisNodeInput
    output_type: type[ResearchSynthesisNodeOutput] = ResearchSynthesisNodeOutput

    @workflow_node_handler
    async def __call__(
        self,
        state: ResearchGraphState,
        config: RunnableConfig | None = None,
        writer: StreamWriter | None = None,
    ) -> ResearchGraphState:
        prompts = await build_formatted_prompts(
            company_code=state.req_input.company_code,
            node_name=self.name,
            query=state.req_input.query,
            search_results=state.search.search_results,
            overall_goal=state.planner.overall_goal,
            output_type=self.output_type,
        )
        llm_response = await ainvoke_llm(
            messages=prompts,
            llm_client=LlmClient.llm_gpt_4o,
            output_type=self.output_type,
        )
        state.synthesis = self.validate_output(llm_response)
        return state
