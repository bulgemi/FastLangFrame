import pytest
from src.common.configs.settings import get_settings, FastLangFrameSettings

def test_settings_initialization():
    settings = get_settings()
    assert isinstance(settings, FastLangFrameSettings)
    assert settings.llm_api_key in ["default_key", "your_llm_api_key"]
    assert settings.model_name == "gpt-4o"
    assert settings.llm_endpoint == "https://api.openai.com/v1"

def test_oauth_settings():
    settings = get_settings()
    assert hasattr(settings, "jwt_secret_key")
    assert len(settings.jwt_secret_key) >= 32
    assert hasattr(settings, "jwt_algorithm")
    assert hasattr(settings, "zitadel_url")
    assert hasattr(settings, "zitadel_token_url")
