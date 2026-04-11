import pytest
from unittest.mock import MagicMock, patch
from pydantic import SecretStr
from src.utils.connectors.llm.llm_client import get_llm_by_role, get_langchain_chat_model

@pytest.fixture
def mock_settings():
    with patch("src.utils.connectors.llm.llm_client.get_settings") as mock:
        settings = MagicMock()
        settings.llm_provider = "openai"
        settings.model_name = "gpt-4o"
        settings.llm_api_key = "fake-key"
        settings.llm_endpoint = "https://api.openai.com/v1"
        settings.llm_timeout_sec = 60
        settings.azure_openai_api_key = None
        settings.azure_openai_endpoint = None
        settings.anthropic_api_key = "fake-anthropic-key"
        settings.anthropic_api_url = None
        settings.google_api_key = "fake-google-key"
        settings.llm_models = {
            "fast": {"provider": "openai", "model": "gpt-4o-mini"},
            "smart": {"provider": "anthropic", "model": "claude-3-5-sonnet-20240620"},
            "gemini": {"provider": "google", "model": "gemini-1.5-pro"}
        }
        mock.return_value = settings
        yield settings

def test_get_llm_by_role_openai(mock_settings):
    llm = get_llm_by_role("fast")
    assert llm.model_name == "gpt-4o-mini"

def test_get_llm_by_role_anthropic(mock_settings):
    # This specifically tests the fix for model_name in ChatAnthropic
    llm = get_llm_by_role("smart")
    # In langchain-anthropic 1.4.0, it should be accessible via .model 
    # but we provided it via model_name= in the constructor.
    assert llm.model == "claude-3-5-sonnet-20240620"

def test_get_llm_by_role_google(mock_settings):
    llm = get_llm_by_role("gemini")
    assert llm.model == "gemini-1.5-pro"

def test_get_langchain_chat_model_anthropic(mock_settings):
    # Test get_langchain_chat_model for anthropic
    mock_settings.llm_provider = "anthropic"
    llm = get_langchain_chat_model(model_name="claude-3-opus-20240229")
    assert llm.model == "claude-3-opus-20240229"
