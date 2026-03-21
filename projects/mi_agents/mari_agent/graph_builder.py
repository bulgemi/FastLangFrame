from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from mari_agent.common.config import phoenix_config
from mari_agent.common.tracer_for_sdk import using_tracer
from mari_agent.graph.nodes import (
    DataAnalysisNode,
    DataCollectNode,
    OutOfDomainAnswerNode,
    PlannerNode,
    PrepareAxPromptNode,
    RewriteQueryNode,
)
from mari_agent.graph.states import MariGraphState


class MariGraphBuilder:
    def __init__(self):
        self.mari_graph = self._compile()
        self.mari_graph.stream_mode = "custom"

    def _compile(self, **kwargs):
        builder = StateGraph(MariGraphState)

        # init nodes
        prepare_prompt_node = PrepareAxPromptNode()
        rewrite_query_node = RewriteQueryNode()
        planner_node = PlannerNode()
        collect_node = DataCollectNode()
        analysis_node = DataAnalysisNode()
        out_of_domain_node = OutOfDomainAnswerNode()

        # add nodes
        builder.add_node(prepare_prompt_node.name, prepare_prompt_node)
        builder.add_node(rewrite_query_node.name, rewrite_query_node)
        builder.add_node(planner_node.name, planner_node)
        builder.add_node(collect_node.name, collect_node)
        builder.add_node(analysis_node.name, analysis_node)
        builder.add_node(out_of_domain_node.name, out_of_domain_node)

        # add edges
        builder.add_edge(START, prepare_prompt_node.name)
        builder.add_edge(prepare_prompt_node.name, rewrite_query_node.name)
        ## conditional edges (branching based on domain relevance)
        builder.add_conditional_edges(
            rewrite_query_node.name,
            lambda state: planner_node.name
            if (state.rewrite_query and state.rewrite_query.is_domain_related)
            else out_of_domain_node.name,
        )
        ## data analysis flow
        builder.add_edge(planner_node.name, collect_node.name)
        builder.add_edge(collect_node.name, analysis_node.name)
        builder.add_edge(analysis_node.name, END)

        ## out of domain answer flow
        builder.add_edge(out_of_domain_node.name, END)

        return builder.compile(**kwargs)

    async def ainvoke(self, input: dict, config=None):
        if phoenix_config.enabled:
            with using_tracer(
                project_name="app-mi-project-mari_agent",
                session_id=str(uuid4()),
                user_id="mari_test_user",
                metadata={},
                tags=None,
            ):
                result = await self.mari_graph.ainvoke(input, config)
        else:
            result = await self.mari_graph.ainvoke(input, config)
        return result


# mari_graph = builder.compile(checkpointer=MemorySaver())
builder = MariGraphBuilder()
mari_graph = builder.mari_graph
