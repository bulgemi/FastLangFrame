from __future__ import annotations

from typing import TypeVar

from apps.common.runtime.runtime import ensure_runtime_context_ready


T = TypeVar("T")


async def ensure_runtime[T](x: T) -> T:
    await ensure_runtime_context_ready()
    return x
