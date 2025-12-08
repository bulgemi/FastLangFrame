from __future__ import annotations

from langchain_core.runnables import Runnable, RunnableLambda
from langgraph.graph import StateGraph

from apps.agents.mi_agent.flows.mari_agent_adapters import to_output, to_state
from apps.agents.mi_agent.flows.mari_agent_runtime import ensure_runtime
from apps.agents.mi_agent.nodes.analyze import generate_analysis
from apps.agents.mi_agent.nodes.planner import planner_node
from apps.agents.mi_agent.nodes.rewrite_query import rewrite_query_node
from apps.agents.mi_agent.nodes.search import search_node
from apps.agents.mi_agent.schemas.mari_agent_input import MariAgentInput
from apps.agents.mi_agent.schemas.mari_agent_output import MariAgentOutput
from apps.agents.mi_agent.state.state import MariAgentState


def build_mi_agent() -> Runnable:
    graph = StateGraph(state_schema=MariAgentState)

    graph.add_node("rewrite_query", rewrite_query_node)
    graph.add_node("plan", planner_node)
    graph.add_node("search", search_node)
    graph.add_node("analysis", generate_analysis)

    graph.set_entry_point("rewrite_query")
    graph.add_edge("rewrite_query", "plan")
    graph.add_edge("plan", "search")
    graph.add_edge("search", "analysis")
    graph.set_finish_point("analysis")

    return graph.compile()


_mari_agent = build_mi_agent()


runnable_graph: Runnable = (
    RunnableLambda(to_state) | RunnableLambda(ensure_runtime) | _mari_agent | RunnableLambda(to_output)
).with_types(input_type=MariAgentInput, output_type=MariAgentOutput)
