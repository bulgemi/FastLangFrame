from langchain_core.runnables import Runnable, RunnableLambda
from langgraph.graph import END, START, StateGraph

from apps.agents.mi_agent.state.state import MariAgentState
from apps.agents.mi_agent.subgraphs.vdb_search.schemas import VDBSearchOutput
from apps.agents.mi_agent.subgraphs.vdb_search.stages.execute.search_documents_node import (
    search_documents_node,
)
from apps.agents.mi_agent.subgraphs.vdb_search.state import VDBSearchState
from apps.agents.mi_agent.subgraphs.vdb_search.subgraph_adapter import to_output, to_state


def build_vdb_subgraph() -> Runnable:
    graph = StateGraph(state_schema=VDBSearchState)

    graph.add_node("search_documents_node", search_documents_node)
    graph.add_edge(START, "search_documents_node")
    graph.add_edge("search_documents_node", END)

    return graph.compile()


_vdb_subgraph = build_vdb_subgraph()

runnable_graph: Runnable = (
    RunnableLambda(to_state) | _vdb_subgraph | RunnableLambda(to_output)
).with_types(
    input_type=MariAgentState,
    output_type=VDBSearchOutput,
)


async def run_vdb(agent_state: MariAgentState) -> VDBSearchOutput:
    out: VDBSearchOutput =  await runnable_graph.ainvoke(agent_state)
    return out
