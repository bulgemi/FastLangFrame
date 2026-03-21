import os
import sys
import streamlit as st
import asyncio
from dotenv import load_dotenv

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
    # 패키지 명칭이 다를 경우를 위한 폴백
    sys.path.append(PACKAGE_ROOT)
    from <%project_name%> import builder

st.set_page_config(page_title="FastLangFrame Chat Test", page_icon="🤖", layout="wide")
st.title("🤖 FastLangFrame Chat Test")
st.caption("FastLangFrame 기반 에이전트의 기능을 실시간으로 테스트합니다.")
st.markdown("---")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 내용 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 비동기 실행을 위한 헬퍼
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# 사용자 입력
if prompt := st.chat_input("에이전트에게 질문하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.status("에이전트가 생각 중입니다...", expanded=True) as status:
            try:
                inputs = {
                    "question": prompt,
                    "input": prompt,
                    "messages": [{"role": "user", "content": prompt}]
                }
                
                response = run_async(builder.ainvoke(inputs))
                
                if hasattr(response, "content"):
                    full_response = response.content
                elif isinstance(response, dict):
                    if "messages" in response:
                        last_msg = response["messages"][-1]
                        full_response = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
                    elif "output" in response:
                        full_response = response["output"]
                    else:
                        full_response = str(response)
                else:
                    full_response = str(response)
                
                status.update(label="답변 완료!", state="complete", expanded=False)
            except Exception as e:
                full_response = f"⚠️ **에러 발생**: {str(e)}"
                status.update(label="오류 발생", state="error", expanded=True)
                st.exception(e)

        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})

with st.sidebar:
    st.header("Project Info")
    st.info(f"**Project**: <%project_name%>")
    if st.button("대화 기록 초기화"):
        st.session_state.messages = []
        st.rerun()
