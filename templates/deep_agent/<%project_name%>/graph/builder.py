from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from .state import AgentState
from .nodes import call_model
from .tools import tools

# 1. StateGraph 정의
workflow = StateGraph(AgentState)

# 2. 노드 추가
workflow.add_node("agent", call_model)
tool_node = ToolNode(tools)
workflow.add_node("tools", tool_node)

# 3. 엣지 설정
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    tools_condition,
)
workflow.add_edge("tools", "agent")

# 4. 컴파일
agent_graph = workflow.compile()

# Standardized builder instance
class DeepAgentBuilder:
    def __init__(self, graph):
        self.agent_graph = graph
    async def ainvoke(self, input: dict, config=None):
        return await self.agent_graph.ainvoke(input, config=config)

builder = DeepAgentBuilder(agent_graph)
