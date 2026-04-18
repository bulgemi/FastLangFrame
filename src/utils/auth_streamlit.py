import streamlit as st
import httpx
from typing import Optional, Dict, Any
from src.common.configs.settings import get_settings

settings = get_settings()

def login_with_password(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticates with the backend using username and password"""
    # Use relative or configured URL for the backend token endpoint
    # In production, this should be the full URL. For now, we'll use a relative path if possible, 
    # but Streamlit runs on a different port, so we need the backend URL.
    # We can assume the backend is at AUTHELIA_URL but on the FastAPI port (usually 8000)
    # or just use a new setting if needed. For now, let's use a common pattern.
    backend_url = settings.authelia_url.replace(":9091", ":8000") if settings.authelia_url else "http://localhost:8000"
    token_url = f"{backend_url}/token"
    
    data = {
        "username": username,
        "password": password,
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(token_url, data=data)
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Login failed: {response.json().get('detail', 'Unknown error')}")
                return None
    except Exception as e:
        st.error(f"Could not connect to auth server: {str(e)}")
        return None

def check_auth():
    """ Main entry point to check authentication state in Streamlit """
    # If no secret key is set, we might be in a dev mode without auth
    if settings.jwt_secret_key == "your_jwt_secret_key" and not settings.authelia_url:
        return True

    if "auth_token" not in st.session_state:
        st.title("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_state = st.form_submit_button("Login")
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    token_data = login_with_password(username, password)
                    if token_data:
                        st.session_state.auth_token = token_data.get("access_token")
                        # We could also decode the token here for user_info if needed
                        import jwt
                        payload = jwt.decode(st.session_state.auth_token, options={"verify_signature": False})
                        st.session_state.user_info = payload
                        st.rerun()
        st.stop()

    return True
