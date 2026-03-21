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

* **LLM Agent Project Manager(lapm)**: Agent 프로젝트 관리 및 실행을 위한 Core 컴포넌트

### Graph

* langchain, lang graph 기반 Agent or Deep Agent 핵심 패키지

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
* Langchain
* Langgraph
* Pydantic
* Alembic
* SQLAlchemy
* Opensearch
* Redis
* poetry

## 디렉토리 구조

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

## 동작 흐름

1. bin/lapm 실행
2. `프로젝트명` 입력
3. LLM Provider 선택
    * openai
    * azure
    * deepseek
    * gemini
    * claude
    * local
4. 템플릿 선택
    * simple_agent: Langchain 기반 Simple Agent
    * rag_agent: Langchain 기반 RAG Agent
    * multi_agent: Langchain 기반 Multi Agent
    * mcp_agent: Langchain 기반 MCP Agent
    * deep_agent: Langgraph 기반 Deep Agent
5. 템플릿에 따라 프로젝트 생성
    * copier를 사용하여 템플릿에 따라 프로젝트 생성
    * LLM Provider, DB, Redis, Opensearch 등 설정은 사용자가 직접 프로젝트 폴더 내에서 Config 파일 수정
6. Chat UI 테스트 실행
    * 생성된 프로젝트 폴더 내에서 `streamlit run {project_name}/chat_test/app.py` 실행
    * 웹 브라우저를 통해 에이전트와 실시간 대화 및 기능 검증
