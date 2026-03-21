import os
import sys
import streamlit as st
import asyncio
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# 1. 경로 설정 (패키지 구조와 프로젝트 루트 고려)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# PACKAGE_ROOT = azure_simple
PACKAGE_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
# PROJECT_ROOT = projects/azure_simple
PROJECT_ROOT = os.path.abspath(os.path.join(PACKAGE_ROOT, ".."))
# PROJECTS_DIR = projects
PROJECTS_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, ".."))
# FRAMEWORK_ROOT = FastLangFrame (여기에 src 존재)
FRAMEWORK_ROOT = os.path.abspath(os.path.join(PROJECTS_DIR, ".."))

# 2. 환경 변수 우선 로드 (패키지 임포트 전)
env_path = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(env_path)

# 3. 경로 추가 및 패키지 임포트
sys.path.append(PROJECT_ROOT)
sys.path.append(FRAMEWORK_ROOT)

try:
    from <%project_name%> import builder
except ImportError:
    sys.path.append(PACKAGE_ROOT)
    from <%project_name%> import builder

st.set_page_config(page_title="FastLangFrame Chat Test", page_icon="🧠", layout="wide")
st.title("🧠 FastLangFrame Chat Test (LangGraph ReAct)")
st.caption("LangGraph 및 커스텀 노드 기반의 심층 에이전트 테스트 UI입니다.")
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 내용 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# 사용자 입력
if prompt := st.chat_input("에이전트에게 복잡한 요청을 해보세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.status("그래프 노드 실행 중...", expanded=True) as status:
            try:
                inputs = {
                    "messages": [HumanMessage(content=prompt)]
                }
                
                response = run_async(builder.ainvoke(inputs))
                
                if isinstance(response, dict) and "messages" in response:
                    last_msg = response["messages"][-1]
                    full_response = last_msg.content
                else:
                    full_response = str(response)
                
                status.update(label="그래프 실행 완료!", state="complete", expanded=False)
            except Exception as e:
                full_response = f"⚠️ **에러 발생**: {str(e)}"
                status.update(label="오류 발생", state="error", expanded=True)
                st.exception(e)

        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})

with st.sidebar:
    st.header("Project Info")
    st.info(f"**Project**: <%project_name%>")
    st.info("**Engine**: LangGraph")
    if st.button("대화 기록 초기화"):
        st.session_state.messages = []
        st.rerun()
