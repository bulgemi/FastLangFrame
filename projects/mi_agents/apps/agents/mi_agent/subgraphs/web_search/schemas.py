from pydantic import BaseModel, Field


class WEBSearchOutput(BaseModel):
    web_sources: list[str] = Field(
        default_factory=list,
        description="웹검색 목록",
    )
