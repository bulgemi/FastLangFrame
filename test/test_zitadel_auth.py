import pytest
import httpx
from unittest.mock import patch, MagicMock
from src.core.server import create_agent_app
from src.common.middleware.auth import verify_credentials_with_zitadel
from src.common.configs.settings import get_settings

@pytest.mark.asyncio
async def test_verify_credentials_with_zitadel_fail_no_zitadel():
    username = "user01"
    password = "user01"
    
    with patch("src.common.middleware.auth.settings") as mock_settings:
        mock_settings.zitadel_token_url = "http://localhost:9999/unreachable"
        result = await verify_credentials_with_zitadel(username, password)
        assert result is None

@pytest.mark.asyncio
async def test_token_endpoint_user01_success_mocked_zitadel():
    from fastapi.testclient import TestClient
    from src.core.server import create_agent_app
    
    mock_graph = MagicMock()
    app = create_agent_app(mock_graph)
    client = TestClient(app)
    
    # Mock user info returned by Zitadel
    mock_user_info = {"sub": "user01", "name": "Test User 01", "groups": ["users"]}
    
    with patch("src.core.server.verify_credentials_with_zitadel", return_value=mock_user_info):
        response = client.post(
            "/token",
            data={"username": "user01", "password": "user01"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_token_endpoint_user01_fail_incorrect_credentials():
    from fastapi.testclient import TestClient
    from src.core.server import create_agent_app
    
    mock_graph = MagicMock()
    app = create_agent_app(mock_graph)
    client = TestClient(app)
    
    with patch("src.core.server.verify_credentials_with_zitadel", return_value=None):
        response = client.post(
            "/token",
            data={"username": "user01", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
