import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.utils.connectors.db.database import DBClient
from src.common.configs.settings import FastLangFrameSettings
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.anyio
async def test_db_client_get_session_mocked():
    # Setup mock session
    mock_session = AsyncMock(spec=AsyncSession)
    
    settings = FastLangFrameSettings(database_url="sqlite+aiosqlite:///:memory:")
    client = DBClient(settings=settings)
    
    # Define an async generator to be yielded by the mock
    async def mock_async_gen(*args, **kwargs):
        yield mock_session

    with patch.object(client, "get_async_session", side_effect=mock_async_gen):
        # Check if get_session yields the mock session
        sessions = []
        async for session in client.get_session():
            sessions.append(session)
        
        assert len(sessions) == 1
        assert sessions[0] == mock_session

@pytest.mark.anyio
async def test_db_client_no_url():
    # Setting database_driver="" will result in database_url returning None/empty
    settings = FastLangFrameSettings(database_driver="")
    client = DBClient(settings=settings)
    
    with pytest.raises(ValueError, match="Database URL not configured"):
        async for _ in client.get_session():
            pass
