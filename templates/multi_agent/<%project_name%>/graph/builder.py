from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from src.utils.connectors.llm.llm_client import get_langchain_chat_model

# Import tools from the local tools directory
from .tools.tool_manager import researcher_tool, writer_tool

class MultiAgentBuilder:
    def __init__(self):
        self.llm = get_langchain_chat_model()
        self.tools = [researcher_tool, writer_tool]
        self.system_prompt = "You are a multi-agent supervisor. Use the provided tools (researcher, writer) to fulfill the request."
        
        # Using langgraph's create_react_agent instead of AgentExecutor
        self.agent_executor = create_react_agent(self.llm, self.tools, prompt=self.system_prompt)

    async def ainvoke(self, input: dict, config=None):
        """
        Handle input structure difference between AgentExecutor and React Agent.
        React Agent expects {'messages': [HumanMessage(content=...)]}
        """
        if "input" in input and "messages" not in input:
            input = {"messages": [("user", input["input"])]}
        return await self.agent_executor.ainvoke(input, config=config)

builder = MultiAgentBuilder()
agent_graph = builder.agent_executor
