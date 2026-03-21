from pydantic import BaseModel, Field

class BaseAgentInput(BaseModel):
    """Base input schema for FastLangFrame agents"""
    query: str = Field(..., description="The user's input query")
    session_id: str = Field(..., description="Unique session identifier for tracing/memory")

class BaseAgentOutput(BaseModel):
    """Base output schema for FastLangFrame agents"""
    answer: str = Field(..., description="The agent's final answer")
    tokens_used: int = Field(default=0, description="Number of tokens used in generation")
