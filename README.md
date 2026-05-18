# FastLangFrame 🚀

## 아키텍처

![FastLangFrame Architecture](assets/fastlangframe_architecture.png)

FastLangFrame은 LangChain 및 LangGraph를 기반으로 한 경량급 LLM 에이전트 개발 프레임워크입니다. 표준화된 코어 엔진, 재사용 가능한 툴 세트, 그리고 다양한 프로젝트 템플릿을 제공하여 복잡한 에이전트 시스템을 신속하게 구축하고 안정적으로 운영할 수 있도록 돕습니다.

## 핵심 가치 (Core Philosophy)

![FastLangFrame Philosophy](assets/fastlangframe_philosophy.png)

* **유연함 (Flexibility)**: 선형/비선형 그래프 워크플로우를 자유롭게 구성 가능
* **경량화 (Lightweight)**: 최소한의 핵심 의존성으로 빠른 실행 속도 및 낮은 오버헤드 유지
* **신속한 구현 (Rapid Prototyping)**: CLI 도구(`lapm`)와 템플릿을 통한 즉각적인 프로젝트 시작
* **표준 구조 (Standardization)**: 유지보수가 용이한 일관된 프로젝트 레이아웃 및 API 규격 제공

## 주요 구성요소 (Components)

### 🛠️ Core Engine (`src/core`)

* **Graph Builder**: 복잡한 LangGraph 워크플로우를 쉽게 구성할 수 있는 인터페이스 제공
* **Runtime Context**: HTTP, LLM, MCP 요청을 위한 세마포어 기반 자원 관리 및 상태 제어
* **API Server**: FastAPI 기반의 고성능 비동기 API 서버 (Default: 8888 포트)
  * `/invoke`: 단일 호출 (Blocking)
  * `/stream`: 실시간 SSE 스트리밍
  * `/invoke_batch`: 다중 입력 병렬 처리
  * `/invoke_stream_batch`: 다중 입력 개별 스트리밍 (Interleaved SSE)
  * `/api/v1/auth/callback`: OIDC 인증 처리를 위한 콜백 엔드포인트

### 🔐 Security & Identity

* **Authelia Integration**: 오픈소스 IDP인 Authelia를 활용한 표준 OAuth2/OIDC 인증 및 토큰 인트로스펙션(Introspection) 지원
* **Nginx HTTPS Proxy**: Nginx를 통한 SSL(HTTPS) 지원 및 백엔드/인증 서버 통합 진입점 제공 (Port 8000)
* **RBAC (Role-Based Access Control)**: JWT 토큰 기반의 세밀한 권한 제어 및 API 엔드포인트 보호

### 🧰 Utilities & Connectors (`src/utils`)

* **Connectors**: Database (PostgreSQL, MySQL), Redis, OpenSearch, HTTP, MCP, VectorDB 등 다양한 외부 시스템 연동 모듈 완비
* **Multimodal**: 이미지, 오디오 등 멀티모달 데이터 처리 지원

### 📦 Project Manager (`lapm`)

통합 CLI 도구를 통한 프로젝트 생애주기 관리
* **`create`**: 템플릿 기반 보일러플레이트 생성 (LLM 및 에이전트 유형 선택)
* **`build`**: 최적화된 Docker 이미지 빌드 (프로젝트별 독립 빌드 환경)
* **`deploy`**: Kubernetes 매니페스트 생성 및 배포 지원

---

## CLI 도구 사용법 (`lapm`)

`bin/lapm`은 FastLangFrame의 핵심 CLI 도구로, 프로젝트 생성부터 배포까지의 전 과정을 자동화합니다.

### 1. 프로젝트 생성 (Create)

```bash
# 기본 사용법
./bin/lapm <프로젝트명> create <LLM_번호> <템플릿_번호>

# 예시: OpenAI 기반의 RAG 에이전트 생성
./bin/lapm my_agent create 1 4
```

