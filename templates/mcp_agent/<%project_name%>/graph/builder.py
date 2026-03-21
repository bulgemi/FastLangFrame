from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from src.utils.connectors.llm.llm_client import get_langchain_chat_model

# Assume an MCP integration package for Langchain is available, e.g., mcp-langchain
# from mcp_langchain import MCPToolLoader

class MCPAgentBuilder:
    def __init__(self):
        self.llm = get_langchain_chat_model()
        self.tools = []  # Placeholder for MCP tools
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an MCP-enabled agent. Use the loaded MCP tools to answer requests."),
            ("placeholder", "{chat_history}"),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    async def ainvoke(self, input: dict, config=None):
        return await self.agent_executor.ainvoke(input, config=config)

builder = MCPAgentBuilder()
agent_graph = builder.agent_executor
