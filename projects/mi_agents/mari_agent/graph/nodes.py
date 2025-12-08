"""
LangGraph 워크플로우 기본 노드 클래스 및 주요 입출력 노드 정의 모듈.

이 모듈은 에너지·원자재 데이터 분석 워크플로우의 핵심 노드를 정의합니다.

주요 내용:
- WorkflowNode: 모든 노드의 추상 기반 클래스. 타입 검증, 실행 인터페이스 제공.
- PrepareAxPromptNode: AX MCP 서버에서 프롬프트 리소스를 조회하는 노드.
- RewriteQueryNode: 질의 재작성 및 정규화 노드.
- PlannerNode: 전체 분석 계획을 수립하는 노드.
- DataCollectNode: 데이터 수집 단계(뉴스, DB 등)를 조율하는 노드.
- DataAnalysisNode: 수집된 데이터를 분석·가공하는 노드.

각 노드는 Pydantic 모델 기반의 입력/출력 타입을 사용하며,
비동기 실행 및 상태(state) 관리에 최적화되어 있습니다.

"""

import asyncio
import functools
import logging
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Generic

from langchain_core.runnables import RunnableConfig
from langgraph.config import get_stream_writer
from langgraph.types import StreamWriter
from pydantic import BaseModel, ConfigDict

from mari_agent.common.config import mari_config
from mari_agent.common.mcp import (
    get_ax_mcp_prompt_resources,
)
from mari_agent.common.types.nodes import (
    DataAnalysisNodeInput,
    DataCollectNodeInput,
    DataCollectNodeOutput,
    DataSearchToolNodeOutput,
    DummyOutput,
    InputT,
    OutOfDomainAnswerNodeInput,
    OutputT,
    PlannerNodeInput,
    PlannerNodeOutput,
    PrepareAxPromptNodeInput,
    PrepareAxPromptNodeOutput,
    RewriteQueryNodeInput,
    RewriteQueryNodeOutput,
)
from mari_agent.common.types.schemas import (
    DataBundle,
    Step,
    StreamData,
    StreamInfo,
    StreamStatus,
    ToolCategory,
)
from mari_agent.graph.llms import ainvoke_llm, astream_llm
from mari_agent.graph.prompts.prompt_manager import (
    build_formatted_prompts,
    set_ax_prompt_cache,
)
from mari_agent.graph.states import MariGraphState
from mari_agent.graph.tools.tool_manager import tool_manager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def workflow_node_handler(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(
        self,
        state: MariGraphState,
        config: RunnableConfig | None = None,
        writer: StreamWriter | None = None,
    ) -> MariGraphState:
        logger.info(
            f"[{state.req_input.company_code}][user:{state.req_input.user_num}] progress {self.name}"
        )
        self._stream_write_value(writer)

        try:
            return await func(self, state, config, writer)
        except Exception as e:
            logger.error(f"{self.name} failed: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")

            stream_info = StreamInfo(state=StreamStatus.error, data=StreamData.message)
            self._stream_write_value(writer, stream_info, value=str(e))

            raise  # 예외 재발생 → 그래프 중단!

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
        state: MariGraphState,
        config: RunnableConfig | None = None,
        writer: StreamWriter | None = None,
    ) -> MariGraphState:
        pass


class PrepareAxPromptNode(
    WorkflowNode[PrepareAxPromptNodeInput, PrepareAxPromptNodeOutput]
):
    """
    AX MCP 서버에서 프롬프트 리소스를 조회하여 캐시에 저장하는 노드.
    """

    name: str = "PrepareAxPromptNode"
    description: str = "Preparing prompt resources for analysis... 🛠️"
    input_type: type[PrepareAxPromptNodeInput] = PrepareAxPromptNodeInput
    output_type: type[PrepareAxPromptNodeOutput] = PrepareAxPromptNodeOutput

    def __init__(self, **data):
        super().__init__(**data)

    @workflow_node_handler
    async def __call__(
        self,
        state: MariGraphState,
        config: RunnableConfig | None = None,
        writer: StreamWriter | None = None,
    ) -> MariGraphState:
        if not mari_config.AX_MCP_PROMPT_ENABLED:
            return state

        input_data = self.input_type(**state.req_input.model_dump())
        output = await get_ax_mcp_prompt_resources(input_data.prompt_group)
        prompts = {prompt.id: prompt for prompt in output}
        set_ax_prompt_cache(prompts)
        return state