#### 🤖 지원 LLM Provider (`LLM_번호`)
1. **openai**: OpenAI (GPT-4o, etc.)
2. **azure**: Azure OpenAI Service
3. **deepseek**: DeepSeek API
4. **gemini**: Google Gemini (2.0 Pro/Flash)
5. **claude**: Anthropic Claude (3.5 Sonnet, etc.)
6. **local**: Local LLM (Ollama/vLLM via OpenAI compatible API)

#### 📝 지원 에이전트 유형 (`템플릿_번호`)
1. **simple_agent**: 최소한의 구조를 가진 기본 ReAct 에이전트
2. **deep_agent**: 복잡한 추론과 사고 과정(Thinking)에 최적화된 에이전트
3. **mcp_agent**: MCP(Model Context Protocol)를 통한 외부 도구 연동 특화 에이전트
4. **rag_agent**: 지식 베이스 검색 및 참조(RAG) 기능이 내장된 에이전트
5. **research_agent**: 다단계 웹 검색 및 보고서 작성에 최적화된 연구용 에이전트
6. **multi_agent**: 여러 에이전트 간의 협업 및 오케스트레이션 데모

### 2. Docker 이미지 빌드 (Build)

생성된 프로젝트 디렉토리 내부의 `Dockerfile`을 사용하여 최적화된 이미지를 생성합니다.

```bash
./bin/lapm <프로젝트명> build
```

### 3. 배포 (Deploy)

Kubernetes 환경으로의 배포를 지원합니다. (준비 중)

```bash
./bin/lapm <프로젝트명> deploy
```

### 🧪 Test & Monitoring

* **Streamlit Chat UI**: 생성된 에이전트를 즉시 테스트할 수 있는 웹 인터페이스 (OAuth 연동 완료)
* **Node Trace**: 실행 중인 에이전트의 각 단계(Node)를 시각적으로 추적
* **Langfuse Integration**: LLM 호출 트레이싱, 성능 분석, 프롬프트 관리 및 비용 모니터링

## 기술 스택 (S/W Stack)

* **Runtime**: Python 3.12+
* **Framework**: LangChain, LangGraph, FastAPI, deepagents
* **Security**: Authelia (OAuth2/OIDC), PyJWT
* **Observability**: Langfuse (Tracing, Metrics, Prompt Management)
* **DevOps**: Docker (Nginx, Redis, Authelia, Langfuse, ClickHouse), Kubernetes, Poetry, Copier
* **Storage/Middleware**: SQLAlchemy (PostgreSQL/MySQL), Alembic, Redis, OpenSearch, ClickHouse, MinIO
* **UI/Test**: Streamlit, Pytest

## 디렉토리 구조

```text
.
├── bin/                    # lapm 등 실행 가능한 CLI 도구
├── conductor/              # 프로젝트 관리 및 워크플로우 가이드 (Product, Specs, Plans)
├── nginx/                  # Nginx 설정 및 SSL 인증서 (HTTPS 프록시)
├── authelia/               # Authelia 설정 및 사용자 데이터베이스
├── projects/               # 생성된 개별 에이전트 프로젝트 저장소
├── src/                    # FastLangFrame 핵심 프레임워크 소스
│   ├── core/               # 그래프 빌더, 런타임, API 서버 로직
│   │   └── runtime/        # 자원 관리 및 세마포어 제어
│   ├── common/             # 공통 예외, 설정, 상수, 로깅, 미들웨어(Auth)
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

### 2. 인프라 및 환경 설정

1. **인프라(Nginx, Authelia, Redis, PostgreSQL, Langfuse) 기동**:

   ```bash
   docker compose up -d
   ```

2. **환경 변수 설정**:

   `.env` 파일을 생성하고 LLM API Key 및 Authelia, DB 설정을 입력합니다. Langfuse용 `LANGFUSE_NEXTAUTH_SECRET`, `LANGFUSE_SALT`, `ENCRYPTION_KEY`는 무작위 문자열로 설정하세요. (Self-hosted Langfuse 기동을 위해 필요)

### 🗄️ 기본 DB 접속 정보 (Default Credentials)

Docker Compose로 기동된 PostgreSQL의 기본 접속 정보입니다.

* **Host**: `localhost` (또는 `postgres`)
* **Port**: `5432`
* **Username**: `admin`
* **Password**: `fastlangframe1@`
* **Database**: `backend`
* **Default Schema**: `public`

### 3. 서버 실행

```bash
# 기본 포트 8888로 실행 (Nginx가 8000 -> 8888로 프록시)
PYTHONPATH=. poetry run python -m src.core.server --port 8888
```

---

## 설정 및 인증 가이드 (Configuration & Auth)

### 🤖 LLM Provider 설정 (`.env`)

FastLangFrame은 다양한 LLM Provider를 지원합니다. 사용하는 Provider에 맞춰 `.env` 파일을 설정하세요.

#### 1. OpenAI

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-4o  # 또는 gpt-4-turbo, gpt-3.5-turbo
```

