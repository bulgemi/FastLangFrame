import logging

from <%project_name%>.common.config import get_flf_config
from <%project_name%>.common.types.nodes import (
    DataSearchToolNodeInput,
    DataSearchToolNodeOutput,
)
from <%project_name%>.graph.tools.tool_manager import BaseSearchTool

flf_config = get_flf_config()

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
