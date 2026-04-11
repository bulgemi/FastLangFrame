import pytest
from src.common.configs.settings import get_settings, FastLangFrameSettings

def test_settings_initialization():
    settings = get_settings()
    assert isinstance(settings, FastLangFrameSettings)
    assert settings.llm_api_key == "default_key"
    assert settings.model_name == "gpt-4o"
    assert settings.llm_endpoint == "https://api.openai.com/v1"

def test_oauth_settings():
    settings = get_settings()
    assert hasattr(settings, "authentik_url")
    assert hasattr(settings, "authentik_client_id")
    assert hasattr(settings, "authentik_client_secret")
    assert hasattr(settings, "authentik_jwks_url")
    assert hasattr(settings, "authentik_auth_url")
    assert hasattr(settings, "authentik_token_url")
    assert hasattr(settings, "authentik_userinfo_url")
    assert hasattr(settings, "authentik_callback_url")
