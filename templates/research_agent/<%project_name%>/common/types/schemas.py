from enum import Enum

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, ConfigDict, Field


class StreamStatus(str, Enum):
    start = "start"
    progress = "progress"
    error = "error"
    complete = "complete"


class StreamData(str, Enum):
    message = "message"
    series = "series"
    table = "table"
    chunk = "chunk"


class StreamInfo(BaseModel):
    state: StreamStatus = Field(default=StreamStatus.progress)
    data: StreamData = Field(default=StreamData.message)

    def to_dict(self) -> dict[str, str]:
        return {"state": self.state.value, "data": self.data.value}


class PeriodQuery(BaseModel):
    period: dict[str, str] = Field(..., description="start:YYYY-MM-DD, end:YYYY-MM-DD")
    query: str = Field(..., description="재작성된 단일 쿼리")


class PromptResource(BaseModel):
    """프롬프트 리소스 스키마"""

    prompt_id: str = Field(..., description="프롬프트 ID")
    prompt_name: str = Field(..., description="프롬프트 이름")
    description: str = Field("", description="프롬프트 설명")
    tags: list[str] = Field("", description="프롬프트 태그 목록")
    variables: list[str] = Field([], description="프롬프트 변수 목록")
    messages: list[HumanMessage | SystemMessage] = Field(
        [], description="프롬프트 메시지 목록"
    )

    model_config = ConfigDict(extra="allow")


class Step(BaseModel):
    id: str = Field(..., description="단계 ID")
    tool_name: str = Field(..., description="사용할 도구 이름")
    params: dict = Field(..., description="도구별 파라미터")
    depends_on: list[str] = Field(
        default_factory=list,
        description="이 단계가 의존하는 이전 단계 ID 목록",
    )
    # enough_if: str = Field(
    #     ...,
    #     description="이 단계가 충분한지 판단하는 조건식 (예: '∀G rowcount>=60 & no_nulls(metrics)')",
    # )
    # on_insufficient: dict = Field(
    #     ...,
    #     description="데이터가 부족할 때의 증강 및 재시도 전략",
    #     examples=[
    #         {
    #             "augment": [
    #                 {"param": "period", "widen_by_days": 7},
    #                 {"param": "groupby", "to": "day"},
    #             ],
    #             "retry_at_most": 2,
    #         }
    #     ],
    # )

    model_config = ConfigDict(exclude_none=True)


class WebDataSchema(BaseModel):
    title: str = Field(description="웹 페이지 제목")
    content: str = Field(description="웹 페이지의 핵심 내용")
    url: str = Field(description="웹 페이지 원문 링크 주소")
    # published_date: str | None = Field(
    #     default="", description="웹 페이지 발행 시각(YYYY-MM-DD hh:mm)"
    # )
    # raw_content: str | None = Field(
    #     default="", description="웹 페이지 원문 전체 텍스트"
    # )

    model_config = ConfigDict(exclude_none=True)


class DataBundle(BaseModel):
    rdb_data: list[dict] = Field(default_factory=list)
    vector_data: list[dict] = Field(default_factory=list)
    web_data: list[dict] = Field(default_factory=list)

    @property
    def summary(self) -> str:
        return (
            f"RDB rows: {len(self.rdb_data)}, "
            f"Vector items: {len(self.vector_data)}, "
            f"Web pages: {len(self.web_data)}"
        )


class ToolCategory(str, Enum):
    data_search = "data_search"
    data_analysis = "data_analysis"


# Output models for time series data


class TimeSeriesItem(BaseModel):
    legend: str
    date: list[str]
    value: list[float]


class TimeSeriesResult(BaseModel):
    results: list[TimeSeriesItem]
