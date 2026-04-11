try:
    from deepagents import create_deep_agent
except ImportError:
    # This might happen if poetry install was not run
    print("❌ Error: 'deepagents' library not found. Please run 'poetry install' in the project root.")
    raise

from src.utils.connectors.llm.llm_client import get_langchain_chat_model
from .tools import tools

# 1. LLM 모델 초기화
llm = get_langchain_chat_model()

# 2. deepagents를 이용한 에이전트 그래프 생성
# create_deep_agent는 내부적으로 LangGraph의 StateGraph를 구축하고 컴파일하여 반환합니다.
agent_graph = create_deep_agent(
    model=llm,
    system_prompt="You are a helpful Deep Agent. Use tools when necessary to solve complex tasks.",
    tools=tools
)

# Standardized builder instance for FastLangFrame API bridge
class DeepAgentBuilder:
    def __init__(self, graph):
        self.agent_graph = graph

    async def ainvoke(self, input: dict, config=None):
        """
        에이전트 실행 (비동기)
        deepagents는 기본적으로 LangGraph 입력 형식을 따릅니다.
        """
        return await self.agent_graph.ainvoke(input, config=config)

builder = DeepAgentBuilder(agent_graph)
