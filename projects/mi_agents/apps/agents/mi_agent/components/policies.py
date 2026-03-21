# TODO: 환경병수로 변환
from __future__ import annotations

import asyncio

from pydantic import BaseModel, Field

from apps.common.configs.settings import Settings, get_settings
from apps.common.values.enums import SearchSource


class RetryPolicy(BaseModel):
    retries: int = 1
    retry_on: tuple[type[BaseException], ...] = (asyncio.TimeoutError,)


class ExecutionPolicy(BaseModel):
    authorized_product_nums: list[int] = None
    exec_timeout_sec: float = 5.0
    retry: RetryPolicy = Field(default_factory=RetryPolicy)


class SearchPolicySet(BaseModel):
    enabled_sources: set[SearchSource]
    required_sources: set[SearchSource]
    search_exec_fanout_deadline_sec: float
    strict_required: bool

    rdb: ExecutionPolicy
    vdb: ExecutionPolicy
    web: ExecutionPolicy

    def get(self, resource: str) -> ExecutionPolicy:
        return getattr(self, resource)


def build_search_policy_set() -> SearchPolicySet:
    settings: Settings = get_settings()

    return SearchPolicySet(
        rdb=ExecutionPolicy(exec_timeout_sec=settings.search_rdb_exec_timeout_sec),
        vdb=ExecutionPolicy(exec_timeout_sec=settings.search_vdb_exec_timeout_sec),
        web=ExecutionPolicy(
            exec_timeout_sec=settings.search_web_exec_timeout_sec,
            retry=RetryPolicy(retries=1),
        ),
        enabled_sources={SearchSource(x) for x in settings.search_sources if x in {e.value for e in SearchSource}},
        required_sources={SearchSource(x) for x in settings.search_sources if x in {e.value for e in SearchSource}},
        search_exec_fanout_deadline_sec=settings.search_exec_fanout_deadline_sec,
        strict_required=True,
    )
