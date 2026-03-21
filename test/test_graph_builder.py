import pytest
from pydantic import BaseModel
from src.core.graph_builder import BaseGraphBuilder

class DummyState(BaseModel):
    input: str

def test_graph_builder_init():
    builder = BaseGraphBuilder(DummyState)
    assert builder.builder is not None
    
def dummy_node(state: DummyState):
    return {"input": "processed"}

def test_graph_builder_compile():
    builder = BaseGraphBuilder(DummyState)
    builder.add_node("dummy", dummy_node)
    builder.builder.set_entry_point("dummy")
    compiled = builder.compile()
    assert compiled is not None
