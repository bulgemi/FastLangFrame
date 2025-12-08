from pydantic import BaseModel, Field


class WebSearchState(BaseModel):
    rewritten_query: str | None = Field(default=None, description="사용자 질의를 LLM에 의해 재작성해 얻은 보완 질의")
