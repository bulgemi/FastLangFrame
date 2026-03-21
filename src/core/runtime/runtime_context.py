import asyncio
import logging
from typing import Dict
from src.common.values.enums import SemaphoreName

logger = logging.getLogger(__name__)

class RuntimeContext:
    """Manages Agent resources, semaphores, and shared contexts"""
    def __init__(self):
        self._semaphores: Dict[str, asyncio.Semaphore] = {}
        self.is_ready = False

    async def ensure_ready(self):
        if not self.is_ready:
            self._semaphores[SemaphoreName.HTTP] = asyncio.Semaphore(10)
            self._semaphores[SemaphoreName.LLM] = asyncio.Semaphore(5)
            self._semaphores[SemaphoreName.MCP] = asyncio.Semaphore(5)
            self.is_ready = True
            logger.info("RuntimeContext initialized")

    def get_semaphore(self, name: SemaphoreName) -> asyncio.Semaphore:
        return self._semaphores[name]

    async def close_all(self):
        self.is_ready = False
        logger.info("RuntimeContext closed all resources")
