import pytest
import httpx
from unittest.mock import patch, MagicMock
from src.core.server import create_agent_app
# Try to import the new function, it should fail or we mock it as non-existent
try:
    from src.common.middleware.auth import verify_credentials_with_zitadel
except ImportError:
    verify_credentials_with_zitadel = None
from src.common.configs.settings import get_settings

@pytest.mark.asyncio
async def test_verify_credentials_with_zitadel_exists():
    # This defines our first Red task: the function should exist
    assert verify_credentials_with_zitadel is not None

@pytest.mark.asyncio
async def test_token_endpoint_user01_success_mocked_zitadel():
    from fastapi.testclient import TestClient
    from src.core.server import create_agent_app
    
    mock_graph = MagicMock()
    app = create_agent_app(mock_graph)
    client = TestClient(app)
    
    # Mock user info returned by Zitadel
    mock_user_info = {"sub": "user01", "name": "Test User 01", "groups": ["users"]}
    
    if verify_credentials_with_zitadel:
        with patch("src.core.server.verify_credentials_with_zitadel", return_value=mock_user_info):
            response = client.post(
                "/token",
                data={"username": "user01", "password": "user01"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
    else:
        pytest.fail("verify_credentials_with_zitadel is not implemented yet")

@pytest.mark.asyncio
async def test_token_endpoint_user01_fail_zitadel_not_configured():
    from fastapi.testclient import TestClient
    from src.core.server import create_agent_app
    
    mock_graph = MagicMock()
    app = create_agent_app(mock_graph)
    client = TestClient(app)
    
    # When Zitadel is not configured or fails, it should return 401
    # We mock the implementation that we haven't written yet
    if verify_credentials_with_zitadel:
        with patch("src.core.server.verify_credentials_with_zitadel", return_value=None):
            response = client.post(
                "/token",
                data={"username": "user01", "password": "user01"}
            )
            assert response.status_code == 401
    else:
        # If it doesn't exist, the server probably still uses verify_credentials_with_authelia
        # which will fail anyway, but our goal is to show the NEW behavior fails.
        pytest.fail("verify_credentials_with_zitadel is not implemented yet")
