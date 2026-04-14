import pytest
import httpx
from unittest.mock import patch, MagicMock
from src.core.server import create_agent_app
from src.common.middleware.auth import verify_credentials_with_authentik
from src.common.configs.settings import get_settings

@pytest.mark.asyncio
async def test_verify_credentials_with_authentik_user01_fail_without_authentik():
    # Without a real Authentik running, this should return None or raise an exception
    # This is our Red phase test
    username = "user01"
    password = "user01"
    result = await verify_credentials_with_authentik(username, password)
    assert result is None

@pytest.mark.asyncio
async def test_token_endpoint_user01_red():
    # Testing the /token endpoint with user01/user01
    # Should FAIL (fail the assertion) because Authentik is not reachable/configured correctly in test env
    from fastapi.testclient import TestClient
    from src.core.server import create_agent_app
    
    # Mock graph
    mock_graph = MagicMock()
    app = create_agent_app(mock_graph)
    client = TestClient(app)
    
    response = client.post(
        "/token",
        data={"username": "user01", "password": "user01"}
    )
    
    # We expect this to fail (it returns 401) during the Red phase
    # because we haven't mocked a successful Authentik response yet.
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_protected_endpoint_red():
    # Should return 401 if token is missing or invalid
    from fastapi.testclient import TestClient
    from src.core.server import create_agent_app
    
    # Mock graph
    mock_graph = MagicMock()
    app = create_agent_app(mock_graph)
    client = TestClient(app)
    
    # POST to /invoke without Auth header
    response = client.post("/invoke", json={"input": {}})
    
    # This should pass if auth middleware is correctly applied
    assert response.status_code == 401
