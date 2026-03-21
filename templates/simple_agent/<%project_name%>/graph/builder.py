from langchain_core.prompts import PromptTemplate
from src.utils.connectors.llm.llm_client import get_langchain_chat_model

class SimpleAgentBuilder:
    def __init__(self):
        self.llm = get_langchain_chat_model()
        self.prompt = PromptTemplate.from_template("You are a helpful assistant. Answer the user's question: {question}")
        self.chain = self.prompt | self.llm

    async def ainvoke(self, input: dict, config=None):
        # input is expected to have 'question'
        return await self.chain.ainvoke(input, config=config)

builder = SimpleAgentBuilder()
agent_graph = builder.chain
