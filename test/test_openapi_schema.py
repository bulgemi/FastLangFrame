import pytest
from httpx import AsyncClient, ASGITransport
from src.core.server import create_agent_app

class MockGraph:
    async def ainvoke(self, input, config=None): return {"response": "ok"}
    async def astream(self, input, config=None): yield {}
    async def abatch(self, inputs, config=None): return []

@pytest.fixture
def test_app():
    return create_agent_app(MockGraph())

@pytest.mark.asyncio
async def test_openapi_schema_contains_examples(test_app):
    """OpenAPI JSON schema contains examples and descriptions for AgentInvokeRequest"""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        response = await ac.get("/openapi.json")
    
    assert response.status_code == 200
    schema = response.json()
    
    # Check AgentInvokeRequest
    agent_invoke_schema = schema["components"]["schemas"]["AgentInvokeRequest"]
    input_prop = agent_invoke_schema["properties"]["input"]
    
    # In Pydantic v2 + FastAPI, examples are typically here
    assert "examples" in input_prop
    assert {"text": "hi"} in input_prop["examples"]
    assert "description" in input_prop
    
    # Check AgentInvokeResponse
    assert "AgentInvokeResponse" in schema["components"]["schemas"]
    response_schema = schema["components"]["schemas"]["AgentInvokeResponse"]
    assert "result" in response_schema["properties"]
    assert "status" in response_schema["properties"]
    
    # Check if the /invoke endpoint documentation has the response model
    invoke_post = schema["paths"]["/invoke"]["post"]
    assert "responses" in invoke_post
    assert "200" in invoke_post["responses"]
    content = invoke_post["responses"]["200"]["content"]["application/json"]
    assert "AgentInvokeResponse" in content["schema"]["$ref"]
