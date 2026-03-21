from src.utils.connectors.llm.llm_client import get_langchain_chat_model
from .state import AgentState
from .tools import tools

llm = get_langchain_chat_model()
# Binding all tools including DB and VDB
llm_with_tools = llm.bind_tools(tools)

async def call_model(state: AgentState):
    messages = state["messages"]
    # Using ainvoke for consistency with async tools
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}
