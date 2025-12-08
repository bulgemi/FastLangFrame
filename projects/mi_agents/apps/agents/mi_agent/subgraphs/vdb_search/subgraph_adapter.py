from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from apps.agents.mi_agent.state.state import MariAgentState
from apps.agents.mi_agent.subgraphs.vdb_search.schemas import (
    VDBSearchInput,
    VDBSearchOutput,
    VectorSourceModel,
)
from apps.agents.mi_agent.subgraphs.vdb_search.state import VDBSearchState


def to_input_from_agent_state(mari_state: MariAgentState) -> VDBSearchInput:
    return VDBSearchInput(
        api_key=mari_state.api_key,
        headers=mari_state.headers,
        rewritten_query=mari_state.rewritten_query,
        histories=mari_state.histories or [],
        repo_id=mari_state.repo_id,
        authorized_product_nums=mari_state.authorized_product_nums,
    )

def _ensure_mari_state(mari_state: MariAgentState | Mapping[str, Any]) -> MariAgentState:
    if isinstance(mari_state, MariAgentState):
        return mari_state
    return MariAgentState.model_validate(cast(Mapping[str, Any], mari_state))

def _to_input_from_agent_state(mari_state: MariAgentState) -> VDBSearchInput:
    return VDBSearchInput(
        api_key=mari_state.api_key,
        headers=mari_state.headers,
        rewritten_query=mari_state.rewritten_query,
        histories=mari_state.histories or [],
        repo_id=mari_state.repo_id,
        authorized_product_nums=mari_state.authorized_product_nums,
    )


def to_state(mari_state: MariAgentState | Mapping[str, Any]) -> VDBSearchState:
    mari_model = _ensure_mari_state(mari_state)
    vdb_search_input: VDBSearchInput = _to_input_from_agent_state(mari_model)
    return VDBSearchState(
        api_key=vdb_search_input.api_key,
        headers=vdb_search_input.headers,
        histories=vdb_search_input.histories or [],
        rewritten_query=vdb_search_input.rewritten_query,
        repo_id=vdb_search_input.repo_id,
        authorized_product_nums=vdb_search_input.authorized_product_nums,
    )


def to_output(vdb_state: VDBSearchState | Mapping[str, Any]) -> VDBSearchOutput:
    vdb_search_results = vdb_state["vector_sources"]
    vector_sources: list[VectorSourceModel] = _convert_dict_to_vdb_source_list(vdb_search_results)

    return VDBSearchOutput(
        vector_sources=vector_sources,
    )

def _convert_dict_to_vdb_source_list(
    vdb_state: VDBSearchOutput | Mapping[str, Any] | list[Any],
) -> list[VectorSourceModel]:
    return [
        item
        if isinstance(item, VectorSourceModel)
        else VectorSourceModel.model_validate(cast(Mapping[str, Any], item))
        for item in vdb_state
    ]
