import jwt
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from src.common.configs.settings import get_settings

settings = get_settings()

# We'll use Authorization Code Flow as per the plan for Streamlit -> Authentik
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=settings.authentik_auth_url or "",
    tokenUrl=settings.authentik_token_url or ""
)

async def verify_token(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Validates a JWT token issued by Authentik.
    """
    if not settings.authentik_jwks_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentik JWKS URL not configured"
        )
    
    try:
        # In a real implementation, we should fetch and cache the JWKS.
        # For now, we'll demonstrate the structure.
        # Real validation would use jwt.PyJWKClient(settings.authentik_jwks_url)
        
        # Placeholder for actual validation logic
        payload = jwt.decode(token, options={"verify_signature": False}) # Temporary for initial structure
        return payload
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

class RoleChecker:
    """
    A dependency that checks if the authenticated user has any of the allowed roles.
    Authentik typically maps groups to the 'groups' claim in the JWT.
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
