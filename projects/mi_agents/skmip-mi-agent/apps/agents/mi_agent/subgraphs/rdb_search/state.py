from __future__ import annotations

from connectors.vdb.schemas import RetrievalAdvancedQuery
from pydantic import Field

from apps.agents.mi_agent.schemas.mari_agent_input import MariAgentInput
from apps.agents.mi_agent.subgraphs.rdb_search.schemas import (
    RDBSearchCandidate,
    RDBSearchQuery,
    RDBSearchResults,
)


class RDBSearchState(MariAgentInput):
    rewritten_query: str | None = Field(
        default=None,
        description="사용자 질의를 LLM으로 정제/보완하여 얻은 최종 자연어 질의",
    )

    vdb_search_condition: RetrievalAdvancedQuery | None = Field(
        default=None,
        description="사용자 질의와 관련성 높은 데이터를 벡터DB에서 조회해오기 위한 검색 조건",
    )
    rdb_search_queries: list[RDBSearchQuery] | None = Field(
        default=None,
        description="분리된 사용자 질의 및 추출 키워드 (RDB검색을 위한 VDB검색(후보군 데이터 추출) 시 사용)리스트",
    )
    cantidate_items: list[RDBSearchCandidate] | None = Field(
        default=None,
        description="사용자 질의와 유사도 높은 데이터 리스트(벡터DB로 부터 추출)",
    )
    rdb_search_results: RDBSearchResults | None = Field(
        default=None,
        description="RDB검색결과(조회된 데이터 리스트, 관련 데이터 항목들, 관련 테이블들, 생성된 SQL)",
    )
