import os
import sys
import streamlit as st
import asyncio
from dotenv import load_dotenv

# 1. 경로 설정 (패키지 구조와 프로젝트 루트 고려)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(PACKAGE_ROOT, ".."))
PROJECTS_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, ".."))
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

st.set_page_config(page_title="FastLangFrame Chat Test", page_icon="🤖", layout="wide")
st.title("🤖 FastLangFrame Chat Test (RAG)")
st.caption("RAG 기반 에이전트 테스트 UI입니다.")
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

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

if prompt := st.chat_input("질문을 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.status("지식베이스 검색 및 답변 생성 중...", expanded=True) as status:
            try:
                inputs = {
                    "question": prompt,
                    "input": prompt
                }
                
                response = run_async(builder.ainvoke(inputs))
                
                if hasattr(response, "content"):
                    full_response = response.content
                elif isinstance(response, dict) and "output" in response:
                    full_response = response["output"]
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
