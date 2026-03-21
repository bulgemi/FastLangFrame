import logging

from <%project_name%>.common.config import get_mari_config
from <%project_name%>.common.types.nodes import (
    DataSearchToolNodeInput,
    DataSearchToolNodeOutput,
)
from <%project_name%>.graph.tools.tool_manager import BaseSearchTool

mari_config = get_mari_config()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorSearchTool(BaseSearchTool):
    @property
    def name(self) -> str:
        return "VectorSearchTool"

    @property
    def description(self) -> str:
        return "Search Report for wti, brent, and other oil prices."

    async def search(self, input: DataSearchToolNodeInput) -> DataSearchToolNodeOutput:
        # 웹 검색 로직
        return DataSearchToolNodeOutput()
