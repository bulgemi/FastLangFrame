from __future__ import annotations

from apps.agents.mi_agent.components.context import get_search_policies
from apps.agents.mi_agent.components.policies import SearchPolicySet
from apps.agents.mi_agent.orchestration.supervisors.search_supervisor import (
    SearchSupervisor,
)
from apps.agents.mi_agent.state.state import MariAgentState


# from apps.common.models.mari_agent_output import MessageModel, ContentModel


async def search_node(state: MariAgentState) -> MariAgentState:
    search_policy_set: SearchPolicySet = get_search_policies()
    supervisor = SearchSupervisor(search_policy_set=search_policy_set)
    merged = await supervisor.run_parallel_searches(agent_state=state)
    # TODO: 검색 결과 조합 필요
    # content = ContentModel(
    #     text="검색 요약 ...",
    #     charts=state.charts or [],
    #     sources=state.web_sources or [],
    #     vector_sources=state.vector_metadata or [],
    #     related_data=state.related_data or [],
    # )
    # state.messages.append(
    #     MessageModel(
    #         content=content,
    #         usage=state.usage,
    #         sql=state.sql or "",
    #         used_tables=state.used_tables or [],
    #         rewrite=state.rewrite or "",
    #     )
    # )
    state.search_output = merged
    return state