#### 2. Anthropic (Claude)

```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key_here
MODEL_NAME=claude-3-5-sonnet-20240620  # 또는 claude-3-opus-20240229
```

#### 3. Google Gemini

```bash
LLM_PROVIDER=google
GOOGLE_API_KEY=your_google_api_key_here
MODEL_NAME=gemini-2.5-pro  # 또는 gemini-2.5-flash
```

### ⚙️ 환경 변수 설정 (`.env`)

Authelia와 Nginx 환경에서 정상적인 인증을 위해 다음 변수들이 필요합니다.

```bash
# --- Authelia OIDC Configuration ---
AUTHELIA_URL=http://localhost:9091
AUTHELIA_INTROSPECTION_URL=http://localhost:9091/api/oidc/introspection
AUTHELIA_TOKEN_URL=http://localhost:9091/api/oidc/token
AUTHELIA_AUTHORIZATION_URL=http://localhost:9091/api/oidc/authorization
AUTHELIA_CLIENT_ID=fastapi
AUTHELIA_CLIENT_SECRET=fastapi_secret
AUTHELIA_REDIRECT_URI=http://localhost:8888/api/v1/auth/callback
```

### 🔐 인증 및 API 테스트 방법

#### 1. Swagger UI를 통한 OIDC 인증 (추천)

실 운영 환경과 동일한 브라우저 기반 인증 흐름을 테스트합니다.

1. **Swagger 접속**: `https://localhost:8000/docs` (Nginx HTTPS 포트)
2. **보안 경고 우회**: 브라우저에서 '고급' 클릭 후 이동하거나, 화면에 `thisisunsafe`를 입력하여 자체 서명 인증서를 통과합니다.
3. **Authorize 클릭**: 우측 상단의 **Authorize** 버튼 클릭.
4. **OIDC Flow 선택**: `oidc_scheme` 섹션에서 모든 스코프를 체크하고 **Authorize** 클릭.
5. **Authelia 로그인**: 리다이렉트된 Authelia 페이지에서 로그인 (`user` / `password`).
6. **인증 완료**: Swagger로 돌아오면 이제 모든 API를 인증된 상태로 호출할 수 있습니다.

#### 2. 로컬 개발용 간이 인증 (Password Flow)

Authelia 없이 백엔드 로직만 빠르게 테스트할 때 사용합니다.

1. **Authorize 클릭**: `password_scheme` 섹션 선택.
2. **정보 입력**:
    * **Username**: `testuser`
    * **Password**: `testpassword`
3. **로그인**: 내부 `/token` 엔드포인트를 통해 발급된 임시 토큰으로 인증됩니다.

#### 3. Authelia 직접 접속 및 세션 확인

인증 서버 상태를 직접 확인하려면 `http://localhost:9091`에 접속하세요.

---

## 🔍 관측성 및 트레이싱 (Langfuse)

