from pydantic import BaseModel, Field

from research_agent.common.types.nodes import (
    ResearchPlannerNodeOutput,
    ResearchSearchNodeOutput,
    ResearchSynthesisNodeOutput,
    UserRequestInput,
)


class ResearchGraphState(BaseModel):
    # User Request Input
    req_input: UserRequestInput = Field(
        default_factory=UserRequestInput, description="사용자 요청 입력 정보"
    )

    # Graph Nodes Results
    ## ResearchPlannerNode results
    planner: ResearchPlannerNodeOutput = Field(
        default_factory=lambda: ResearchPlannerNodeOutput(overall_goal=""),
        description="연구 계획 정보",
    )

    ## ResearchSearchNode results
    search: ResearchSearchNodeOutput = Field(
        default_factory=ResearchSearchNodeOutput,
        description="검색 결과 정보",
    )

    ## ResearchSynthesisNode results
    synthesis: ResearchSynthesisNodeOutput = Field(
        default_factory=lambda: ResearchSynthesisNodeOutput(final_report=""),
        description="최종 리포트 정보",
    )
