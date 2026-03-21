from __future__ import annotations

from typing import Any
from uuid import UUID

from apps.agents.mi_agent.schemas.mari_agent_input import MariAgentInput
from apps.agents.mi_agent.schemas.mari_agent_output import (
    ContentModel,
    MariAgentOutput,
    MessageModel,
)
from apps.agents.mi_agent.schemas.search_output import SearchOutput
from apps.agents.mi_agent.state.state import MariAgentState
from apps.common.configs.settings import get_settings


def to_state(raw: dict[str, Any] | MariAgentInput) -> MariAgentState:
    mi = raw if isinstance(raw, MariAgentInput) else MariAgentInput.model_validate(raw)
    cfg = get_settings()

    repo_id = _to_uuid(getattr(mi, "repo_id", None)) or cfg.repo_id
    repo_id_rdb_metadata = _to_uuid(getattr(mi, "repo_id_rdb_metadata", None)) or cfg.repo_id_rdb_metadata

    return MariAgentState(
        api_key=mi.api_key if mi.api_key else cfg.api_key,
        headers=mi.headers,
        company_code=mi.company_code,
        authorized_product_nums=mi.authorized_product_nums,
        message=mi.message,
        histories=mi.histories,
        web_search_enabled=mi.web_search,
        repo_id=repo_id,
        repo_id_rdb_metadata=repo_id_rdb_metadata,
        current_node="rewrite_query",
        executed_nodes=[],
    )


def _to_uuid(v: Any | None) -> UUID | None:
    if v is None or isinstance(v, UUID):
        return v
    return UUID(str(v))


from typing import Any


def to_output(state_dict: dict[str, Any]) -> MariAgentOutput:
    mari_agent_state = MariAgentState.model_validate(state_dict["analysis"])

    search_output: SearchOutput = mari_agent_state.search_output
    rdb = search_output.rdb_search_output
    vdb = search_output.vdb_search_output
    web = search_output.web_search_output

    content = ContentModel(
        text=mari_agent_state.analysis_content,
        related_data=rdb.related_data if rdb else [],
        charts=rdb.charts if rdb else [],
        sources=web.web_sources if web else [],
        vector_sources=vdb.vector_sources if vdb else [],
    )
    one = MessageModel(
        content=content,
        usage=mari_agent_state.usage,
        sql=rdb.sqls if rdb else "",
        used_tables=rdb.used_tables if rdb else [],
        rewrite=mari_agent_state.rewritten_query or "",
    )
    return MariAgentOutput(messages=[one])

