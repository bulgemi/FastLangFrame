import asyncio
import logging
import threading
from abc import ABC, abstractmethod
from typing import Dict

from langchain_core.tools import StructuredTool

from mari_agent.common.types.nodes import (
    DataAnalysisToolNodeInput,
    DataAnalysisToolNodeOutput,
    DataSearchToolNodeInput,
    DataSearchToolNodeOutput,
)
from mari_agent.common.types.schemas import ToolCategory

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BaseSearchTool(ABC):
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.data_search

    @property
    def input_type(self) -> type[DataSearchToolNodeInput]:
        return DataSearchToolNodeInput

    @property
    def output_type(self) -> type[DataSearchToolNodeOutput]:
        return DataSearchToolNodeOutput

    @property
    @abstractmethod
    def name(self) -> str:
        """도구 이름"""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """도구 설명"""
        ...

    @abstractmethod
    async def search(self, input: DataSearchToolNodeInput) -> DataSearchToolNodeOutput:
        """검색 실행"""
        ...

    def as_structured_tool(self) -> StructuredTool:
        async def async_handler(**kwargs):
            search_input = self.input_type.model_validate(kwargs)
            return await self.search(search_input)

        def sync_handler(**kwargs):
            try:
                search_input = self.input_type.model_validate(kwargs)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.search(search_input))
                loop.close()
                return result
            except Exception as e:
                logger.error(f"Error in sync fallback: {e}")
                return {"error": str(e)}

        description_parts = [
            f"### {self.name}",
            f"**Detail**: {self.__class__.__doc__ or self.description}",
            f"**Input format**: {self.input_type.__doc__}",
            f"**Output**: {self.output_type.__doc__}",
        ]

        return StructuredTool(
            name=self.name,
            func=sync_handler,
            coroutine=async_handler,
            description="\n".join(description_parts),
            args_schema=self.input_type,
        )


class BaseAnalysisTool(ABC):
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.data_analysis

    @property
    def input_type(self) -> type[DataAnalysisToolNodeInput]:
        return DataAnalysisToolNodeInput

    @property
    def output_type(self) -> type[DataAnalysisToolNodeOutput]:
        return DataAnalysisToolNodeOutput

    @property
    @abstractmethod
    def name(self) -> str:
        """도구 이름"""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """도구 설명"""
        ...

    @abstractmethod
    async def analyze(
        self, input_data: DataAnalysisToolNodeInput
    ) -> DataAnalysisToolNodeOutput:
        """분석 실행"""
        ...

    def as_structured_tool(self) -> StructuredTool:
        async def async_handler(**kwargs):
            search_input = self.input_type.model_validate(kwargs)
            result = await self.analyze(search_input)
            return result.model_dump()

        def sync_handler(**kwargs):
            try:
                search_input = self.input_type.model_validate(kwargs)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.analyze(search_input))
                loop.close()
                return result
            except Exception as e:
                logger.error(f"Error in sync fallback: {e}")
                return {"error": str(e)}

        description_parts = [
            f"### {self.name}",
            f"**Detail**: {self.__class__.__doc__ or self.description}",
            f"**Input format**: {self.input_type.__doc__}",
            f"**Output**: {self.output_type.__doc__}",
        ]

        return StructuredTool(
            name=self.name,
            func=sync_handler,
            coroutine=async_handler,
            description="\n".join(description_parts),
            args_schema=self.input_type,
        )


class ToolManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self.search_tools, self.analysis_tools = self._create_tools()
                    self._initialized = True

    def _create_tools(
        self,
    ) -> tuple[Dict[str, StructuredTool], Dict[str, StructuredTool]]:
        from mari_agent.graph.tools.data_analysis.similarity import TimeSeriesTrendTool
        from mari_agent.graph.tools.data_collect.rdb_search import RdbSearchTool
        from mari_agent.graph.tools.data_collect.vector_search import VectorSearchTool
        from mari_agent.graph.tools.data_collect.web_search import WebSearchTool

        tool_classes_config = {
            "search": [WebSearchTool, RdbSearchTool, VectorSearchTool],
            "analysis": [TimeSeriesTrendTool],
        }

        search_tools = {}
        analysis_tools = {}

        for tool_type, tool_classes in tool_classes_config.items():
            target_dict = search_tools if tool_type == "search" else analysis_tools

            for tool_class in tool_classes:
                tool_inst = tool_class()
                target_dict[tool_inst.name] = tool_inst.as_structured_tool()

        return search_tools, analysis_tools

    async def ainvoke_tool(
        self,
        tool_name: str,
        input_data: dict,
        category: ToolCategory,
    ) -> DataSearchToolNodeOutput | DataAnalysisToolNodeOutput:
        tool_dict = (
            self.search_tools
            if category == ToolCategory.data_search
            else self.analysis_tools
        )

        tool = tool_dict[tool_name]
        return await tool.ainvoke(input_data)

    def get_description(self, category: ToolCategory) -> str:
        tools = (
            self.search_tools
            if category == ToolCategory.data_search
            else self.analysis_tools
        )
        descriptions = [
            f"- **{tool_name}**: {tool.description}"
            for tool_name, tool in tools.items()
        ]
        return "\n".join(descriptions)


tool_manager = ToolManager()
