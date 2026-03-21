from langchain.agents import AgentExecutor, create_tool_calling_agent
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
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a multi-agent supervisor. Use the provided tools (researcher, writer) to fulfill the request."),
            ("placeholder", "{chat_history}"),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    async def ainvoke(self, input: dict, config=None):
        return await self.agent_executor.ainvoke(input, config=config)

builder = MultiAgentBuilder()
agent_graph = builder.agent_executor
