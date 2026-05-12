import pytest
from unittest.mock import MagicMock, patch
from src.utils.observability import get_langfuse_callback

def test_get_langfuse_callback_no_config(monkeypatch):
    # Ensure no config is present
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    
    # Should return None if config is missing
    callback = get_langfuse_callback()
    assert callback is None

def test_get_langfuse_callback_with_metadata(monkeypatch):
    with patch("src.utils.observability.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.langfuse_secret_key = "sk-test"
        mock_settings.langfuse_public_key = "pk-test"
        mock_settings.langfuse_host = "http://test"
        mock_get_settings.return_value = mock_settings
        
        with patch("src.utils.observability.CallbackHandler") as mock_handler:
            callback = get_langfuse_callback(
                user_id="user-123",
                session_id="sess-456",
                tags=["test-tag"]
            )
            
            assert callback is not None
            mock_handler.assert_called_once()
            args, kwargs = mock_handler.call_args
            assert kwargs["secret_key"] == "sk-test"
            assert kwargs["public_key"] == "pk-test"
            assert kwargs["host"] == "http://test"
            assert kwargs["user_id"] == "user-123"
            assert kwargs["session_id"] == "sess-456"
            assert "test-tag" in kwargs["tags"]
