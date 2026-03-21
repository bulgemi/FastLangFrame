import asyncio
import logging
from src.common.exceptions.custom import RuntimeRegistryNotReadyError
from .runtime_context import RuntimeContext

logger = logging.getLogger(__name__)

_global_runtime = RuntimeContext()

async def ensure_runtime_context_ready() -> RuntimeContext:
    if not _global_runtime.is_ready:
        await _global_runtime.ensure_ready()
    return _global_runtime

def get_runtime_resources() -> RuntimeContext:
    if not _global_runtime.is_ready:
        raise RuntimeRegistryNotReadyError("Runtime Context is not ready. Call ensure_runtime_context_ready() first.")
    return _global_runtime

async def shutdown_runtime():
    await _global_runtime.close_all()
    logger.info("Runtime stopped smoothly")
