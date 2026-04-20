import pytest
from httpx import AsyncClient, ASGITransport
import json
from unittest.mock import patch, AsyncMock
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
async def test_invoke_no_auth(test_app):
    """/invoke should return 401 without token"""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        response = await ac.post("/invoke", json={"input": {"text": "hello"}})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_invoke_with_valid_bearer(test_app):
    """
    /invoke should return 200 with a valid bearer token.
    This will fail in the Red phase until we implement local JWT validation
    and update the dependency.
    """
    # For now, we'll try to use verify_authelia_token which we just implemented
    # but the server doesn't use it yet.
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        response = await ac.post(
            "/invoke", 
            json={"input": {"text": "hello"}},
            headers={"Authorization": "Bearer some_valid_token"}
        )
    # In the Red phase, this might return 401 or 500 depending on current implementation
    assert response.status_code == 200
