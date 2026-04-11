import pytest
from unittest.mock import patch, MagicMock
from src.utils.connectors.llm.llm_client import get_langchain_chat_model

def test_gemini_fails_fast_on_missing_api_key():
    """Test that Gemini provider fails fast if no valid API key is found."""
    with patch("src.utils.connectors.llm.llm_client.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.llm_provider = "gemini"
        mock_settings.google_api_key = None
        mock_settings.llm_api_key = "default_key"
        mock_settings.model_name = "gemini-1.5-flash"
        mock_settings.azure_openai_api_key = None
        mock_settings.azure_openai_endpoint = None
        mock_settings.anthropic_api_key = None
        mock_settings.llm_timeout_sec = 60
        mock_settings.llm_endpoint = "https://api.openai.com/v1"
        mock_get_settings.return_value = mock_settings

        # This should currently NOT raise an exception, but we WANT it to raise a ValueError.
        # So we expect it to fail if it DOESN'T raise an exception (Red Phase).
        with pytest.raises(ValueError, match="Gemini API Key is not set or invalid"):
            get_langchain_chat_model()
