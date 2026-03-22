# FastLangFrame

## 아키텍처

![FastLangFrame Architecture](assets/fastlangframe_architecture.png)

FastLangFrame 프레임워크 아키텍처는 Langchain/Langgraph 기반에 Core, Tool, Test, 확장 포인트, 표준 구조 제공으로 구성되어 있습니다.

## 철학

![FastLangFrame Philosophy](assets/fastlangframe_philosophy.png)

FastLangFrame은 다음과 같은 핵심 철학을 바탕으로 설계되었습니다.

* **유연함**: 다양한 요구사항과 환경에 유연하게 대응할 수 있는 구조를 지향합니다.
* **경량화**: 불필요한 의존성을 줄이고 핵심 기능에 집중하여 가볍고 빠르게 동작합니다.
* **빠른 구현 및 검증**: 아이디어를 신속하게 구현하고 검증할 수 있는 환경을 제공합니다.
* **명확한 구조 제공**: 개발자가 쉽게 이해하고 확장할 수 있는 명확하고 직관적인 프로젝트 구조를 제공합니다.

## 아이콘

![FastLangFrame Icon](assets/icons/favicon-32x32.png)

## 구성요소

### Core

* **LLM Agent Project Manager (lapm)**: 프로젝트 생성, 빌드, 배포를 위한 통합 CLI 도구
  * `create`: 템플릿 기반 프로젝트 생성
  * `build`: Docker 이미지 빌드
  * `deploy`: Kubernetes 환경 배포

### Graph (API Server)

* **FastAPI 기반 표준 API 서버**: 모든 에이전트 프로젝트에 기본 내장 (Default Port: 8888)
  * **Swagger UI 제공**: `{host}:8888/docs`를 통해 엔드포인트 대화식 테스트 가능
  * **표준 엔드포인트**:
    * `POST /invoke`: 에이전트 단일 실행
    * `POST /stream`: 실시간 이벤트 스트리밍 (SSE)
    * `POST /invoke_batch`: 다중 입력 병렬 처리
    * `POST /invoke_stream_batch`: 다중 입력 개별 스트리밍 (Interleaved SSE)
* **LLM 아키텍처**: LangChain 및 LangGraph를 활용한 선형/비선형 에이전트 워크플로우 구현

### Utils

* Database(MySQL, PostgreSQL), Opensearch, Redis 연동 유틸리티 패키지

### Test

* 구현한 LLM Agent 또는 Deep Agent의 기능을 검증하기 위한 테스트 패키지
* stremlit 기반 UI 테스트 기능 제공

### 확장 포인트

* MCP, Skill 등 외부 모듈 연동을 위한 확장 포인트

## 템플릿

* 다양한 구성의 LLM Agent 또는 Deep Agent를 위한 템플릿 (copier 기반)

## S/W Stack

* Python 3.12
* copier
* streamlit
* fastapi
* Langchain
* Langgraph
* Pydantic
* Alembic
* SQLAlchemy
* Opensearch
* Redis
* poetry

## 디렉토리 구조

``` text
.
├── LICENSE: 오픈소스 라이선스 파일
├── README.md: 프로젝트 소개 및 가이드 파일
├── assets: 마크다운 등에서 사용되는 정적 자원(이미지 등)
│   └── icons: 서비스/앱 아이콘 모음
├── bin: 실행 가능한 쉘 스크립트 도구들
├── docs: 문서 파일 디렉토리
├── projects: FastLangFrame을 기반으로 구현된 실제 프로젝트 모음
│   └── {project_name}: 실제 구현된 Agent 프로젝트
│      ├── core: 코어 모듈
│      ├── common: 공통 모듈
│      ├── graph: 그래프 모듈
│      ├── prompts: 프롬프트 모듈
│      ├── states: 상태 모듈
│      ├── utils: 유틸리티 모듈
│      ├── config: 설정 모듈
│      ├── docker: 도커 관련 파일
│      ├── k8s: 쿠버네티스 관련 파일
│      ├── chat_test: stremlit 기반 UI 테스트
│      └── tools: Tool, MCP, Skills 모듈
├── pyproject.toml: 의존성 및 환경 설정 메타 파일
├── src: FastLangFrame 핵심 소스코드 폴더
│   ├── core: 프레임워크 핵심 기능 로직
│   ├── common: 프레임워크 공통 모듈
│   └── utils: 유틸리티 함수 묶음
├── test: FastLangFrame 단위 테스트 코드 폴더
└── templates: 프로젝트 보일러플레이트 템플릿(Copier) 저장소
     ├── docker: 도커 관련 파일 템플릿
     ├── k8s: 쿠버네티스 관련 파일 템플릿
     ├── simple_agent: Langchain 기반 Simple Agent 템플릿
     ├── rag_agent: Langchain 기반 RAG Agent 템플릿
     ├── multi_agent: Langchain 기반 Multi Agent 템플릿
     ├── mcp_agent: Langchain 기반 MCP Agent 템플릿
     └── deep_agent: Langgraph 기반 Deep Agent 템플릿
```

## 동작 흐름 (Quick Start)

1. **프로젝트 생성**:

   ```bash
   # ./bin/lapm <프로젝트명> create <LLM_NUMBER> <TEMPLATE_NUMBER>
   ./bin/lapm my_agent create 1 1
   ```

   * **LLM Provider 선택 (1-6)**: 1:openai, 2:azure, 3:deepseek, 4:gemini, 5:claude, 6:local
   * **템플릿 선택 (1-5)**: 1:simple_agent, 2:rag_agent, 3:multi_agent, 4:mcp_agent, 5:deep_agent

2. **환경 변수 설정**:
   생성된 프로젝트 폴더 내 `.env` 파일을 수정합니다.
   * **OpenAI**: `OPENAI_API_KEY`, `MODEL_NAME`
   * **Azure**: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_DEPLOYMENT_NAME`

3. **API 서버 실행 및 검증**:

   ```bash
   # 생성된 프로젝트 내부 폴더로 이동 후 실행
   cd projects/my_agent/my_agent
   python3 main.py --port 8888
   ```

   * 브라우저에서 `http://localhost:8888/docs` 접속하여 Swagger UI 테스트

4. **Chat UI 테스트 실행**:

   ```bash
   streamlit run chat_test/app.py
   ```

   * 웹 브라우저를 통해 실시간 대화 및 실행 로그(Node Trace) 확인

## Streamlit Chat Test UI

FastLangFrame은 생성된 에이전트를 즉시 테스트할 수 있는 웹 기반 Chat UI를 제공합니다.

### 실행 방법

1. 생성된 프로젝트 폴더로 이동합니다.
2. 다음 명령어를 실행하여 Streamlit 앱을 구동합니다:

   ```bash
   # /projects/test_deep 디렉토리 기준 예시
   streamlit run test_deep/chat_test/app.py
   ```

3. 브라우저에서 `http://localhost:8501` (또는 지정된 포트)로 접속하여 에이전트와 대화합니다.

### 주요 기능

* **실시간 노드 실행 추적**: 각 에이전트의 내부 실행 상태(LangGraph 노드, 도구 호출 등)를 실시간으로 확인 가능합니다.
* **히스토리 초기화**: 우측 사이드바의 버튼을 통해 대화 내용을 초기화하고 새 테스트를 시작할 수 있습니다.
* **다양한 에이전트 지원**: Simple, RAG, Multi, MCP, Deep 등 모든 에이전트 유형에 최적화된 UI를 제공합니다.

![Chat Test UI Screenshot](docs/images/chat_test_screenshot.png)
