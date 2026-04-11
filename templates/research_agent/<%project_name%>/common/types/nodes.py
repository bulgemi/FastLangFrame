"""
데이터 수집, 분석, 계획, 입출력 등 파이프라인을 구성하는 주요 노드들의
입력(Input) 및 출력(Output) 모델을 제공합니다.

포함된 주요 노드 및 역할:
1. 파이프라인 제어 및 처리 노드:
   - PrepareAxPromptNode: 프롬프트 리소스 준비
   - RewriteQueryNode: 질의 재작성 및 정규화
   - PlannerNode: 전체 작업 계획 수립
   - DataCollectNode: 데이터 수집 단계 조율
   - DataAnalysisNode: 수집 데이터 분석 및 가공

2. 데이터 수집 도구 노드:
   - RdbSearchNode: 관계형 데이터베이스(RDB) 검색
   - WebSearchNode: 웹 뉴스/이벤트 검색 및 수집
   - VectorSearchNode: 임베딩 기반 벡터DB 검색

"""

from typing import TypeVar

from pydantic import BaseModel, Field, field_validator

from <%project_name%>.common.config import mari_config
from <%project_name%>.common.types.schemas import (
    DataBundle,
    PeriodQuery,
    PromptResource,
    Step,
)
from <%project_name%>.graph.prompts.prompt_manager import PromptTag

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class DummyOutput(BaseModel):
    pass


class UserRequestInput(BaseModel):
    query: str = Field(default="", description="사용자 질의")
    company_code: str = Field(default="", description="회사 코드")
    dept_code: str = Field(default="", description="부서 코드")
    user_num: int = Field(default=0)
    authorized_product_nums: list[int] = Field(default_factory=list)
    repository_ids: list[int] = Field(default_factory=list, description="repo id 목록")
    histories: list[dict] = Field(
        default_factory=list,
        description="대화 히스토리",
        max_length=mari_config.LATEST_HISTORIES_CNT,
    )
    web_search_enabled: bool = Field(default=True, description="웹 검색 도구 사용 여부")

    @field_validator("histories")
    @classmethod
    def latest_histories(cls, v: list[dict]) -> list[dict]:
        return (
            v[-mari_config.LATEST_HISTORIES_CNT :]
            if len(v) > mari_config.LATEST_HISTORIES_CNT
            else v
        )


## PrepareAxPromptNode Input/Output Types
class PrepareAxPromptNodeInput(BaseModel):
    # 프롬프트 리소스를 가져오기 위한 태그 정보
    prompt_group: str = Field(
        default=mari_config.AX_MCP_PROMPT_MARI_TAG_GROUP,
        description="프롬프트 그룹 태그",
    )
    company_code: str = Field(default="")
    dept_code: str = Field(default="", description="부서 코드")

    @property
    def prompt_tags(self) -> str:
        tags = [self.prompt_group]
        if self.company_code:
            tags.append(PromptTag.to_prompt_tag(self.company_code))
        if self.dept_code:
            tags.append(PromptTag.to_dept_tag(self.dept_code))
        return ",".join(tags)


class PrepareAxPromptNodeOutput(BaseModel):
    prompt_resources: list[PromptResource] = Field(
        default_factory=list, description="사용 가능한 프롬프트 리소스 목록"
    )


## RewriteQueryNode Input/Output Types
class RewriteQueryNodeInput(BaseModel):
    query: str
    base_date: str = Field(
        default="",
        description="상대 기간을 절대 날짜로 변환할 기준일. 'YYYY-MM-DD' 형식",
    )
    histories: list[dict] = Field(default_factory=list, description="대화 히스토리")


