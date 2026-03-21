import pytest
from src.common.configs.settings import get_settings, FastLangFrameSettings

def test_settings_initialization():
    settings = get_settings()
    assert isinstance(settings, FastLangFrameSettings)
    assert settings.llm_api_key == "default_key"
    assert settings.model_name == "gpt-4o"
    assert settings.llm_endpoint == "https://api.openai.com/v1"
