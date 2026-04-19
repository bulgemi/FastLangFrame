import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from src.core.server import create_agent_app
import src.core.server as server_module
import src.common.middleware.auth as auth_module

@pytest.fixture
def test_app():
    # Mock graph to avoid ChatOpenAI initialization
    mock_graph = AsyncMock()
    return create_agent_app(mock_graph)

@pytest.mark.asyncio
async def test_protected_endpoint_no_auth(test_app):
    """Endpoints should return 401 without any authorization header"""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        response = await ac.post("/invoke", json={"input": {"messages": [{"role": "user", "content": "hi"}]}})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_protected_endpoint_invalid_token(test_app):
    """Endpoints should return 401 with an invalid token"""
    # Temporarily inject Authelia settings without replacing the whole object
    original_url_server = server_module.settings.authelia_introspection_url
    server_module.settings.authelia_introspection_url = "http://authelia:9091/api/oidc/introspection"
    
    try:
        # We patch where it's used - in src.core.server (imported from auth)
        with patch("src.core.server.verify_token_with_authelia") as mock_verify:
            mock_verify.side_effect = HTTPException(status_code=401, detail="Invalid token")
            async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
                response = await ac.post(
                    "/invoke", 
                    json={"input": {"messages": [{"role": "user", "content": "hi"}]}},
                    headers={"Authorization": "Bearer invalid"}
                )
            assert response.status_code == 401
    finally:
        server_module.settings.authelia_introspection_url = original_url_server

@pytest.mark.asyncio
async def test_protected_endpoint_valid_token(test_app):
    """Endpoints should allow access with a valid Authelia token"""
    mock_payload = {"active": True, "sub": "user01"}
    
    # Temporarily inject Authelia settings
    original_url_server = server_module.settings.authelia_introspection_url
    server_module.settings.authelia_introspection_url = "http://authelia:9091/api/oidc/introspection"

    try:
        with patch("src.core.server.verify_token_with_authelia", return_value=mock_payload):
            async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
                response = await ac.post(
                    "/invoke", 
                    json={"input": {"messages": [{"role": "user", "content": "hi"}]}},
                    headers={"Authorization": "Bearer valid_token"}
                )
            assert response.status_code == 200
    finally:
        server_module.settings.authelia_introspection_url = original_url_server
