import pytest
from httpx import AsyncClient, ASGITransport
import json
from src.core.server import create_agent_app

# --- Mocking Graph Object ---
class MockGraph:
    async def ainvoke(self, input, config=None):
        return {"response": f"Mock {input.get('text')}"}
    
    async def astream(self, input, config=None):
        yield {"chunk": "1"}
        yield {"chunk": "2"}
        
    async def abatch(self, inputs, config=None):
        return [{"response": f"Mock {i.get('text')}"} for i in inputs]

@pytest.fixture
def test_app():
    return create_agent_app(MockGraph())

@pytest.mark.asyncio
async def test_invoke(test_app):
    """/invoke 엔드포인트 정상 동작 검증"""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        response = await ac.post("/invoke", json={"input": {"text": "hello"}})
    assert response.status_code == 200
    assert response.json() == {"result": {"response": "Mock hello"}, "status": "ok", "error": None}

@pytest.mark.asyncio
async def test_stream(test_app):
    """/stream 스트리밍 이벤트 스트림 포맷 및 컨텐츠 정상 검증"""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        response = await ac.post("/stream", json={"input": {"text": "hello"}})
    assert response.status_code == 200
    text = response.text
    assert "data: {\"chunk\": \"1\"}" in text
    assert "data: {\"chunk\": \"2\"}" in text
    assert "data: {\"__end__\": true}" in text

@pytest.mark.asyncio
async def test_invoke_batch(test_app):
    """/invoke_batch 멀티 인풋 병렬/배치 처리 정상 검증"""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        response = await ac.post("/invoke_batch", json={"inputs": [{"text": "a"}, {"text": "b"}]})
    assert response.status_code == 200
    assert response.json() == {"results": [{"response": "Mock a"}, {"response": "Mock b"}], "status": "ok", "error": None}

@pytest.mark.asyncio
async def test_invoke_stream_batch(test_app):
    """/invoke_stream_batch 병합 스트리밍 검증"""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        response = await ac.post("/invoke_stream_batch", json={"inputs": [{"text": "a"}, {"text": "b"}]})
    assert response.status_code == 200
    text = response.text
    # Check if index 0 and 1 streams both outputted chunk 1
    assert "data: {\"index\": 0, \"event\": {\"chunk\": \"1\"}}" in text
    assert "data: {\"index\": 1, \"event\": {\"chunk\": \"1\"}}" in text
    # Check that both indicated completion
    assert "data: {\"index\": 0, \"done\": true}" in text
    assert "data: {\"index\": 1, \"done\": true}" in text
