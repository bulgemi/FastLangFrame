import streamlit as st
import httpx
import jwt
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from src.common.configs.settings import get_settings

settings = get_settings()

def get_login_url() -> str:
    """Generates the Authentik login URL"""
    params = {
        "client_id": settings.authentik_client_id,
        "redirect_uri": settings.authentik_callback_url,
        "response_type": "code",
        "scope": "openid profile email",
        # State should be used in production for security
        "state": "random_state_string" 
    }
    return f"{settings.authentik_auth_url}?{urlencode(params)}"

def exchange_code_for_token(code: str) -> Optional[Dict[str, Any]]:
    """Exchanges the authorization code for an access token"""
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": settings.authentik_client_id,
        "client_secret": settings.authentik_client_secret,
        "redirect_uri": settings.authentik_callback_url,
    }
    
    with httpx.Client() as client:
        response = client.post(settings.authentik_token_url, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to exchange token: {response.text}")
            return None

def get_user_info(access_token: str) -> Optional[Dict[str, Any]]:
    """Fetches user info from Authentik using the access token"""
    headers = {"Authorization": f"Bearer {access_token}"}
    with httpx.Client() as client:
        response = client.get(settings.authentik_userinfo_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

def check_auth():
    """ Main entry point to check authentication state in Streamlit """
    if not settings.authentik_auth_url:
        # OAuth not configured, skip
        return True

    if "auth_token" not in st.session_state:
        # Check if we are returning from Authentik with a code
        query_params = st.query_params
        if "code" in query_params:
            code = query_params["code"]
            token_data = exchange_code_for_token(code)
            if token_data:
                st.session_state.auth_token = token_data.get("access_token")
                st.session_state.id_token = token_data.get("id_token")
                # Clear query params
                st.query_params.clear()
                st.rerun()
        
        # Still no token, show login button
        st.warning("Please log in to continue.")
        st.link_button("Login with Authentik", get_login_url())
        st.stop()
    
    # Optional: Verify token and get user info
    if "user_info" not in st.session_state:
        user_info = get_user_info(st.session_state.auth_token)
        if user_info:
            st.session_state.user_info = user_info
        else:
            # Token might be expired
            del st.session_state.auth_token
            st.rerun()

    return True
