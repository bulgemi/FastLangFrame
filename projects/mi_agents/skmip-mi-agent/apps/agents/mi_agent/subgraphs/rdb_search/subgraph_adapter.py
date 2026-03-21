from __future__ import annotations

from typing import Any, Mapping, cast

from apps.agents.mi_agent.state.state import MariAgentState
from apps.agents.mi_agent.subgraphs.rdb_search.schemas import (
    RDBSearchInput,
    RDBSearchOutput,
    RDBSearchResults,
)
from apps.agents.mi_agent.subgraphs.rdb_search.state import RDBSearchState


def to_state(mari_state: MariAgentState | Mapping[str, Any]) -> RDBSearchState:
    mari_model = _ensure_mari_state(mari_state)
    rdb_search_input: RDBSearchInput = _to_input_from_agent_state(mari_model)

    return RDBSearchState(
        api_key=rdb_search_input.api_key,
        headers=rdb_search_input.headers,
        rewritten_query=rdb_search_input.rewritten_query,
        histories=rdb_search_input.histories or [],
        repo_id_rdb_metadata=rdb_search_input.repo_id_rdb_metadata,
        authorized_product_nums=rdb_search_input.authorized_product_nums,
    )


def to_output(rdb_state: RDBSearchState | Mapping[str, Any]) -> RDBSearchOutput:
    rdb_model = _ensure_rdb_state(rdb_state)

    rdb_search_results = rdb_model.rdb_search_results
    if rdb_search_results is None:
        rdb_search_results = RDBSearchResults(sqls="")

    return RDBSearchOutput(
        used_tables=rdb_search_results.used_tables,
        metric_data=rdb_search_results.metric_data,
        related_data=rdb_search_results.related_data,
        sqls=rdb_search_results.sqls,
    )


def _to_input_from_agent_state(mari_state: MariAgentState) -> RDBSearchInput:
    return RDBSearchInput(
        api_key=mari_state.api_key,
        headers=mari_state.headers,
        rewritten_query=mari_state.rewritten_query,
        histories=mari_state.histories or [],
        repo_id_rdb_metadata=mari_state.repo_id_rdb_metadata,
        authorized_product_nums=mari_state.authorized_product_nums,
    )


def _ensure_mari_state(mari_state: MariAgentState | Mapping[str, Any]) -> MariAgentState:
    if isinstance(mari_state, MariAgentState):
        return mari_state
    return MariAgentState.model_validate(cast(Mapping[str, Any], mari_state))


def _ensure_rdb_state(rdb_state: RDBSearchState | Mapping[str, Any]) -> RDBSearchState:
    if isinstance(rdb_state, RDBSearchState):
        return rdb_state
    return RDBSearchState.model_validate(cast(Mapping[str, Any], rdb_state))
