from langgraph.graph import StateGraph
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class BaseGraphBuilder:
    """
    Standard LangGraph Builder for FastLangFrame projects.
    Handles Phoenix tracing injection implicitly if enabled.
    """
    def __init__(self, state_schema: type[BaseModel]):
        self.builder = StateGraph(state_schema)

    def add_node(self, name: str, action):
        return self.builder.add_node(name, action)

    def add_edge(self, start: str, end: str):
        return self.builder.add_edge(start, end)
        
    def add_conditional_edges(self, start, condition, path_map=None):
        return self.builder.add_conditional_edges(start, condition, path_map)

    def compile(self, **kwargs):
        """Compile the graph, applying common checkpointers or tracing settings"""
        logger.info("Compiling graph using FastLangFrame BaseGraphBuilder")
        compiled_graph = self.builder.compile(**kwargs)
        return compiled_graph
