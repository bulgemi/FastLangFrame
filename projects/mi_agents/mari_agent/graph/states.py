from pydantic import BaseModel, Field

from mari_agent.common.types.nodes import (
    DataCollectNodeOutput,
    PlannerNodeOutput,
    RewriteQueryNodeOutput,
    UserRequestInput,
)


class MariGraphState(BaseModel):
    # User Request Input
    req_input: UserRequestInput = Field(
        default_factory=UserRequestInput, description="사용자 요청 입력 정보"
    )

    # Graph Nodes Results
    ## RewriteQueryNode results
    rewrite_query: RewriteQueryNodeOutput | None = Field(
        default=None,
        description="최종 재작성 질의 및 정규화 정보, 가정, 변경점, 신뢰도 등 질의 재작성 결과 전체를 포함",
    )

    ## PlannerNode results
    planner: PlannerNodeOutput = Field(
        default_factory=PlannerNodeOutput,
        description="최종 작업 계획 정보",
    )

    ## DataCollectNode results
    data_collect: DataCollectNodeOutput = Field(
        default_factory=DataCollectNodeOutput, description="수집 노드 결과"
    )

    ## DataAnalysisNodeInput results
    data_analysis: str = Field(
        default="", description="분석 정보 (예: entity extraction 등)"
    )