class RewriteQueryNode(WorkflowNode[RewriteQueryNodeInput, RewriteQueryNodeOutput]):
    name: str = "RewriteQueryNode"
    description: str = "Understanding query intent clearly... ✍️"
    input_type: type = RewriteQueryNodeInput
    output_type: type = RewriteQueryNodeOutput

    @workflow_node_handler
    async def __call__(
        self,
        state: MariGraphState,
        config: RunnableConfig | None = None,
        writer: StreamWriter | None = None,
    ) -> MariGraphState:
        # ToDo LTM 추가
        input_data = self.input_type(
            **state.req_input.model_dump(),
            base_date=datetime.now().strftime("%Y-%m-%d"),
        )
        messages = await build_formatted_prompts(
            company_code=state.req_input.company_code,
            node_name=self.name,
            output_type=self.output_type,
            **input_data.model_dump(),
        )

        output = await ainvoke_llm(
            messages=messages,
            output_type=self.output_type,
        )
        output = self.validate_output(output)
        logger.info(
            f"[{state.req_input.company_code}][user:{state.req_input.user_num}]\n- query: {input_data.query},\n- rewritten query: {output.rewritten_query},\n- objective: {output.objective}, \n- period queries: "
        )
        for period_query in output.period_queries:
            logger.info(f"\n  -- {period_query}")
        updated_state = state.model_copy()
        updated_state.rewrite_query = output
        return updated_state


class PlannerNode(WorkflowNode[PlannerNodeInput, PlannerNodeOutput]):
    name: str = "PlannerNode"
    description: str = "️Planning analysis with optimized data and methods... 🗺️"
    input_type: type = PlannerNodeInput
    output_type: type = PlannerNodeOutput

    @workflow_node_handler
    async def __call__(
        self,
        state: MariGraphState,
        config: RunnableConfig | None = None,
        writer: StreamWriter | None = None,
    ) -> MariGraphState:
        input_data = self.input_type(
            **state.rewrite_query.model_dump(),
            query=state.req_input.query,
            collect_tools_desc=tool_manager.get_description(ToolCategory.data_search),
            analysis_tools_desc=tool_manager.get_description(
                ToolCategory.data_analysis
            ),
        )
        messages = await build_formatted_prompts(
            company_code=state.req_input.company_code,
            node_name=self.name,
            output_type=self.output_type,
            **input_data.model_dump(),
        )

        output = await ainvoke_llm(
            messages=messages,
            output_type=self.output_type,
        )
        output = self.validate_output(output)
        updated_state = state.model_copy()
        updated_state.planner = output
        return updated_state


class DataCollectNode(WorkflowNode[DataCollectNodeInput, DataCollectNodeOutput]):
    name: str = "DataCollectNode"
    description: str = "Rapidly collecting key data for analysis... 🔍"
    input_type: type = DataCollectNodeInput
    output_type: type = DataCollectNodeOutput

    @workflow_node_handler
    async def __call__(
        self,
        state: MariGraphState,
        config: RunnableConfig | None = None,
        writer: StreamWriter | None = None,
    ) -> MariGraphState:
        input_data = self.input_type(
            **state.planner.model_dump(),
            objective=state.rewrite_query.objective,
        )
        for step in input_data.collect_steps:
            self._stream_write_value(
                writer,
                node_name=step.tool_name,
                value=f"Starting {step.tool_name} data collection...",
            )

        semaphore = asyncio.Semaphore(mari_config.DATA_COLLECT_MAX_CONCURRENT_TASKS)

        async def execute_with_semaphore(step: Step):
            async with semaphore:
                try:
                    return await tool_manager.ainvoke_tool(
                        step.tool_name,
                        step.params,
                        ToolCategory.data_search,
                    )

                except Exception as e:
                    logger.error(f"Tool execution failed: {e}")
                    return DataSearchToolNodeOutput()

        tasks = [execute_with_semaphore(step) for step in input_data.collect_steps]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        web_data, rdb_data, vector_data = [], [], []
        for data in results:
            rdb_data.extend(data.rdb_data)
            vector_data.extend(data.vector_data)
            web_data.extend(data.web_data)

        output = self.output_type(
            data_bundle=DataBundle(
                rdb_data=rdb_data, vector_data=vector_data, web_data=web_data
            )
        )

        logger.info(f"[DataCollectNode] Collected data: {output.data_bundle.summary}")
        updated_state = state.model_copy()
        updated_state.data_collect = output
        return updated_state


