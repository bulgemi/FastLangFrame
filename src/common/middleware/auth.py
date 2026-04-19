import jwt
import httpx
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.common.configs.settings import get_settings
from src.common.logging.logger_config import setup_logger

settings = get_settings()
logger = setup_logger(__name__)

# OAuth2PasswordBearer flow
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a native JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

async def verify_credentials_with_zitadel(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Verifies credentials against Zitadel using the password grant flow (back-channel).
    Returns the user info (token payload) if successful, None otherwise.
    """
    if not settings.zitadel_token_url:
        # If Zitadel is not configured, we might want a fallback or just fail
        return None

    try:
        async with httpx.AsyncClient() as client:
            data = {
                "grant_type": "password",
                "username": username,
                "password": password,
                "client_id": settings.zitadel_client_id,
                "client_secret": settings.zitadel_client_secret,
                "scope": "openid profile email groups" # Adjust scope as needed
            }
            response = await client.post(settings.zitadel_token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                # We can decode the Zitadel token to get user info/groups
                # and then map them to our native token.
                # For now, we'll just decode without verification (trusting Zitadel's response)
                payload = jwt.decode(access_token, options={"verify_signature": False})
                return payload
            else:
                logger.warning(f"Zitadel credential verification failed for user '{username}': {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error verifying credentials with Zitadel: {str(e)}")
        return None

async def verify_token(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Validates a native JWT token issued by this FastAPI server.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def verify_token_with_authelia(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Validates a token by calling Authelia's OIDC introspection endpoint.
    """
    if not settings.authelia_introspection_url:
        logger.error("AUTHELIA_INTROSPECTION_URL is not configured.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication server configuration error."
        )

    try:
        async with httpx.AsyncClient() as client:
            # Introspection typically requires client credentials via Basic Auth or POST body
            auth = (settings.authelia_client_id, settings.authelia_client_secret)
            data = {"token": token}
            
            response = await client.post(
                settings.authelia_introspection_url,
                auth=auth,
                data=data
            )
            
            if response.status_code == 200:
                payload = response.json()
                if payload.get("active") is True:
                    return payload
                else:
                    logger.warning("Token verification failed: Token is not active.")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or inactive token",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            else:
                logger.error(f"Authelia introspection failed: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to verify token with identity provider",
                    headers={"WWW-Authenticate": "Bearer"},
                )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during Authelia token introspection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification error",
            headers={"WWW-Authenticate": "Bearer"},
        )

class RoleChecker:
    """
    A dependency that checks if the authenticated user has any of the allowed roles.
    Zitadel typically maps groups to the 'groups' claim in the JWT.
    """
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, payload: Dict[str, Any] = Depends(verify_token)):
        user_roles = payload.get("groups", [])
        
        # Check if any of the user's roles match the allowed roles
        if not any(role in user_roles for role in self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required roles: {self.allowed_roles}"
            )
        
        return payload
