import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.utils.connectors.db.db_client import DBClient
from src.common.configs.settings import FastLangFrameSettings
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.anyio
async def test_db_client_get_session_mocked():
    # Setup mock session and session factory
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None
    
    mock_session_factory = MagicMock()
    mock_session_factory.return_value = mock_session
    
    # Patch create_async_engine and sessionmaker to avoid and database driver issues
    with patch("src.utils.connectors.db.db_client.create_async_engine"), \
         patch("src.utils.connectors.db.db_client.async_sessionmaker"):
        
        settings = FastLangFrameSettings(database_url="sqlite+aiosqlite:///:memory:")
        client = DBClient(settings=settings)
        # Manually inject the mock session factory
        client.session_factory = mock_session_factory
        
        # Check if get_session yields the mock session
        sessions = []
        async for session in client.get_session():
            sessions.append(session)
        
        assert len(sessions) == 1
        assert sessions[0] == mock_session
        mock_session_factory.assert_called_once()

@pytest.mark.anyio
async def test_db_client_no_url():
    # Patch create_async_engine and async_sessionmaker
    with patch("src.utils.connectors.db.db_client.create_async_engine"), \
         patch("src.utils.connectors.db.db_client.async_sessionmaker"):
        
        settings = FastLangFrameSettings(database_url="")
        client = DBClient(settings=settings)
        
        with pytest.raises(ValueError, match="Database URL not configured"):
            async for _ in client.get_session():
                pass