class OutOfDomainAnswerNode(WorkflowNode[OutOfDomainAnswerNodeInput, DummyOutput]):
    """
    도메인 외 질의에 대한 답변 생성 노드
    """

    name: str = "OutOfDomainAnswerNode"
    description: str = "generating answer for query... 🌐"
    input_type: type[OutOfDomainAnswerNodeInput] = OutOfDomainAnswerNodeInput
    output_type: type[DummyOutput] = DummyOutput

    @workflow_node_handler
    async def __call__(
        self,
        state: MariGraphState,
        config: RunnableConfig | None = None,
        writer: StreamWriter | None = None,
    ) -> MariGraphState:
        input_data = self.input_type(
            **state.req_input.model_dump(),
            detected_language=state.rewrite_query.detected_language,
            base_date=state.rewrite_query.base_date,
        )
        messages = await build_formatted_prompts(
            company_code=state.req_input.company_code,
            node_name=self.name,
            output_type=self.output_type,
            **input_data.model_dump(),
        )

        full_response = []
        async for chunk in astream_llm(messages=messages):
            if chunk:
                stream_info = StreamInfo(data=StreamData.chunk)
                self._stream_write_value(writer, stream_info, value=chunk)
                full_response.append(chunk)

        output = "".join(full_response)
        logger.info(
            f"[{state.req_input.company_code}][user:{state.req_input.user_num}] Answer: \n{output}"
        )

        stream_info = StreamInfo(state=StreamStatus.complete, data=StreamData.message)
        self._stream_write_value(writer, stream_info, value=output)

        updated_state = state.model_copy()
        updated_state.data_analysis = output
        return updated_state