class RewriteQueryNodeOutput(BaseModel):
    detected_language: str = Field(
        ...,
        description="질의에서 감지된 언어 코드 (예: 'kor', 'eng', 'japan', 'china' etc.)",
    )
    is_domain_related: bool = Field(..., description="질의의 도메인 관련 여부")
    base_date: str | None = Field(
        None, description="상대 기간을 절대 날짜로 변환할 기준일. 'YYYY-MM-DD' 형식"
    )
    rewritten_query: str = Field(
        ...,
        description="재작성된 최종 질의. 상대적 시간 표현(오늘/어제/내일 등) 및 특정 날짜가 명시된 경우, 반드시 절대 날짜로 변환하여 포함 (예: 'on 2025-11-19')",
    )
    objective: str = Field(
        ...,
        description="구체적인 작업 목표를 영문으로 간결하게 기술, 상대적 기간이 포함된 경우 절대 날짜로 변환하여 명시",
        examples=[
            "Retrieve Brent crude oil front-month settlement price",
            "Analyze WTI price trend from 2024-08-19 to 2024-11-19",
            "Compare Henry Hub and LNG JKM price spread",
        ],
    )
    period_queries: list[PeriodQuery] = Field(
        ...,
        description="전체 질의를 절대 날짜로 변환 한 후, 각 기간에 맞게 질의를 키워드 기반 세분화하여 작성.",
        examples=[
            {
                "period": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
                "query": "키워드 기반 세분화된 질의. 특정 날짜에 대한 질의 경우, 'on YYYY-MM-DD' 날짜 정보 포함.",
            }
        ],
    )
    # reasoning_details 포함 시, 대략 4~7초 LLM 응답 시간 증가(정확도 성능 확인 시)
    # reasoning_details: dict = Field(
    #     ...,
    #     description="질의 재작성에 대한 상세 정보, 가정, 변경점, 신뢰도 등 질의 재작성 결과 전체를 포함",
    #     examples={
    #         "normalized": {
    #             "commodity": "oil|natgas|lng",
    #             "period": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
    #             "metrics": ["settle", "spread_1M"],
    #             "unit": "USD/bbl|USD/MMBtu",
    #             "benchmarks": ["Brent", "WTI", "Dubai", "Henry Hub", "JKM"],
    #             "contracts": ["front-month", "Cal-25"],  # 필요 시
    #             "region": ["Global", "Asia", "US", "Europe"],
    #         },
    #         "assumptions_filled": [
    #             "기간=...",
    #             "단위=...",
    #             "벤치마크=...",
    #             "계약월=front-month",
    #         ],
    #         "changes_diff": {
    #             "added": [
    #                 {
    #                     "field": "period",
    #                     "value": "2025-06-17~2025-09-15",
    #                     "source_ids": ["m_12"],
    #                 }
    #             ],
    #             "modified": [
    #                 {
    #                     "field": "benchmark",
    #                     "from": "유가",
    #                     "to": "Brent front-month",
    #                     "source_ids": ["m_05"],
    #                 }
    #             ],
    #             "dropped": [{"field": "ambiguous_term", "value": "최근"}],
    #         },
    #         "normalization_log": [
    #             "브랜트 → Brent (synonym)",
    #             "정산가/종가 → settle (synonym)",
    #             "‘최근 3개월’ → 2025-06-17~2025-09-15 (base_date 적용)",
    #         ],
    #         "unresolved_gaps": [],
    #     },
    # )


## PlannerNode Input/Output Types
class PlannerNodeInput(BaseModel):
    objective: str = Field(..., description="작업 목표")
    rewritten_query: str = Field(..., description="재작성된 최종 질의")
    period_queries: list[PeriodQuery] = Field(..., description="기간과 쿼리 분리")
    collect_tools_desc: str = Field(..., description="사용할 수집 도구 설명")
    analysis_tools_desc: str = Field(..., description="사용할 분석 도구 설명")


class PlannerNodeOutput(BaseModel):
    # data 수집과 분석 Plan 분리
    collect_steps: list[Step] = Field(
        default_factory=list,
        description="데이터 수집 수행 단계, periodic_queries 기준으로 구성",
    )
    analysis_steps: list[Step] = Field(
        default_factory=list, description="데이터 분석 수행 단계"
    )
    comparison_specs: dict = Field(
        default_factory=dict,
        description="cohorts, pairs, alignment{period, frequency, timezone, unit, missing}",
        examples=[
            {
                "cohorts": [
                    {
                        "id": "G1",
                        "desc": "Brent front-month",
                        "filters": {
                            "commodity": "oil",
                            "benchmark": "Brent",
                            "contract": "front-month",
                        },
                    },
                    {
                        "id": "G2",
                        "desc": "WTI front-month",
                        "filters": {
                            "commodity": "oil",
                            "benchmark": "WTI",
                            "contract": "front-month",
                        },
                    },
                    # 전후 비교라면 {id:"PRE"}, {id:"POST"} 등으로 기간 분할
                ],
                "pairs": [
                    {"lhs": "G1", "rhs": "G2", "ops": ["spread", "diff", "ratio"]}
                    # 전후비교: {"lhs":"PRE","rhs":"POST","ops":["delta","effect_size"]}
                ],
                "alignment": {
                    "period": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
                    "frequency": "day",
                    "timezone": "UTC",
                    "unit": "USD/bbl",
                    "missing": "forward_fill|max_drop=5%",
                },
            }
        ],
    )


