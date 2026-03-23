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

# 3. 경로 추가 (패키지 임포트 전)
sys.path.append(PROJECT_ROOT)
sys.path.append(FRAMEWORK_ROOT)
sys.path.append(PACKAGE_ROOT)

from langchain_core.messages import HumanMessage
from src.utils.multimodal import create_multimodal_message

try:
    from <%project_name%> import builder
except ImportError:
    # 패키지 명칭이 다를 경우를 위한 폴백
    from <%project_name%> import builder

st.set_page_config(page_title="Simple Chat", page_icon="🤖", layout="wide")
st.title("🤖 Simple Chat")
st.caption("FastLangFrame 기반 에이전트의 기능을 실시간으로 테스트합니다.")
st.markdown("---")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 내용 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("image"):
            try:
                st.image(message["image"], caption="Uploaded Image", use_container_width=True)
            except Exception as e:
                st.warning(f"이미지를 표시할 수 없습니다: {e}")

# 비동기 실행을 위한 헬퍼
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# 사용자 입력
if prompt := st.chat_input("에이전트에게 복잡한 요청을 해보세요..."):
    # 업로드된 파일 확인
    uploaded_file = st.session_state.get("uploaded_file")
    image_bytes = uploaded_file.getvalue() if uploaded_file else None
    
    # 세션 상태에 저장 (화면 표시용)
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt,
        "image": image_bytes
    })
    
    with st.chat_message("user"):
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
                elif isinstance(response, dict):
                    if "messages" in response:
                        last_msg = response["messages"][-1]
                        # Check if last_msg is a dict (e.g., from tool_code) or an object with content
                        if isinstance(last_msg, dict) and "content" in last_msg:
                            full_response = last_msg["content"]
                        elif hasattr(last_msg, "content"):
                            full_response = last_msg.content
                        else:
                            full_response = str(last_msg)
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
    st.info("**Engine**: LangGraph")
    
    st.markdown("---")
    st.header("Multimodal Input")
    st.session_state.uploaded_file = st.file_uploader(
        "이미지를 업로드하세요", 
        type=["jpg", "jpeg", "png"],
        help="이미지를 선택한 후 채팅을 입력하면 에이전트에게 함께 전달됩니다."
    )
    
    if st.button("대화 기록 초기화"):
        st.session_state.messages = []
        st.rerun()
