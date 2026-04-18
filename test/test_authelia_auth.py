import pytest
import httpx
from unittest.mock import patch, MagicMock
from src.core.server import create_agent_app
from src.common.configs.settings import get_settings

# Try to import the new function, it should fail or we mock it as non-existent
try:
    from src.common.middleware.auth import verify_credentials_with_authelia
except ImportError:
    verify_credentials_with_authelia = None

@pytest.mark.asyncio
async def test_verify_credentials_with_authelia_exists():
    # This defines our first Red task: the function should exist
    assert verify_credentials_with_authelia is not None

@pytest.mark.asyncio
async def test_token_endpoint_user01_success_mocked_authelia():
    from fastapi.testclient import TestClient
    from src.core.server import create_agent_app
    
    mock_graph = MagicMock()
    app = create_agent_app(mock_graph)
    client = TestClient(app)
    
    # We want the server to eventually use verify_credentials_with_authelia
    # For Red phase, we'll see if we can force it to use a mock of the new function
    # (This will likely require server.py changes to be truly Red, but let's start with import failure)
    mock_user_info = {"sub": "user01", "name": "Test User 01", "groups": ["users"]}
    
    if verify_credentials_with_authelia:
        with patch("src.core.server.verify_credentials_with_authelia", return_value=mock_user_info):
            response = client.post(
                "/token",
                data={"username": "user01", "password": "user01"}
            )
            assert response.status_code == 200
    else:
        pytest.fail("verify_credentials_with_authelia is not implemented yet")
