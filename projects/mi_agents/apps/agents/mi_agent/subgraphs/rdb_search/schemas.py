from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class RDBSearchInput(BaseModel):
    api_key: str | None = Field(
        default=None,
        description="A.X플랫폼 API호출을 위한 api_key",
    )  # TODO: None허용 검토후 수정
    headers: dict[str, Any] | None = Field(default=None, description="A.X플랫폼 API호출시 전달할 headers")

    rewritten_query: str = Field(
        ...,
        description="사용자 입력 질의",
    )
    histories: list[dict] = Field(default_factory=list, description="대화 히스토리")
    repo_id_rdb_metadata: UUID | None = Field(
        default=None,
        description="RDB 메타데이터 설명 문서가 저장된 벡터DB 리포지토리(컬렉션/인덱스) 식별자. ",
    )

    authorized_product_nums: list[int] | None = Field(
        default=None,
        description="접근 권한 있는 상품 번호 리스트",
    )


class RDBSearchResult(BaseModel):
    used_table: str = Field(
        ...,
        description="생성/실행된 SQL에서 참조된 테이블명",
    )
    metric_data: dict[str, Any] = Field(
        ...,
        description="RDB 검색 결과(직렬화된 문자열 등; 사용 형식은 상위 레이어에서 해석)",
    )
    related_data: str = Field(
        ...,
        description="연관 데이터 식별자(예: data_source_num)",
    )
    sql: str = Field(  # TODO: 리스트로 전달 & sql_queries로 명칭 변경 MI BE와 논의 후, 수정 예정, int로 변환 검토(MI BE와 논의)
        ...,
        description="생성된 sql",
    )

class RDBSearchResults(BaseModel):
    used_tables: list[str] = Field(
        default_factory=list,
        description="생성/실행된 SQL에서 참조된 테이블명 목록",
    )
    metric_data: list[dict[str, Any]] = Field(
        default_factory=list,
        description="RDB 검색 결과(직렬화된 문자열 등; 사용 형식은 상위 레이어에서 해석)",
    )
    related_data: list[str] = Field(
        default_factory=list,
        description="연관 데이터 식별자 목록(예: data_source_num 리스트)",
    )
    charts: list[str] = Field(
        default_factory=list,
        description="차트",
    )
    sqls: str | None= Field(  # TODO: 리스트로 전달 & sql_queries로 명칭 변경 MI BE와 논의 후, 수정 예정
        default=None,
        description="생성된 sql들",
    )


class RDBSearchOutput(RDBSearchResults):
    pass


class RDBSearchQuery(BaseModel):
    query: str = Field(
        ...,
        description="사용자 질의(단일 질의로 분리, 정제한 질의)",
        min_length=1,
    )
    search_text: str | None = Field(
        default=None,
        description="사용자 질의로 부터 추출한 키워드 (RDB검색을 위한 VDB검색(후보군 데이터 추출) 시 사용)",
    )


class VDBSearchCandidate(BaseModel):
    tbl_expn: str = Field(
        ...,
        description="원본 사용자 질의와 유사도 높은 후보데이터의 테이블 설명",
    )

    agtmtm_id: int = Field(
        ...,
        description="원본 사용자 질의와 유사도 높은 후보데이터의 메타데이터 ID",
    )


class RDBSearchCandidate(BaseModel):
    query: str = Field(
        ...,
        description="사용자 질의(단일 질의로 분리, 정제한 질의)",
        min_length=1,
    )
    company_code: str | None = Field(
        default=None,
        description="회사 코드",
    )
    vdb_search_candidates: list[VDBSearchCandidate] = Field(
        ...,
        description="사용자 질의와 유사도 높은 정보를 VectorDB로 부터 조회한 결과(테이블명, 데이터 설명, 메타데이터ID)",
    )


class RDBSearchNltoSqlMapping(BaseModel):
    rdb_search_nl_query: str = Field(
        ...,
        description="RDB 검색을 위해 정제·보정된 자연어 질의(NL)",
        min_length=1,
    )
    sql: str | None = Field(
        default=None,
        description="해당 자연어 질의로부터 생성된 SQL(생성되지 않은 경우 None)",
    )
