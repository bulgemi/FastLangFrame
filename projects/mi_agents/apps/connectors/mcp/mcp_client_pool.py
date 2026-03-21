from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, List, Set, Tuple

from anyio import ClosedResourceError
from loguru import logger

from apps.connectors.mcp.mcp_client_manager import MCPClientManager

Fn = Callable[[object], Awaitable[object]]


class MCPClientPool:
    def __init__(self, url: str, size: int = 3, per_session_limit: int = 1):
        self.url = url
        self.size = size
        self.per_session_limit = per_session_limit
        self.managers: List[MCPClientManager] = []
        self.semaphores: List[asyncio.Semaphore] = []
        self.dead: Set[int] = set()
        self.rr: int = 0
        self.global_sem = asyncio.Semaphore(size * per_session_limit)
        self._started = False

    async def start(self) -> None:
        """
        풀 구조만 준비한다.
        실제 세션 시작은 call() 내부에서 lazy하게 수행된다.
        """
        if self._started:
            return

        for _ in range(self.size):
            mgr = await MCPClientManager.get(self.url, force_new=True)
            self.managers.append(mgr)
            self.semaphores.append(asyncio.Semaphore(self.per_session_limit))

        self._started = True

    async def close(self) -> None:
        if not self._started:
            return
        await asyncio.gather(
            *(mgr.close() for mgr in self.managers),
            return_exceptions=True,
        )
        self.managers.clear()
        self.semaphores.clear()
        self.dead.clear()
        self._started = False

    async def _pick_fast(self) -> Tuple[int, MCPClientManager]:
        n = len(self.managers)
        for _ in range(n):
            i = self.rr % n
            self.rr += 1
            if i in self.dead:
                continue
            return i, self.managers[i]

        i = 0
        await self._revive_manager(i)
        self.dead.clear()
        return i, self.managers[i]

    async def _revive_manager(self, idx: int) -> None:
        try:
            await self.managers[idx].reconnect()
        except Exception as ex:  # noqa: BLE001
            self.dead.add(idx)
            logger.info("[MCPClientPool._revive_manager] error on idx={}: {}", idx, ex)

    async def call(self, fn: Fn):
        """
        MCP 세션 풀을 통해 fn(session)을 실행.
        - global_sem으로 전체 동시 호출 수 제한
        - 각 manager별 sem으로 per_session_limit 제한
        - 세션이 없으면 여기서 lazy-start
        - ClosedResourceError 발생 시 revive 후 다른 세션/동일 세션으로 재시도
        """
        if not self._started:
            raise RuntimeError("MCPClientPool not started. Call start() at app boot.")

        async with self.global_sem:
            last_exc: Exception | None = None

            # 최대 manager 수 + α 만큼 재시도
            for attempt in range(len(self.managers) + 1):
                i, mgr = await self._pick_fast()
                sem = self.semaphores[i]

                async with sem:
                    try:
                        # 세션이 아직 준비되지 않았다면 여기서 시작
                        if mgr.session is None:
                            await mgr._ensure_started()

                        return await fn(mgr.session)

                    except ClosedResourceError as e:
                        logger.warning(
                            (
                                "[MCPClientPool.call] ClosedResourceError on "
                                "mgr={} attempt={}: {}"
                            ),
                            i,
                            attempt,
                            e,
                        )
                        # 세션이 진짜 죽은 케이스만 dead에 넣고 revive 시도
                        self.dead.add(i)
                        last_exc = e
                        await self._revive_manager(i)
                        # 다음 루프에서 살아난 세션/다른 세션으로 재시도
                        continue

                    except Exception as ex:  # noqa: BLE001
                        logger.error(
                            "[MCPClientPool.call] Unexpected error on mgr={}: {}", i, ex
                        )
                        # 사용자 쿼리 오류, DB 오류 등은 세션을 죽이지 말고 바로 밖으로 전달
                        raise

            # 여기까지 오면 모든 세션이 ClosedResourceError를 내고 revive도 실패
            if last_exc is not None:
                raise last_exc
            raise RuntimeError("All MCP sessions failed")
