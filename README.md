# FastLangFrame 🚀

## 아키텍처

![FastLangFrame Architecture](assets/fastlangframe_architecture.png)

FastLangFrame은 LangChain 및 LangGraph를 기반으로 한 경량급 LLM 에이전트 개발 프레임워크입니다. 표준화된 코어 엔진, 재사용 가능한 툴 세트, 그리고 다양한 프로젝트 템플릿을 제공하여 복잡한 에이전트 시스템을 신속하게 구축하고 안정적으로 운영할 수 있도록 돕습니다.

## 핵심 가치 (Core Philosophy)

![FastLangFrame Philosophy](assets/fastlangframe_philosophy.png)

*   **유연함 (Flexibility)**: 선형/비선형 그래프 워크플로우를 자유롭게 구성 가능
*   **경량화 (Lightweight)**: 최소한의 핵심 의존성으로 빠른 실행 속도 및 낮은 오버헤드 유지
*   **신속한 구현 (Rapid Prototyping)**: CLI 도구(`lapm`)와 템플릿을 통한 즉각적인 프로젝트 시작
*   **표준 구조 (Standardization)**: 유지보수가 용이한 일관된 프로젝트 레이아웃 및 API 규격 제공

## 주요 구성요소 (Components)

### 🛠️ Core Engine (`src/core`)
*   **Graph Builder**: 복잡한 LangGraph 워크플로우를 쉽게 구성할 수 있는 인터페이스 제공
*   **Runtime Context**: HTTP, LLM, MCP 요청을 위한 세마포어 기반 자원 관리 및 상태 제어
*   **API Server**: FastAPI 기반의 고성능 비동기 API 서버 (Default: 8888 포트)
    *   `/invoke`: 단일 호출 (Blocking)
    *   `/stream`: 실시간 SSE 스트리밍
    *   `/invoke_batch`: 다중 입력 병렬 처리
    *   `/invoke_stream_batch`: 다중 입력 개별 스트리밍 (Interleaved SSE)

### 🧰 Utilities & Connectors (`src/utils`)
*   **Connectors**: Database (PostgreSQL, MySQL), Redis, OpenSearch, HTTP, MCP, VectorDB 등 다양한 외부 시스템 연동 모듈 완비
*   **Multimodal**: 이미지, 오디오 등 멀티모달 데이터 처리 지원

### 📦 Project Manager (`lapm`)
*   통합 CLI 도구를 통한 프로젝트 생애주기 관리
*   `create`: 템플릿 기반 보일러플레이트 생성
*   `build`: 최적화된 Docker 이미지 빌드
*   `deploy`: Kubernetes 매니페스트 생성 및 배포

### 🧪 Test & Monitoring
*   **Streamlit Chat UI**: 생성된 에이전트를 즉시 테스트할 수 있는 웹 인터페이스
*   **Node Trace**: 실행 중인 에이전트의 각 단계(Node)를 시각적으로 추적

## 템플릿 종류

*   **Simple Agent**: 기본적인 LangChain 기반 단일 에이전트
*   **RAG Agent**: 지식 기반 검색 및 답변이 가능한 RAG 최적화 구조
*   **Multi-Agent**: 다수의 에이전트가 협업하는 분산 워크플로우
*   **MCP Agent**: Model Context Protocol을 활용한 강력한 확장성 제공
*   **Deep Agent**: `deepagents` 라이브러리를 활용한 고도화된 추론 에이전트

## 기술 스택 (S/W Stack)

*   **Runtime**: Python 3.12+
*   **Framework**: LangChain, LangGraph, FastAPI, deepagents
*   **DevOps**: Docker, Kubernetes, Poetry, Copier
*   **Storage/Middleware**: SQLAlchemy (PostgreSQL/MySQL), Alembic, Redis, OpenSearch
*   **UI/Test**: Streamlit, Pytest

## 디렉토리 구조

```text
.
├── bin/                    # lapm 등 실행 가능한 CLI 도구
├── conductor/              # 프로젝트 관리 및 워크플로우 가이드 (Product, Specs, Plans)
├── projects/               # 생성된 개별 에이전트 프로젝트 저장소
├── src/                    # FastLangFrame 핵심 프레임워크 소스
│   ├── core/               # 그래프 빌더, 런타임, API 서버 로직
│   │   └── runtime/        # 자원 관리 및 세마포어 제어
│   ├── common/             # 공통 예외, 설정, 상수, 로깅
│   └── utils/              # 각종 커넥터(DB, LLM, MCP 등) 및 유틸리티
├── templates/              # 프로젝트 생성을 위한 Copier 템플릿
├── test/                   # 프레임워크 단위 테스트
└── assets/                 # 이미지, 아이콘 등 정적 자원
```

## 시작하기 (Quick Start)

### 1. 프로젝트 생성
`lapm` CLI를 사용하여 새로운 프로젝트를 생성합니다.

```bash
# ./bin/lapm <프로젝트명> create <LLM_provider_choice> <Template_choice>
./bin/lapm my_agent create 1 1
```
*   **LLM Provider**: 1:OpenAI, 2:Azure, 3:DeepSeek, 4:Gemini, 5:Claude, 6:Local
*   **Template**: 1:Simple, 2:RAG, 3:Multi, 4:MCP, 5:Deep

### 2. 환경 설정
생성된 프로젝트 폴더 (`projects/my_agent/my_agent`) 내의 `.env` 파일을 수정하여 API Key 및 모델 정보를 설정합니다.

### 3. 서버 실행
```bash
cd projects/my_agent/my_agent
python3 main.py --port 8888
```
*   브라우저에서 `http://localhost:8888/docs` 접속하여 Swagger UI 테스트

### 4. UI 테스트 실행
```bash
streamlit run chat_test/app.py
```

## Chat Test UI 가이드

FastLangFrame은 에이전트의 추론 과정을 시각화하여 디버깅을 돕는 전용 UI를 제공합니다.

*   **실시간 추적**: LangGraph의 각 노드 실행 상태와 도구 호출 결과를 실시간 확인
*   **로그 뷰어**: 에이전트 내부에서 발생하는 상세 로그를 스트리밍 형태로 제공
*   **히스토리 관리**: 대화 초기화 및 세션별 테스트 데이터 관리

![Chat Test UI Screenshot](docs/images/chat_test_screenshot.png)

## 라이선스

이 프로젝트는 [MIT License](LICENSE)를 따릅니다.
