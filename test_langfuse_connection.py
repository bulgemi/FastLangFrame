import os
import time
import logging
from langfuse import Langfuse
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from src.utils.observability import get_langfuse_callback, prepare_langfuse_metadata
from src.common.configs.settings import get_settings

# 로깅 설정 (디버그 정보 확인용)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_langfuse_direct():
    print("\n=== 1. Langfuse Direct Client Test ===")
    settings = get_settings()
    print(f"Host: {settings.langfuse_host}")
    print(f"Public Key: {settings.langfuse_public_key[:10]}...")
    
    langfuse = Langfuse(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_host,
        debug=True # 디버그 모드 활성화
    )
    
    # 인증 체크
    try:
        if langfuse.auth_check():
            print("✅ Langfuse Authentication Successful!")
        else:
            print("❌ Langfuse Authentication Failed!")
            return
    except Exception as e:
        print(f"❌ Auth Check Error: {e}")
        return

    # 단순 이벤트 생성
    langfuse.event(name="test-event", metadata={"type": "manual-check"})
    langfuse.flush()
    print("✅ Manual event sent and flushed.")

def test_langchain_tracing():
    print("\n=== 2. LangChain Callback Test ===")
    
    # 1. 콜백 핸들러 가져오기
    handler = get_langfuse_callback()
    if not handler:
        print("❌ Failed to get Langfuse callback handler. Check your .env settings.")
        return
    
    print(f"✅ Callback handler created: {handler}")

    # 2. 메타데이터 준비
    metadata = prepare_langfuse_metadata(
        user_id="test-user-123",
        session_id="test-session-456",
        tags=["manual-test"]
    )
    
    # 3. 간단한 체인 실행
    try:
        llm = ChatOpenAI(model="gpt-4o") # OpenAI API 키가 설정되어 있어야 함
        print("Running LLM query...")
        response = llm.invoke(
            [HumanMessage(content="Hi, this is a Langfuse tracing test. Say 'Tracing is working!'")],
            config={"callbacks": [handler], "metadata": metadata}
        )
        print(f"Response: {response.content}")
        
        # 데이터 전송 보장 (비동기 전송 방지)
        handler.client.flush()
        print("✅ LangChain trace sent and flushed.")
        print(f"🔗 Trace ID: {handler.last_trace_id}")
        
    except Exception as e:
        print(f"❌ LangChain Execution Error: {e}")

if __name__ == "__main__":
    # .env 로드가 필요한 경우 (src 모듈을 위해)
    from dotenv import load_dotenv
    load_dotenv()
    
    test_langfuse_direct()
    test_langchain_tracing()
    print("\nDone. Please check your Langfuse dashboard.")
