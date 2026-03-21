import logging

from mari_agent.common.config import get_mari_config
from mari_agent.common.types.nodes import (
    DataSearchToolNodeInput,
    DataSearchToolNodeOutput,
)
from mari_agent.graph.tools.tool_manager import BaseSearchTool

mari_config = get_mari_config()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RdbSearchTool(BaseSearchTool):
    @property
    def name(self) -> str:
        return "RdbSearchTool"

    @property
    def description(self) -> str:
        return "Search wti, brent, and other oil prices from RDB database."

    async def search(self, input: DataSearchToolNodeInput) -> DataSearchToolNodeOutput:
        # 웹 검색 로직
        return DataSearchToolNodeOutput()
