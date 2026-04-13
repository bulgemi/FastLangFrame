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
