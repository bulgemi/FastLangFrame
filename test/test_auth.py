import pytest
import jwt
from unittest.mock import patch, MagicMock
from fastapi import HTTPException, status
from src.common.middleware.auth import verify_token, RoleChecker
from src.common.configs.settings import get_settings

@pytest.mark.asyncio
async def test_verify_token_invalid_jwt():
    # Test with an invalid JWT string
    with patch("src.common.middleware.auth.settings") as mock_settings:
        mock_settings.jwt_secret_key = "secret"
        mock_settings.jwt_algorithm = "HS256"
        with pytest.raises(HTTPException) as excinfo:
            await verify_token("not-a-valid-jwt")
        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid token" in excinfo.value.detail

@pytest.mark.asyncio
async def test_verify_token_success_mocked():
    # Create a dummy JWT for testing
    secret = "secret_key_at_least_32_chars_long_for_validation"
    payload = {"sub": "user123", "name": "Test User", "groups": ["admins"]}
    token = jwt.encode(payload, secret, algorithm="HS256")
    
    with patch("src.common.middleware.auth.settings") as mock_settings:
        mock_settings.jwt_secret_key = secret
        mock_settings.jwt_algorithm = "HS256"
        result = await verify_token(token)
        assert result["sub"] == "user123"
        assert "admins" in result["groups"]

@pytest.mark.asyncio
async def test_role_checker_success():
    payload = {"sub": "user123", "groups": ["admins", "users"]}
    checker = RoleChecker(allowed_roles=["admins"])
    # Should not raise exception
    await checker(payload)

@pytest.mark.asyncio
async def test_role_checker_fail():
    payload = {"sub": "user123", "groups": ["users"]}
    checker = RoleChecker(allowed_roles=["admins"])
    with pytest.raises(HTTPException) as excinfo:
        await checker(payload)
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Permission denied" in excinfo.value.detail

@pytest.mark.asyncio
async def test_verify_authelia_token_success():
    """Test successful validation of an Authelia-issued token using a public key."""
    from src.common.middleware.auth import verify_authelia_token
    
    # This should be implemented to decode JWT using a public key
    # For the test, we'll mock the public key and the decoded payload
    token = "some.authelia.token"
    mock_payload = {"sub": "user01", "iss": "https://auth.example.com", "aud": "fastapi"}
    
    with patch("src.common.middleware.auth.jwt.decode", return_value=mock_payload):
        with patch("src.common.middleware.auth.settings") as mock_settings:
            mock_settings.authelia_url = "https://auth.example.com"
            mock_settings.authelia_client_id = "fastapi"
            
            result = await verify_authelia_token(token)
            assert result["sub"] == "user01"

@pytest.mark.asyncio
async def test_verify_authelia_token_expired():
    """Test validation failure for an expired Authelia token."""
    from src.common.middleware.auth import verify_authelia_token
    token = "expired.token"
    
    with patch("src.common.middleware.auth.jwt.decode", side_effect=jwt.ExpiredSignatureError):
        with pytest.raises(HTTPException) as excinfo:
            await verify_authelia_token(token)
        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Token has expired" in excinfo.value.detail

@pytest.mark.asyncio
async def test_verify_authelia_token_invalid_issuer():
    """Test validation failure for an invalid issuer."""
    from src.common.middleware.auth import verify_authelia_token
    token = "invalid.issuer.token"
    mock_payload = {"sub": "user01", "iss": "https://malicious.example.com", "aud": "fastapi"}
    
    with patch("src.common.middleware.auth.jwt.decode", return_value=mock_payload):
        with patch("src.common.middleware.auth.settings") as mock_settings:
            mock_settings.authelia_url = "https://auth.example.com"
            
            with pytest.raises(HTTPException) as excinfo:
                await verify_authelia_token(token)
            assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid issuer" in excinfo.value.detail