## DataCollectNode Input/Output Types
class DataCollectNodeInput(BaseModel):
    query: str = Field(default="", description="재작성된 최종 질의")
    base_date: str = Field(
        default="",
        description="상대 기간을 절대 날짜로 변환할 기준일. 'YYYY-MM-DD' 형식",
    )
    objective: str = Field(default="", description="작업 목표")
    collect_steps: list[Step] = Field(
        default_factory=list, description="작업 계획의 세부 단계"
    )


class DataCollectNodeOutput(BaseModel):
    data_bundle: DataBundle = Field(
        default_factory=DataBundle, description="수집된 데이터 번들"
    )


## DataAnalysisNodeInput Input/Output Types
class DataAnalysisNodeInput(BaseModel):
    # RewriteQueryNode results
    detected_language: str = Field(
        ...,
        description="질의에서 감지된 언어 코드 (예: 'kor', 'eng', 'japan', 'china' etc.)",
    )
    rewritten_query: str = Field(default="", description="재작성된 최종 질의")
    base_date: str | None = Field(
        default=None,
        description="상대 기간을 절대 날짜로 변환할 기준일. 'YYYY-MM-DD' 형식",
    )
    objective: str = Field(default="", description="작업 목표")
    # PlannerNode results
    analysis_steps: list[Step] = Field(
        default_factory=list, description="작업 계획의 세부 단계"
    )
    # DataCollectNode results
    rdb_data: list[dict] = Field(default_factory=list, description="수집된 RDB 데이터")
    vector_data: list[dict] = Field(
        default_factory=list, description="수집된 Vector 데이터"
    )
    web_data: list[dict] = Field(default_factory=list, description="수집된 Web 데이터")

    # 통계 분석 결과 및 시장 맥락 정보 추가
    statistical_results: dict = Field(
        default_factory=dict, description="RDB 통계 분석 결과 데이터"
    )
    market_context: dict = Field(
        default_factory=dict, description="RDB 시장 상황 및 맥락 정보"
    )


## OutOfDomainAnswerNode Input Type
class OutOfDomainAnswerNodeInput(BaseModel):
    query: str
    base_date: str | None = None
    histories: list[dict] | None = Field(default_factory=list)
    detected_language: str = Field(
        ...,
        description="질의에서 감지된 언어 코드 (예: 'kor', 'eng', 'japan', 'china' etc.)",
    )


# Tool Nodes Input/Output Types
class DataSearchToolNodeInput(BaseModel):
    """
    Parameters:
    - period_query (dict): 기간과 쿼리 정보
        - period (dict): 검색 기간
            - start (str): 시작일 (YYYY-MM-DD 형식)
            - end (str): 종료일 (YYYY-MM-DD 형식)
        - query (str): 검색어

    Example usage:
    WebSearchNode(
        period_query={{
            "period": {"start": "2025-09-29", "end": "2025-09-29"},
            "query": "Brent front-month settle price"
        }}
    )
    """

    period_query: PeriodQuery = Field(..., description="기간과 쿼리")

    @classmethod
    def model_validate(cls, data: dict):
        if data and isinstance(data, dict) and "period_query" not in data:
            data = {"period_query": data}

        return super().model_validate(data)


class DataSearchToolNodeOutput(DataBundle):
    pass


class IntervalEventMapperNodeInput(BaseModel):
    pass


class DataAnalysisToolNodeInput(BaseModel):
    """
    data_bundle (str): 이전 단계에서 수집된 데이터 번들
    """

    data_bundle: str = Field(description="수집된 데이터 번들")


class DataAnalysisToolNodeOutput(BaseModel):
    results: dict = Field(default_factory=dict, description="Analysis Tool 결과")

## ResearchNode Input/Output Types
class ResearchPlannerNodeInput(BaseModel):
    query: str = Field(..., description="사용자 질의")
    histories: list[dict] = Field(default_factory=list, description="대화 히스토리")

class ResearchPlannerNodeOutput(BaseModel):
    research_tasks: list[str] = Field(default_factory=list, description="분해된 연구 작업 목록")
    overall_goal: str = Field(..., description="전체 연구 목표")

class ResearchSearchNodeInput(BaseModel):
    tasks: list[str] = Field(..., description="수행할 연구 작업 목록")

class ResearchSearchNodeOutput(BaseModel):
    search_results: list[dict] = Field(default_factory=list, description="검색 결과 목록")

class ResearchSynthesisNodeInput(BaseModel):
    query: str = Field(..., description="원래 질의")
    search_results: list[dict] = Field(..., description="수집된 검색 결과")
    overall_goal: str = Field(..., description="연구 목표")

class ResearchSynthesisNodeOutput(BaseModel):
    final_report: str = Field(..., description="최종 Markdown 리포트")