FastLangFrame은 [Langfuse](https://langfuse.com/)를 통해 LLM 에이전트의 복잡한 실행 과정을 투명하게 기록하고 분석합니다.

### ⚙️ Langfuse 설정 (`.env`)

자가 호스팅(Self-hosted) Langfuse 서버 및 SDK 연동을 위한 설정입니다.

```bash
# Langfuse SDK 연동 (애플리케이션용)
LANGFUSE_PUBLIC_KEY=pk-lf-...  # Langfuse UI에서 프로젝트 생성 후 발급
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=http://localhost:3000

# Langfuse 서버 기동 설정 (Docker Compose용)
LANGFUSE_DATABASE_URL=postgresql://admin:fastlangframe1@postgres:5432/langfuse
LANGFUSE_NEXTAUTH_URL=http://localhost:3000
LANGFUSE_NEXTAUTH_SECRET=your_random_secret
LANGFUSE_SALT=your_random_salt
ENCRYPTION_KEY=your_32char_encryption_key
```

### 🛠️ 주요 기능

* **자동 트레이싱**: API 서버(`src/core/server.py`)가 모든 요청에 대해 Langfuse 콜백을 자동으로 주입합니다. 사용자는 별도의 코드 수정 없이 LLM 호출, 도구 사용, 그래프 노드 전이 과정을 추적할 수 있습니다.
* **메타데이터 연동**: Authelia를 통해 인증된 `user_id`와 LangGraph의 `thread_id`(session_id)가 Langfuse 트레이스에 자동으로 매핑되어 사용자별/세션별 분석이 가능합니다.
* **성능 및 비용 분석**: 모델별 토큰 사용량, 지연 시간(Latency), 성공률 등을 대시보드에서 한눈에 파악할 수 있습니다.

### 📊 대시보드 접속

1. `http://localhost:3000`에 접속합니다.
2. 첫 접속 시 계정을 생성(Sign up)합니다.
3. 새 프로젝트를 생성하고 발급된 API Key를 `.env`에 반영합니다.
4. 에이전트 호출 후 **Traces** 메뉴에서 실행 상세 내역을 확인합니다.

---

## 데이터베이스 연동 가이드 (Database Integration)

FastLangFrame은 SQLModel(SQLAlchemy)과 Alembic을 통한 표준화된 DB 연동 기능을 제공합니다.

### ⚙️ DB 설정 (`.env`)

```bash
DATABASE_DRIVER=postgresql  # 또는 mysql, sqlite
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USERNAME=admin
DATABASE_PASSWORD=fastlangframe1@
DATABASE_DBNAME=backend
DATABASE_SCHEMA=public      # PostgreSQL 전용
```

### 📝 데이터 모델 정의

`src/common/types/models.py` 또는 각 도메인 하위에 `SQLModel`을 사용하여 테이블을 정의합니다.

```python
from typing import Optional
from sqlmodel import SQLModel, Field

class MyModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
```

### 💉 세션 주입 및 CRUD 처리

FastAPI의 `Depends`를 사용하여 DB 세션을 주입받습니다.

```python
from fastapi import Depends
from sqlmodel import Session
from src.utils.connectors.db.database import get_session

@app.post("/items/")
def create_item(item: MyModel, session: Session = Depends(get_session)):
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
```

### 🔄 데이터베이스 마이그레이션 (Alembic)

1. **마이그레이션 파일 생성**:

   ```bash
   # 스키마 변경 후 실행
   poetry run alembic revision --autogenerate -m "Add new table"
   ```

2. **DB 반영**:

   ```bash
   poetry run alembic upgrade head
   ```

---

## Chat Test UI 가이드

FastLangFrame은 에이전트의 추론 과정을 시각화하여 디버깅을 돕는 전용 UI를 제공합니다.

* **실시간 추적**: LangGraph의 각 노드 실행 상태와 도구 호출 결과를 실시간 확인
* **로그 뷰어**: 에이전트 내부에서 발생하는 상세 로그를 스트리밍 형태로 제공
* **히스토리 관리**: 대화 초기화 및 세션별 테스트 데이터 관리
* **사용자 인증**: Authelia 연동을 통한 안전한 대화 세션 보호

![Chat Test UI Screenshot](docs/images/chat_test_screenshot.png)

## 라이선스

이 프로젝트는 [MIT License](LICENSE)를 따릅니다.

�� 프로젝트는 [MIT License](LICENSE)를 따릅니다.
