import logging

from apps.agents.mi_agent.state.state import MariAgentState


async def planner_node(state: MariAgentState) -> MariAgentState:
    logging.info("planner_node")
    return state
