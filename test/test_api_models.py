import pytest
from pydantic import ValidationError
from src.core.api_models import AgentInvokeRequest, AgentBatchRequest

def test_agent_invoke_request_valid():
    """정상적인 단일 요청 객체 생성 테스트"""
    req = AgentInvokeRequest(input={"message": "hello"}, config={"tag": "v1"})
    assert req.input == {"message": "hello"}
    assert req.config == {"tag": "v1"}

def test_agent_invoke_request_default_config():
    """config 필드가 누락되었을 때 기본값 테스트"""
    req = AgentInvokeRequest(input={"k": "v"})
    assert req.input == {"k": "v"}
    assert req.config is None

def test_agent_invoke_request_missing_input():
    """필수 필드인 input 누락 시 ValidationError 발생 여부 검증"""
    with pytest.raises(ValidationError):
        AgentInvokeRequest(config={"tag": "v1"})

def test_agent_batch_request_valid():
    """정상적인 배치 요청 객체 생성 테스트"""
    req = AgentBatchRequest(inputs=[{"m": "1"}, {"m": "2"}], config={"global": True})
    assert len(req.inputs) == 2
    assert req.inputs[1] == {"m": "2"}
    assert req.config == {"global": True}

def test_agent_batch_request_missing_inputs():
    """필수 필드인 inputs 누락 시 ValidationError 발생 검증"""
    with pytest.raises(ValidationError):
        AgentBatchRequest()
