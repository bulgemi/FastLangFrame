from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import inspect

import httpx

from apps.agents.mi_agent.components.context import set_search_policies
from apps.agents.mi_agent.components.policies import SearchPolicySet, build_search_policy_set
from apps.common.configs.settings import Settings, get_settings
from apps.common.exceptions.custom import (
    RuntimeRegistryNotReadyError,
    SemaphoreManagementError,
)
from apps.common.logging.logger_config import logger
from apps.common.values.enums import SemaphoreName
from apps.connectors.http.http_client_manager import HttpClientManager
from apps.connectors.mcp.mcp_client_pool import MCPClientPool


_ShutdownCallback = Callable[[], None] | Callable[[], Awaitable[None]]


class RuntimeContext:
    """프로세스 전역 리소스(MCP 풀, HTTP 클라이언트, 세마포어 등)를 관리하는 컨테이너.

    - 실제 리소스의 생명주기/초기화/셧다운은 이 클래스가 담당
    - 싱글톤 여부는 모듈 전역의 `_runtime_context`로 관리
    """

    def __init__(self) -> None:
        self.cfg: Settings = get_settings()

        # MCP
        self.mcp_pool: MCPClientPool | None = None
        self.mcp_lock = asyncio.Lock()

        # HTTP
        self.http_lock = asyncio.Lock()
        self.http_manager = HttpClientManager(self.cfg)

        # 세마포어
        self.semaphores: dict[SemaphoreName, asyncio.Semaphore] = {}

        # 초기화 상태
        self._initialized: bool = False
        self._init_lock = asyncio.Lock()

        # 셧다운 콜백
        self._shutdown_callbacks: list[_ShutdownCallback] = []

    @property
    def is_ready(self) -> bool:
        return self._initialized

    def register_shutdown_callback(self, cb: _ShutdownCallback) -> None:
        self._shutdown_callbacks.append(cb)

    async def ensure_ready(self) -> RuntimeContext:
        if self._initialized:
            return self

        async with self._init_lock:
            if self._initialized:
                return self

            self._init_global_semaphores()
            await self._init_mcp_client_pool()

            # TODO: 위치 옮기는거 검토
            search_policy_set: SearchPolicySet = build_search_policy_set()
            set_search_policies(search_policy_set)

            self._initialized = True
            return self

    async def close_all(self) -> None:
        await self._close_mcp_pool()
        await self._close_http_clients()
        await self._run_shutdown_callbacks()

    def _init_global_semaphores(self) -> None:
        self.semaphores[SemaphoreName.HTTP] = asyncio.Semaphore(
            self.cfg.http_max_concurrency,
        )
        self.semaphores[SemaphoreName.MCP] = asyncio.Semaphore(
            self.cfg.mcp_max_concurrency,
        )
        self.semaphores[SemaphoreName.LLM] = asyncio.Semaphore(self.cfg.llm_concurrency)

    async def _init_mcp_client_pool(self) -> None:
        async with self.mcp_lock:
            if self.mcp_pool is not None:
                return

            self.mcp_pool = MCPClientPool(
                self.cfg.mcp_url,
                size=self.cfg.mcp_pool_size,
                per_session_limit=self.cfg.mcp_per_session_limit,
            )
            await self.mcp_pool.start()

    async def _close_mcp_pool(self) -> None:
        async with self.mcp_lock:
            pool = self.mcp_pool
            self.mcp_pool = None

            if pool:
                try:
                    await pool.close()
                except Exception as ex:
                    logger.warning(
                        "[shutdown] MCP pool close failed (type={}, msg={}): {!r}",
                        type(ex).__name__,
                        str(ex),
                        ex,
                    )

    async def _close_http_clients(self) -> None:
        async with self.http_lock:
            return await self.http_manager.close_http_clients()

    async def _run_shutdown_callbacks(self) -> None:
        for cb in list(self._shutdown_callbacks):
            try:
                if inspect.iscoroutinefunction(cb):
                    await cb()
                else:
                    result = cb()
                    if inspect.isawaitable(result):
                        await result
            except Exception as ex:
                logger.warning(
                    "[shutdown] Shutdown callback failed (cb={!r}, type={}, msg={}): {!r}",
                    cb,
                    type(ex).__name__,
                    str(ex),
                    ex,
                )

    async def get_http_client(
        self,
        *,
        base_url: str = "",
        verify: bool | None = None,
        http2: bool | None = None,
    ) -> httpx.AsyncClient:
        if not self._initialized:
            raise RuntimeRegistryNotReadyError

        return await self.http_manager.get_http_client(
            base_url=base_url,
            verify=verify,
            http2=http2,
        )

    def get_semaphore(self, name: SemaphoreName) -> asyncio.Semaphore:
        if not self._initialized:
            raise RuntimeRegistryNotReadyError

        sem = self.semaphores.get(name)
        if sem is None:
            raise SemaphoreManagementError(detail=f"Semaphore '{name}' not initialized")
        return sem

    def get_http_semaphore(self) -> asyncio.Semaphore:
        return self.get_semaphore(SemaphoreName.HTTP)

    def get_mcp_semaphore(self) -> asyncio.Semaphore:
        return self.get_semaphore(SemaphoreName.MCP)

    def get_llm_semaphore(self) -> asyncio.Semaphore:
        return self.get_semaphore(SemaphoreName.LLM)

    def get_mcp_pool(self) -> MCPClientPool:
        if not self._initialized:
            raise RuntimeRegistryNotReadyError
        pool = self.mcp_pool
        if pool is None:
            raise RuntimeRegistryNotReadyError(detail="MCP pool not initialized")
        return pool
