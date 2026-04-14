import pytest
import httpx
from unittest.mock import patch, MagicMock
from src.core.server import create_agent_app
from src.common.middleware.auth import verify_credentials_with_authentik
from src.common.configs.settings import get_settings

@pytest.mark.asyncio
async def test_verify_credentials_with_authentik_fail_no_authentik():
    # Without a real Authentik running and without mocking, this should return None
    username = "user01"
    password = "user01"
    
    # We need to make sure settings.authentik_token_url is not set or unreachable
    with patch("src.common.middleware.auth.settings") as mock_settings:
        mock_settings.authentik_token_url = "http://localhost:9999/unreachable"
        result = await verify_credentials_with_authentik(username, password)
        assert result is None

@pytest.mark.asyncio
async def test_token_endpoint_user01_success_mocked():
    # Testing the /token endpoint with mocked Authentik success
    from fastapi.testclient import TestClient
    from src.core.server import create_agent_app
    
    # Mock graph
    mock_graph = MagicMock()
    app = create_agent_app(mock_graph)
    client = TestClient(app)
    
    # Mock verify_credentials_with_authentik to return success for user01
    mock_user_info = {"sub": "user01", "name": "Test User 01", "groups": ["users"]}
    
    with patch("src.core.server.verify_credentials_with_authentik", return_value=mock_user_info):
        response = client.post(
            "/token",
            data={"username": "user01", "password": "user01"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # Now verify if we can use this token to access a protected endpoint
        token = data["access_token"]
        response = client.post(
            "/invoke",
            json={"input": {"message": "hello"}},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should be 200 now (auth passed)
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_token_endpoint_user01_fail_incorrect_credentials():
    # Testing the /token endpoint with incorrect credentials
    from fastapi.testclient import TestClient
    from src.core.server import create_agent_app
    
    mock_graph = MagicMock()
    app = create_agent_app(mock_graph)
    client = TestClient(app)
    
    with patch("src.core.server.verify_credentials_with_authentik", return_value=None):
        response = client.post(
            "/token",
            data={"username": "user01", "password": "wrongpassword"}
        )
        
        # Should be 401 Unauthorized
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_protected_endpoint_unauthorized():
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
