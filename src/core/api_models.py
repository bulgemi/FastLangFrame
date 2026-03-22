from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AgentInvokeRequest(BaseModel):
    """단일 에이전트 실행을 위한 요청 모델"""
    input: Dict[str, Any] = Field(..., description="에이전트에 전달될 입력 딕셔너리")
    config: Optional[Dict[str, Any]] = Field(default=None, description="실행 설정 값 (런타임 옵션 등)")

class AgentBatchRequest(BaseModel):
    """배치(다중) 에이전트 실행을 위한 요청 모델"""
    inputs: List[Dict[str, Any]] = Field(..., description="여러 개의 입력을 담은 리스트")
    config: Optional[Dict[str, Any]] = Field(default=None, description="전체/개별 입력에 공통으로 적용될 설정 값")
