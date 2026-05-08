import os
import pytest
from src.common.configs.settings import FastLangFrameSettings

def test_db_settings_loading_defaults():
    """Test that database settings have reasonable defaults or load from env if present."""
    settings = FastLangFrameSettings()
    # Check if database fields exist in FastLangFrameSettings
    # We use getattr because we expect them to possibly not exist yet (TDD)
    assert hasattr(settings, "database_driver")
    assert hasattr(settings, "database_host")
    assert hasattr(settings, "database_port")
    assert hasattr(settings, "database_dbname")
    assert hasattr(settings, "database_username")
    assert hasattr(settings, "database_password")
    assert hasattr(settings, "database_schema")

def test_db_url_construction():
    """Test that the database URL is correctly constructed from components."""
    # Mocking environment for specific test
    os.environ["DATABASE_DRIVER"] = "postgresql"
    os.environ["DATABASE_HOST"] = "localhost"
    os.environ["DATABASE_PORT"] = "5432"
    os.environ["DATABASE_DBNAME"] = "testdb"
    os.environ["DATABASE_USERNAME"] = "user"
    os.environ["DATABASE_PASSWORD"] = "pass"
    
    # Reload settings to pick up new env vars
    settings = FastLangFrameSettings()
    
    # We'll use postgresql instead of postgresql-async for the test expectation
    # if the driver is specified as postgresql
    expected_url = "postgresql://user:pass@localhost:5432/testdb"
    assert hasattr(settings, "database_url")
    assert settings.database_url == expected_url
