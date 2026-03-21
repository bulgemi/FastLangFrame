from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from src.utils.connectors.llm.llm_client import get_langchain_chat_model

class RAGAgentBuilder:
    def __init__(self):
        self.llm = get_langchain_chat_model()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Answer the question based on the context: {context}"),
            ("user", "{question}")
        ])
        
        def mock_retriever(query: str):
            # In a real app, use src.utils.connectors.vdb VectorDBClient
            return f"Mock retrieved context for: {query}"
            
        self.chain = (
            {"context": mock_retriever, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
        )

    async def ainvoke(self, input: dict, config=None):
        question = input.get("question", str(input))
        return await self.chain.ainvoke(question, config=config)

builder = RAGAgentBuilder()
agent_graph = builder.chain
