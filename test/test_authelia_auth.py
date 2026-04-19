import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from src.common.middleware.auth import verify_token_with_authelia
import src.common.middleware.auth as auth_module

@pytest.fixture
def mock_authelia_settings():
    # Store original settings
    original_url = auth_module.settings.authelia_introspection_url
    original_id = auth_module.settings.authelia_client_id
    original_secret = auth_module.settings.authelia_client_secret
    
    # Inject mock settings
    auth_module.settings.authelia_introspection_url = "http://authelia:9091/api/oidc/introspection"
    auth_module.settings.authelia_client_id = "fastapi"
    auth_module.settings.authelia_client_secret = "fastapi_secret"
    
    yield
    
    # Restore original settings
    auth_module.settings.authelia_introspection_url = original_url
    auth_module.settings.authelia_client_id = original_id
    auth_module.settings.authelia_client_secret = original_secret

@pytest.mark.asyncio
async def test_verify_token_with_authelia_valid(mock_authelia_settings):
    """Test successful token validation with Authelia introspection"""
    token = "valid_token"
    mock_response = MagicMock() # Use MagicMock for the response object
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "active": True,
        "sub": "user01",
        "username": "user01",
        "scope": "openid profile email"
    }

    # Patch httpx.AsyncClient.post with an AsyncMock that returns our MagicMock response
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        payload = await verify_token_with_authelia(token)
        assert payload["active"] is True
        assert payload["sub"] == "user01"

@pytest.mark.asyncio
async def test_verify_token_with_authelia_invalid(mock_authelia_settings):
    """Test token validation failure (inactive token)"""
    token = "invalid_token"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"active": False}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        with pytest.raises(HTTPException) as excinfo:
            await verify_token_with_authelia(token)
        assert excinfo.value.status_code == 401
        assert "Invalid or inactive token" in str(excinfo.value.detail)

@pytest.mark.asyncio
async def test_verify_token_with_authelia_error(mock_authelia_settings):
    """Test Authelia introspection endpoint error"""
    token = "any_token"
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        with pytest.raises(HTTPException) as excinfo:
            await verify_token_with_authelia(token)
        assert excinfo.value.status_code == 401
        assert "Failed to verify token" in str(excinfo.value.detail)
