import os
import pytest
from src.common.configs.settings import FastLangFrameSettings

def test_langfuse_settings_loading(monkeypatch):
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-test-123")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-test-456")
    monkeypatch.setenv("LANGFUSE_HOST", "http://test-host:3000")
    
    # We need to re-instantiate settings because get_settings() uses a singleton
    settings = FastLangFrameSettings()
    
    assert settings.langfuse_secret_key == "sk-test-123"
    assert settings.langfuse_public_key == "pk-test-456"
    assert settings.langfuse_host == "http://test-host:3000"

def test_langfuse_settings_default():
    settings = FastLangFrameSettings()
    # If not set in .env or environment, they should be None or default
    # Assuming we want them optional to fail gracefully
    assert hasattr(settings, "langfuse_secret_key")
    assert hasattr(settings, "langfuse_public_key")
    assert hasattr(settings, "langfuse_host")
