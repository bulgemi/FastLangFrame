from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """LangGraph state for the agent, using add_messages to append messages to history."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
