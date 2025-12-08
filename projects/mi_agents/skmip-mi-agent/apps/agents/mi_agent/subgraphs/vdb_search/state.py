from typing import Any
from uuid import UUID

from connectors.vdb.schemas import RetrievalAdvancedQuery
from pydantic import BaseModel, Field

from apps.agents.mi_agent.schemas.mari_agent_input import MariAgentInput
from apps.agents.mi_agent.subgraphs.vdb_search.schemas import VDBSearchItem


class VDBSearchState(MariAgentInput):
    rewritten_query: str = Field(
        ...,
        description="사용자 질의를 LLM으로 정제/보완하여 얻은 최종 자연어 질의",
    )
    vdb_search_condition: RetrievalAdvancedQuery | None = Field(
        default=None,
        description="사용자 질의와 관련성 높은 데이터를 벡터DB에서 조회해오기 위한 검색 조건",
    )
    vector_sources: list[VDBSearchItem] | None = Field(
        default_factory=list,
        description="vectorDB 검색 결과",
    )
