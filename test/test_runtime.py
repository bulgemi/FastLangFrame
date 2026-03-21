import pytest
import asyncio
from src.core.runtime.runtime import ensure_runtime_context_ready, get_runtime_resources, shutdown_runtime
from src.common.values.enums import SemaphoreName

@pytest.mark.asyncio
async def test_runtime_context():
    runtime = await ensure_runtime_context_ready()
    assert runtime.is_ready is True
    
    # Should not raise
    res = get_runtime_resources()
    assert res is runtime
    
    sem = res.get_semaphore(SemaphoreName.HTTP)
    assert isinstance(sem, asyncio.Semaphore)
    
    await shutdown_runtime()
    assert runtime.is_ready is False
