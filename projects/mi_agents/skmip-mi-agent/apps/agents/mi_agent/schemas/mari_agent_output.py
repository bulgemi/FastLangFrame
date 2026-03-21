# TODO: MessageModel형식에 대해서 MI BE와 한번 정리하기. 변수명 및 계츨 구조
from typing import Any

from pydantic import BaseModel, Field

from apps.agents.mi_agent.subgraphs.vdb_search.schemas import VDBSearchOutput, VectorSourceModel


class ChartModel(BaseModel):
    order: int = Field(..., description="차트 렌더링/정렬 순서 (0-based 권장)")
    legend: str = Field(..., description="차트 범례명")
    date: list[str] = Field(..., description="x축 날짜 라벨 목록 (YYYY-MM-DD 등)")
    value: list[float] = Field(..., description="y축 값 목록 (date와 길이 매칭)")


class SourceModel(BaseModel):
    url: str = Field(..., description="출처 URL")
    source_nm: str = Field(..., description="출처명(사이트/문서 이름 등)")


class ContentModel(BaseModel):
    text: str = Field(
        ...,
        description="최종 응답 텍스트(요약/해설 등). 없을 수 있음",
    )
    related_data: list[int] = Field(
        default_factory=list,
        description="RDB 기반 관련 데이터 식별자 목록",
    )
    charts: list[ChartModel] = Field(
        default_factory=list,
        description="시각화용 차트 데이터 목록",
    )
    sources: list[SourceModel] = Field(
        default_factory=list,
        description="웹 검색 등 외부 출처 목록",
    )
    vector_sources: list[VectorSourceModel] | None = Field(
        default_factory=list,
        description="VectorDB에서 수집한 출처/문서 메타 목록",
    )


class MessageModel(BaseModel):
    content: ContentModel | None = Field(
        default=None,
        description="에이전트 수행 결과(텍스트/차트/출처 등) 컨테이너",
    )
    usage: Any | None = Field(
        default=None,
        description="LLM 사용량(토큰/비용 등) 기록. 스키마 미정이면 Any 유지",
    )
    sql: str | None = Field(
        default=None,
        description="실행한 SQL 질의문(필요 시 기록)",
    )
    used_tables: list[str] = Field(
        default_factory=list,
        description="질의/분석에 사용된 테이블명 목록",
    )
    rewrite: str | None = Field(
        default=None,
        description="리라이트된 사용자 요청(프롬프트 보정 결과 등)",
    )


class MariAgentOutput(BaseModel):
    messages: list[MessageModel] = Field(
        default_factory=list,
        description="그래프 실행으로 생성된 메시지 배열",
    )
