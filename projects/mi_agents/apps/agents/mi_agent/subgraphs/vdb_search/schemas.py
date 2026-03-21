from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class VDBSearchInput(BaseModel):
    api_key: str | None = Field(
        default=None,
        description="A.X플랫폼 API호출을 위한 api_key",
    )  # TODO: None허용 검토후 수정
    headers: dict[str, Any] | None = Field(default=None, description="A.X플랫폼 API호출시 전달할 headers")

    rewritten_query: str | None = Field(
        default=None,
        description="사용자 입력 질의",
    )
    histories: list[dict] = Field(default_factory=list, description="대화 히스토리")
    repo_id: UUID | None = Field(
        default=None,
        description="RDB 메타데이터 설명 문서가 저장된 벡터DB 리포지토리(컬렉션/인덱스) 식별자. ",
    )

    authorized_product_nums: list[int] | None = Field(
        default=None,
        description="접근 권한 있는 상품 번호 리스트",
    )


class VDBSearchOutput(BaseModel):
    vector_sources: list[VectorSourceModel] = Field(
        default_factory=list,
        description="VectorDB에서 수집한 출처/문서 메타 목록",
    )


class VectorSourceModel(BaseModel):
    source: str = Field(..., description="벡터 소스 경로/ID")
    title: str = Field(..., description="문서 제목")
    gds_no: int = Field(..., description="내부 GDS 식별 번호")
    gds_data_dstg_id: str = Field(..., description="내부 데이터 식별자")


class VDBSearchItem(BaseModel):
    content: str = Field(
        ...,
        title="검색된 본문 내용",
        description="검색 쿼리에 대응하는 문서의 본문 내용 조각입니다.",
    )

    metadata: dict = Field(
        ...,
        title="문서 메타데이터",
        description="검색된 문서와 관련된 메타데이터입니다. 예를 들어, 문서 위치, 문서명, 문서 포맷 등이 포함됩니다.",
    )

    score: float = Field(
        ...,
        title="검색 점수",
        description="검색 쿼리와의 일치도를 나타내는 점수입니다. 높은 점수는 더 높은 관련성을 의미합니다.",
    )
