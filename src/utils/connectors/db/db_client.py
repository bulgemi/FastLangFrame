import logging
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.common.configs.settings import FastLangFrameSettings, get_settings

logger = logging.getLogger(__name__)

class DBClient:
    """Async SQLAlchemy Database connector"""
    def __init__(self, settings: Optional[FastLangFrameSettings] = None):
        self.settings = settings or get_settings()
        self.engine = None
        self.session_factory = None
        if self.settings.database_url:
            self.engine = create_async_engine(self.settings.database_url, echo=False)
            self.session_factory = sessionmaker(
                bind=self.engine, class_=AsyncSession, expire_on_commit=False
            )

    async def get_session(self) -> AsyncSession:
        if not self.session_factory:
            raise ValueError("Database URL not configured")
        async with self.session_factory() as session:
            yield session
