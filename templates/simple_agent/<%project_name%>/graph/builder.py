from langchain_core.prompts import PromptTemplate
from src.utils.connectors.llm.llm_client import get_langchain_chat_model
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

class SimpleAgentBuilder:
    def __init__(self):
        self.llm = get_langchain_chat_model()
        self.prompt = PromptTemplate.from_template("You are a helpful assistant. Answer the user's question: {question}")
        
        # Preprocessing to handle both 'question' and 'messages' (from chat_test)
        def preprocess_input(x: dict):
            if "messages" in x and "question" not in x:
                last_msg = x["messages"][-1]
                if hasattr(last_msg, "content"):
                    return {"question": last_msg.content}
                elif isinstance(last_msg, dict):
                    return {"question": last_msg.get("content", str(last_msg))}
                else:
                    return {"question": str(last_msg)}
            return x

        self.chain = RunnableLambda(preprocess_input) | self.prompt | self.llm

    async def ainvoke(self, input: dict, config=None):
        return await self.chain.ainvoke(input, config=config)

builder = SimpleAgentBuilder()
agent_graph = builder.chain
