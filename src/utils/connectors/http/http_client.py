import httpx
from typing import Optional

_global_client: Optional[httpx.AsyncClient] = None

async def get_http_client() -> httpx.AsyncClient:
    """Returns a reusable httpx async client"""
    global _global_client
    if _global_client is None or _global_client.is_closed:
        _global_client = httpx.AsyncClient(verify=False, timeout=30.0)
    return _global_client

async def close_http_client() -> None:
    """Closes the reusable client if exists"""
    global _global_client
    if _global_client and not _global_client.is_closed:
        await _global_client.aclose()
        _global_client = None
