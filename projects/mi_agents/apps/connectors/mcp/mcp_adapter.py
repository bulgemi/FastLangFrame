from __future__ import annotations

from collections.abc import Callable
from typing import Any

from apps.common.runtime.runtime import (
    ensure_runtime_context_ready,
    get_mcp_pool,
    get_mcp_semaphore,
)


async def mcp_call(op: Callable[[Any], Any]):
    await ensure_runtime_context_ready()
    pool = get_mcp_pool()
    mcp_sem = get_mcp_semaphore()

    async with mcp_sem:
        return await pool.call(op)


async def mcp_read_resource(uri: str):
    return await mcp_call(lambda s: s.read_resource(uri))


async def mcp_get_prompt(name: str, params: dict):
    return await mcp_call(lambda s: s.get_prompt(name, params))


async def mcp_call_tool(name: str, args: dict):
    return await mcp_call(lambda s: s.call_tool(name, args))
