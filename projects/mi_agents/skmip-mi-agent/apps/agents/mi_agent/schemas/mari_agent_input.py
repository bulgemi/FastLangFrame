from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class MariAgentInput(BaseModel):
    api_key: str | None = Field(
        default=None,
        description="A.X플랫폼 API호출을 위한 api_key",
    )
    headers: dict[str, Any] | None = Field(default=None, description="A.X플랫폼 API호출시 전달할 headers")
    company_code: str | None = Field(
        default=None,
        description="회사 코드",
    )
    user_num: int | None = Field(
        default=None,
        description="사용자 번호",
    )
    authorized_product_nums: list[int] | None = Field(
        default=None,
        description="접근 권한 있는 상품 번호 리스트",
    )
    message: str | None = Field(
        default=None,
        description="사용자 입력 질의",
    )  # TODO: user_query로 변경하는 방안에 대해 MI BE와 논의
    histories: list[dict] = Field(default_factory=list, description="대화 히스토리")
    web_search: bool | None = Field(
        default=False,
        description="웹 검색 사용 여부(기본값은 True)",
    )
    repo_id: UUID | None = Field(
        default=None,
        description="문서 검색 대상 벡터 저장소의 리포지토리(컬렉션/인덱스) 식별자.",
    )
    repo_id_rdb_metadata: UUID | None = Field(
        default=None,
        description="RDB 메타데이터 설명 문서가 저장된 벡터DB 리포지토리(컬렉션/인덱스) 식별자. ",
    )
