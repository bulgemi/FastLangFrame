import pytest
from unittest.mock import MagicMock, patch
from src.utils.observability import (
    get_langfuse_callback, 
    get_langfuse_client, 
    prepare_langfuse_metadata
)

def test_get_langfuse_callback_no_config(monkeypatch):
    # Ensure no config is present
    with patch("src.utils.observability.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.langfuse_secret_key = None
        mock_settings.langfuse_public_key = None
        mock_get_settings.return_value = mock_settings
        
        # Reset singleton for test
        with patch("src.utils.observability._langfuse_client", None):
            callback = get_langfuse_callback()
            assert callback is None

def test_get_langfuse_callback_with_client(monkeypatch):
    with patch("src.utils.observability.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.langfuse_secret_key = "sk-test"
        mock_settings.langfuse_public_key = "pk-test"
        mock_settings.langfuse_host = "http://test"
        mock_get_settings.return_value = mock_settings
        
        # Reset singleton for test
        with patch("src.utils.observability._langfuse_client", None):
            with patch("src.utils.observability.Langfuse") as mock_langfuse:
                with patch("src.utils.observability.CallbackHandler") as mock_handler:
                    callback = get_langfuse_callback()
                    
                    assert callback is not None
                    mock_langfuse.assert_called_once()
                    mock_handler.assert_called_once_with(
                        public_key="pk-test",
                        update_trace=True
                    )

def test_prepare_langfuse_metadata():
    metadata = prepare_langfuse_metadata(
        user_id="user-1",
        session_id="sess-1",
        tags=["tag-1"],
        existing_metadata={"other": "data"}
    )
    
    assert metadata["langfuse_user_id"] == "user-1"
    assert metadata["langfuse_session_id"] == "sess-1"
    assert metadata["langfuse_tags"] == ["tag-1"]
    assert metadata["other"] == "data"
