from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AgentInvokeRequest(BaseModel):
    """단일 에이전트 실행을 위한 요청 모델"""
    input: Dict[str, Any] = Field(
        ..., 
        description="에이전트에 전달될 입력 딕셔너리. 예: {'text': 'hi'}",
        examples=[{"text": "hi"}, {"text": "Summarize the latest news about AI"}]
    )
    config: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="실행 설정 값 (런타임 옵션 등). 예: {'configurable': {'thread_id': '1'}}",
        examples=[{"configurable": {"thread_id": "1"}}]
    )

class AgentInvokeResponse(BaseModel):
    """단일 에이전트 실행 결과 응답 모델"""
    result: Optional[Any] = Field(default=None, description="에이전트 실행 결과 데이터")
    status: str = Field(default="ok", description="실행 상태 (ok, error)")
    error: Optional[str] = Field(default=None, description="에러 메시지 (발생 시)")

class AgentBatchRequest(BaseModel):
    """배치(다중) 에이전트 실행을 위한 요청 모델"""
    inputs: List[Dict[str, Any]] = Field(
        ..., 
        description="여러 개의 입력을 담은 리스트",
        examples=[[{"text": "hi"}, {"text": "hello"}]]
    )
    config: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="전체/개별 입력에 공통으로 적용될 설정 값",
        examples=[{"configurable": {"thread_id": "batch_1"}}]
    )

class AgentBatchResponse(BaseModel):
    """배치 에이전트 실행 결과 응답 모델"""
    results: Optional[List[Any]] = Field(default=None, description="에이전트 배치 실행 결과 리스트")
    status: str = Field(default="ok", description="실행 상태 (ok, error)")
    error: Optional[str] = Field(default=None, description="에러 메시지 (발생 시)")
