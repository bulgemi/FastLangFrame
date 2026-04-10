from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from src.utils.connectors.llm.llm_client import get_langchain_chat_model

@tool
def researcher_tool(query: str) -> str:
    """Useful for researching a topic."""
    return f"Research results for {query}"

@tool
def writer_tool(topic: str) -> str:
    """Useful for writing content about a topic."""
    return f"Written content about {topic}"

class MultiAgentBuilder:
    def __init__(self):
        self.llm = get_langchain_chat_model()
        self.tools = [researcher_tool, writer_tool]
        # system_prompt is passed to create_react_agent
        system_prompt = "You are a multi-agent supervisor. Use the provided tools (researcher, writer) to fulfill the request."
        
        self.agent_executor = create_react_agent(self.llm, self.tools, prompt=system_prompt)

    async def ainvoke(self, input: dict, config=None):
        """
        Execute the agent graph.
        create_react_agent expects a dict with 'messages' or similar state.
        """
        return await self.agent_executor.ainvoke(input, config=config)

builder = MultiAgentBuilder()
agent_graph = builder.agent_executor
