import os
import sys
from dotenv import load_dotenv

# 1. 경로 설정 (패키지 구조와 프로젝트 루트 고려)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
PROJECTS_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, ".."))
FRAMEWORK_ROOT = os.path.abspath(os.path.join(PROJECTS_DIR, ".."))

# 2. .env 파일 로드 (패키지 임포트 전, 우선순위 높임)
# 프로젝트 루트(PROJECT_ROOT)에 있는 .env를 로드합니다.
env_path = os.path.join(CURRENT_DIR, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)

# 3. 경로 추가 (패키지 임포트 전)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, FRAMEWORK_ROOT)

import uvicorn
from <%project_name%>.graph.builder import agent_graph
from src.core.server import create_agent_app

# FastAPI app creation
app = create_agent_app(agent_graph)

def run_api_server(port: int = 8888):
    """Start the API server"""
    uvicorn.run(app, host="0.0.0.0", port=port)

def example_api_endpoints(port: int = 8888):
    """Wrapper to show new features"""
    print(f"Starting FastAPI Server on port {port}...")
    print("  Endpoints:")
    print("    - POST /invoke")
    print("    - POST /stream")
    print("    - POST /invoke_batch")
    print("    - POST /invoke_stream_batch")
    run_api_server(port)

def main():
    """Entry point to demonstrate features."""
    import sys
    port = 8888
    if "--port" in sys.argv:
        port_idx = sys.argv.index("--port") + 1
        if port_idx < len(sys.argv):
            port = int(sys.argv[port_idx])
    
    example_api_endpoints(port)

if __name__ == "__main__":
    main()
