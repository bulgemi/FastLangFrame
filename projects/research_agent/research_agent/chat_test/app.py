import os
import sys
import streamlit as st
import asyncio
import base64
from dotenv import load_dotenv
from st_chat_input_multimodal import multimodal_chat_input

# 1. 경로 설정 (패키지 구조와 프로젝트 루트 고려)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(PACKAGE_ROOT, ".."))
PROJECTS_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, ".."))
FRAMEWORK_ROOT = os.path.abspath(os.path.join(PROJECTS_DIR, ".."))

# 2. 환경 변수 우선 로드 (패키지 임포트 전)
env_path = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(env_path)

# 3. 경로 추가 (패키지 임포트 전)
sys.path.append(PROJECT_ROOT)
sys.path.append(FRAMEWORK_ROOT)
sys.path.append(PACKAGE_ROOT)

from langchain_core.messages import HumanMessage
from src.utils.multimodal import create_multimodal_message

try:
    from research_agent.graph.builder import builder
except ImportError:
    import sys
    sys.path.append(PROJECT_ROOT)
    from research_agent.graph.builder import builder

st.set_page_config(page_title="Research Agent", page_icon="🔍", layout="wide")
st.title("🔍 Research Agent")
st.caption("리서치 에이전트 연구 및 보고서 생성 테스트 UI입니다.")
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("image"):
            try:
                st.image(message["image"], caption="Uploaded Image", use_container_width=True)
            except Exception as e:
                st.warning(f"이미지를 표시할 수 없습니다: {e}")

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# 사용자 입력
chat_result = multimodal_chat_input(
    placeholder="에이전트에게 복합적인 요청을 해보세요...",
    enable_voice_input=True,
    voice_language="ko-KR",
    key="chat_input"
)

if chat_result:
    prompt = chat_result.get("text")
    files = chat_result.get("files", [])
    
    image_bytes = None
    if files:
        # 첫 번째 파일만 처리 (이미지)
        file_data = files[0].get("data")
        if file_data:
            try:
                base64_data = file_data.split(',')[1] if ',' in file_data else file_data
                image_bytes = base64.b64decode(base64_data)
            except Exception as e:
                st.error(f"이미지 디코딩 실패: {e}")

    # 세션 상태에 저장 (화면 표시용)
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt,
        "image": image_bytes
    })
    
    with st.chat_message("user"):
        if prompt:
            st.markdown(prompt)
        if image_bytes:
            try:
                st.image(image_bytes, caption="Uploaded Image", use_container_width=True)
            except Exception as e:
                st.warning(f"이미지를 표시할 수 없습니다: {e}")

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.status("그래프 노드 실행 중...", expanded=True) as status:
            try:
                # 멀티모달 메시지 생성
                human_msg = create_multimodal_message(prompt, image_bytes)
                
                inputs = {
                    "messages": [human_msg]
                }
                
                st.write("🔄 에이전트 실행 중...")
                response = run_async(builder.ainvoke(inputs))
                st.write("✅ 에이전트 응답 수신 완료")
                
                if hasattr(response, "content"):
                    full_response = response.content
                elif isinstance(response, dict) and "output" in response:
                    full_response = response["output"]
                else:
                    full_response = str(response)
                
                status.update(label="최종 답변 완료!", state="complete", expanded=False)
            except Exception as e:
                full_response = f"⚠️ **에러 발생**: {str(e)}"
                status.update(label="오류 발생", state="error", expanded=True)
                st.exception(e)

        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})

with st.sidebar:
    st.header("Project Info")
    st.info(f"**Project**: research_agent")
    st.info("**Engine**: LangGraph")
    
    st.markdown("---")
    st.header("Actions")
    
    if st.button("대화 기록 초기화"):
        st.session_state.messages = []
        st.rerun()
