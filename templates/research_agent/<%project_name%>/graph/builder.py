from langgraph.graph import END, StateGraph

from <%project_name%>.graph.nodes import (
    ResearchPlannerNode,
    ResearchSearchNode,
    ResearchSynthesisNode,
)
from <%project_name%>.graph.state import ResearchGraphState


class ResearchAgentBuilder:
    def __init__(self):
        # Initialize nodes
        self.planner = ResearchPlannerNode()
        self.search = ResearchSearchNode()
        self.synthesis = ResearchSynthesisNode()

        # Build Graph
        workflow = StateGraph(ResearchGraphState)

        # Add Nodes
        workflow.add_node(self.planner.name, self.planner)
        workflow.add_node(self.search.name, self.search)
        workflow.add_node(self.synthesis.name, self.synthesis)

        # Set Entry Point and Edges
        workflow.set_entry_point(self.planner.name)
        workflow.add_edge(self.planner.name, self.search.name)
        workflow.add_edge(self.search.name, self.synthesis.name)
        workflow.add_edge(self.synthesis.name, END)

        self.graph = workflow.compile()

    async def ainvoke(self, input: dict, config=None):
        """
        Invoke the research agent graph.
        Expects input with 'req_input' or will wrap it.
        """
        # If input is a raw dict with 'query', wrap it into ResearchGraphState structure
        if "req_input" not in input and "query" in input:
            state = {
                "req_input": {
                    "query": input["query"],
                    "company_code": input.get("company_code", "default"),
                    "user_num": input.get("user_num", 0),
                }
            }
        else:
            state = input

        return await self.graph.ainvoke(state, config=config)


builder = ResearchAgentBuilder()
agent_graph = builder.graph
