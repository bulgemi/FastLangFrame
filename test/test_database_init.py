import pytest
from unittest.mock import MagicMock, patch
from src.utils.connectors.db.database import Database
from src.common.configs.settings import FastLangFrameSettings

def test_database_engine_creation():
    """Test that Database correctly initializes engines using settings."""
    settings = FastLangFrameSettings(
        database_driver="postgresql",
        database_host="test-host",
        database_port=5432,
        database_username="test-user",
        database_password="test-password",
        database_dbname="test-db"
    )
    
    with patch("src.utils.connectors.db.database.engine_from_config") as mock_engine_from_config:
        mock_engine = MagicMock()
        mock_engine_from_config.return_value = mock_engine
        
        db = Database(settings=settings)
        engine = db.get_engine()
        
        assert engine == mock_engine
        mock_engine_from_config.assert_called_once()
        # Verify the config passed to engine_from_config contains our values
        args, kwargs = mock_engine_from_config.call_args
        config = args[0]
        assert "database.url" in config
        assert "postgresql+psycopg://test-user:test-password@test-host:5432/test-db" in config["database.url"]

def test_database_async_engine_creation():
    """Test that Database correctly initializes async engines using settings."""
    settings = FastLangFrameSettings(
        database_driver="postgresql-async",
        database_host="test-host",
        database_port=5432,
        database_username="test-user",
        database_password="test-password",
        database_dbname="test-db"
    )
    
    with patch("src.utils.connectors.db.database.async_engine_from_config") as mock_async_engine_from_config:
        mock_engine = MagicMock()
        mock_async_engine_from_config.return_value = mock_engine
        
        db = Database(settings=settings)
        engine = db.get_async_engine()
        
        assert engine == mock_engine
        mock_async_engine_from_config.assert_called_once()
        args, kwargs = mock_async_engine_from_config.call_args
        config = args[0]
        assert "database.url" in config
        assert "postgresql+asyncpg://test-user:test-password@test-host:5432/test-db" in config["database.url"]
