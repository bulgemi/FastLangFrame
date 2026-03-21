import logging
from typing import Optional
from src.common.configs.settings import FastLangFrameSettings, get_settings

logger = logging.getLogger(__name__)

class VectorDBClient:
    """Mock Vector DB Client pointing to Opensearch or other Vector DB"""
    def __init__(self, settings: Optional[FastLangFrameSettings] = None):
        self.settings = settings or get_settings()
        self.url = self.settings.opensearch_url
        
    async def search(self, index: str, query: str, top_k: int = 5):
        logger.info(f"Mock search on {self.url} index {index} for query: {query}")
        return []