class DataAnalysisNode(WorkflowNode[DataAnalysisNodeInput, DummyOutput]):
    """
    데이터를 인사이트로 변환하는 노드 - 하이브리드 분석 지원
    """

    name: str = "DataAnalysisNode"
    description: str = "Analyzing collected data to derive insights... 📊"
    input_type: type[DataAnalysisNodeInput] = DataAnalysisNodeInput
    output_type: type[DummyOutput] = DummyOutput

    def __init__(self, **data):
        super().__init__(**data)

        # self.correlation_analyzer = CorrelationAnalyzer()
        # self.similarity_analyzer = SimilarityAnalyzer()
        # self.trend_analyzer = TrendAnalyzer()
        # self.comparison_analyzer = ComparisonAnalyzer()

    async def _perform_statistical_analysis(
        self, data_bundle, comparison_specs
    ) -> dict:
        """
        코드 기반 통계 분석 수행
        """
        analysis_results = {}

        try:
            # 1. 데이터 전처리
            processed_data = self._preprocess_data(data_bundle)

            if not processed_data:
                logger.warning("분석할 데이터가 없습니다.")
                return {}

            logger.info(f"전처리된 데이터: {list(processed_data.keys())}")

            # 2. Comparison 분석 (최우선 - comparison_specs 기반)
            if comparison_specs and self.comparison_analyzer:
                try:
                    comparison_results = await self.comparison_analyzer.analyze(
                        data_bundle=data_bundle, comparison_specs=comparison_specs
                    )
                    analysis_results["comparison"] = comparison_results
                    logger.info("비교 분석 완료")
                except Exception as e:
                    logger.error(f"비교 분석 실패: {e}")
                    analysis_results["comparison"] = {"error": str(e)}

            # 3. 상관관계 분석
            if len(processed_data) >= 2 and self.correlation_analyzer:
                try:
                    correlation_results = await self.correlation_analyzer.analyze(
                        data_dict=processed_data, comparison_specs=comparison_specs
                    )
                    analysis_results["correlation"] = correlation_results
                    logger.info("상관관계 분석 완료")
                except Exception as e:
                    logger.error(f"상관관계 분석 실패: {e}")
                    analysis_results["correlation"] = {"error": str(e)}

            # 4. 유사도 분석
            if len(processed_data) >= 2 and self.similarity_analyzer:
                try:
                    similarity_results = await self.similarity_analyzer.analyze(
                        data_dict=processed_data
                    )
                    analysis_results["similarity"] = similarity_results
                    logger.info("유사도 분석 완료")
                except Exception as e:
                    logger.error(f"유사도 분석 실패: {e}")
                    analysis_results["similarity"] = {"error": str(e)}

            # 5. 추세 분석
            if self.trend_analyzer:
                try:
                    trend_results = await self.trend_analyzer.analyze(
                        data_dict=processed_data
                    )
                    analysis_results["trend"] = trend_results
                    logger.info("추세 분석 완료")
                except Exception as e:
                    logger.error(f"추세 분석 실패: {e}")
                    analysis_results["trend"] = {"error": str(e)}

            # 6. 분석 결과 요약
            successful_analyses = [
                k for k, v in analysis_results.items() if "error" not in v
            ]
            failed_analyses = [k for k, v in analysis_results.items() if "error" in v]

            logger.info(
                f"통계 분석 완료 - 성공: {successful_analyses}, 실패: {failed_analyses}"
            )

            return analysis_results

        except Exception as e:
            logger.error(f"통계 분석 전체 실패: {e}")
            return {"error": f"전체 분석 실패: {str(e)}"}

    def _preprocess_data(self, data_bundle) -> dict:
        """
        데이터 번들을 분석용 딕셔너리로 변환 (개선된 버전)
        """
        processed_data = {}

        if not data_bundle:
            return processed_data

        try:
            # data_bundle이 문자열인 경우 (JSON 파싱 시도)
            if isinstance(data_bundle, str):
                try:
                    import json

                    data_bundle = json.loads(data_bundle)
                except json.JSONDecodeError:
                    logger.warning("data_bundle을 JSON으로 파싱할 수 없습니다.")
                    return processed_data

            # data_bundle이 딕셔너리인 경우
            if isinstance(data_bundle, dict):
                # web_results 처리
                if "web_results" in data_bundle:
                    web_results = data_bundle["web_results"]
                    if isinstance(web_results, dict):
                        for source, data in web_results.items():
                            if isinstance(data, list) and data:
                                processed_data[f"web_{source}"] = data
                                logger.debug(
                                    f"Web 데이터 처리: {source} ({len(data)}개)"
                                )

                # rdb_results 처리
                if "rdb_results" in data_bundle:
                    rdb_results = data_bundle["rdb_results"]
                    if isinstance(rdb_results, dict):
                        for table, data in rdb_results.items():
                            if isinstance(data, list) and data:
                                processed_data[f"db_{table}"] = data
                                logger.debug(f"DB 데이터 처리: {table} ({len(data)}개)")

                # vector_results 처리
                if "vector_results" in data_bundle:
                    vector_results = data_bundle["vector_results"]
                    if isinstance(vector_results, dict):
                        for index, data in vector_results.items():
                            if isinstance(data, list) and data:
                                processed_data[f"vec_{index}"] = data
                                logger.debug(
                                    f"Vector 데이터 처리: {index} ({len(data)}개)"
                                )

            # data_bundle이 객체인 경우 (hasattr 사용)
            elif hasattr(data_bundle, "__dict__"):
                # web_results 처리
                if hasattr(data_bundle, "web_results") and data_bundle.web_results:
                    for source, data in data_bundle.web_results.items():
                        if isinstance(data, list) and data:
                            processed_data[f"web_{source}"] = data
                            logger.debug(f"Web 데이터 처리: {source} ({len(data)}개)")

                # rdb_results 처리
                if hasattr(data_bundle, "rdb_results") and data_bundle.rdb_results:
                    for table, data in data_bundle.rdb_results.items():
                        if isinstance(data, list) and data:
                            processed_data[f"db_{table}"] = data
                            logger.debug(f"DB 데이터 처리: {table} ({len(data)}개)")

                # vector_results 처리
                if (
                    hasattr(data_bundle, "vector_results")
                    and data_bundle.vector_results
                ):
                    for index, data in data_bundle.vector_results.items():
                        if isinstance(data, list) and data:
                            processed_data[f"vec_{index}"] = data
                            logger.debug(f"Vector 데이터 처리: {index} ({len(data)}개)")

            # 직접 리스트나 다른 형태의 데이터인 경우
            elif isinstance(data_bundle, list) and data_bundle:
                processed_data["direct_data"] = data_bundle
                logger.debug(f"직접 데이터 처리: ({len(data_bundle)}개)")

            logger.info(f"데이터 전처리 완료: {len(processed_data)}개 데이터셋")
            return processed_data

        except Exception as e:
            logger.error(f"데이터 전처리 실패: {e}")
            return {}

    def _build_market_context(self, state: MariGraphState) -> dict:
        """
        LLM 해석을 위한 시장 맥락 정보 구성 (개선된 버전)
        """
        try:
            context = {
                "query": state.req_input.query,
                "company_code": state.req_input.company_code,
                "user_num": state.req_input.user_num,
                "detected_language": getattr(
                    state.rewrite_query, "detected_language", "kor"
                ),
            }

            # rewrite_query 정보 추가
            if hasattr(state, "rewrite_query") and state.rewrite_query:
                context.update(
                    {
                        "objective": getattr(state.rewrite_query, "objective", ""),
                        "base_date": getattr(state.rewrite_query, "base_date", ""),
                        "rewritten_query": getattr(
                            state.rewrite_query, "rewritten_query", ""
                        ),
                    }
                )

            # planner 정보 추가
            if hasattr(state, "planner") and state.planner:
                context.update(
                    {
                        "analysis_steps": getattr(state.planner, "analysis_steps", []),
                        "data_collect_steps": getattr(
                            state.planner, "data_collect_steps", []
                        ),
                    }
                )

                # comparison_specs가 있는 경우 추가
                if (
                    hasattr(state.planner, "comparison_specs")
                    and state.planner.comparison_specs
                ):
                    context["comparison_specs"] = state.planner.comparison_specs

            return context

        except Exception as e:
            logger.error(f"시장 맥락 구성 실패: {e}")
            return {
                "query": state.req_input.query if hasattr(state, "req_input") else "",
                "error": f"맥락 구성 실패: {str(e)}",
            }

    async def __call__(
        self,
        state: MariGraphState,
        config: RunnableConfig | None = None,
        writer: StreamWriter | None = None,
    ) -> MariGraphState:
        logger.info(
            f"[{state.req_input.company_code}][user:{state.req_input.user_num}] starting {self.name}"
        )
        self._stream_write_value(writer)

        try:
            input_data = self.input_type(
                **state.rewrite_query.model_dump(),
                analysis_steps=state.planner.analysis_steps,
                **state.data_collect.data_bundle.model_dump(),
            )
            # logger.info("Phase 1: 코드 기반 통계 분석 시작")
            # statistical_results = await self._perform_statistical_analysis(
            #     data_bundle=state.data_collect.data_bundle.model_dump(),
            #     comparison_specs=getattr(state.planner, "comparison_specs", None),
            # )
            # logger.info("Phase 2: LLM 기반 해석 시작")
            # market_context = self._build_market_context(state)
            # if statistical_results:
            #         input_data.statistical_analysis = str(statistical_results)
            # if market_context:
            #     input_data.market_context = str(market_context)

            messages = await build_formatted_prompts(
                company_code=state.req_input.company_code,
                node_name=self.name,
                output_type=self.output_type,
                **input_data.model_dump(),
            )

            # 🔄 Phase 3: LLM 스트리밍 응답
            full_response = []
            async for chunk in astream_llm(messages=messages):
                if chunk:
                    stream_info = StreamInfo(data=StreamData.chunk)
                    self._stream_write_value(writer, stream_info, value=chunk)
                    full_response.append(chunk)

            output = "".join(full_response)

            stream_info = StreamInfo(
                state=StreamStatus.complete, data=StreamData.message
            )
            self._stream_write_value(writer, stream_info, value=output)

        except Exception as e:
            logger.error(f"Hybrid analysis failed: {e}")
            import traceback

            logger.error(f"Full traceback: {traceback.format_exc()}")

            stream_info = StreamInfo(state=StreamStatus.error, data=StreamData.message)
            self._stream_write_value(writer, stream_info, value=str(e))
            output = f"분석 중 오류가 발생했습니다: {e}"

        logger.info(
            f"[{state.req_input.company_code}][user:{state.req_input.user_num}] Analysis Result: \n{output}"
        )
        updated_state = state.model_copy()
        updated_state.data_analysis = output
        return updated_state
