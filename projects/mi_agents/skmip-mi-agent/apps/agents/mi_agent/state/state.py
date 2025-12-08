from pydantic import Field

from apps.agents.mi_agent.schemas.mari_agent_input import MariAgentInput
from apps.agents.mi_agent.schemas.search_output import SearchOutput


class MariAgentState(MariAgentInput):
    user_query_language: str | None = Field(
        default=None, description="사용자 입력 질의 언어(영어, 한국어)"
    )
    rewritten_query: str | None = Field(
        default=None,
        description="사용자 질의를 LLM에 의해 재작성해 얻은 보완 질의",
    )
    search_output: SearchOutput = Field(
        default_factory=SearchOutput,
        description="검색 결과",
    )
    current_node: str | None = Field(default=None, description="현재 실행 중인 노드")
    executed_nodes: list[str] | None = Field(
        default_factory=list,
        description="실행된 노드 목록",
    )
    usage: dict | None = Field(default=None, description="LLM 사용량 정보")
    analysis_content: str | None = Field(
        default=None,
        description="분석 내용 (검색 결과 기반)",
    )
