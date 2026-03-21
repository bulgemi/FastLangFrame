# MI Agent 샘플 작업 설명

이 문서는 MI Agent 통합 검색 샘플 작업에 대한 설명 문서입니다.
(개발 및 문서 작업: 이소영)

***
## 1. 개요
### 0) MI 서비스 흐름도
![MI Agent 서비스 흐름도]()


### 1) 배경
이 프로젝트는 LangGraph 프레임워크를 기반으로 통합검색 서비스를 제공하는 AI Agent를 구현한 샘플입니다. 
사용자 질의 의도를 분석해 다양한 데이터 소스에서 데이터 검색 후, 검색된 내용 기반으로 분석 및 결과 도출ㅂ니다.
다양한 시나리오에 맞춰 agent를 재사용 및 확장하거나 개선할 수 있도록 설계했습니다.

### 2) 기능
+ 사용자 질의 입력
  - 사용자 질의(자연어)입력
+ 질의 의도 분류
  - 시나리오 분류 (LLM호출)
  - 답변 유형 결정
  - 질의 대상 데이터 소스 결정
+ 라우팅
  - 시나리오 타입에 따라 flow map 팩토리 참고하여 sub graph실행
+ 사용자 질의 구조화
  - 사용자 질의 기반 구조화 작업 (LLM호출, MCP Server호출(text to sql))
+ 데이터 검색
  - 문서 검색
  - DB 검색
  - 웹 검색
+ 동적으로 생성된 Graph시각화

### 3) 개발 언어 및 lib
langgraph기반
python 3.13기반
fastapi기반

### 4) 설계 방안
1. LangGraph 기반 유연한 흐름 제어
LangGraph의 StateGraph / CompiledStateGraph 구조를 통해 사용자 시나리오 흐름 분기를 동적으로 구성
supervisor를 이용한 병렬 작업 처리 및 제어 지원

2. 고응집/저결합 구조
노드별 기능을 책임 단위로 분리 (nodes/ 내부에 목적별 폴더 구성)
공통 모듈(common/), 외부 연동(connectors/), 도메인 상태(state/)가 명확하게 분리

3. 확장성과 유지보수성
신규 시나리오 추가 시 orchestration/, flows/, nodes/에 최소 변경만으로 확장 가능
구조화된 쿼리 생성, 요약, 시각화 등 다양한 기능이 독립적인 모듈로 제공되어 재사용 용이


***
## 2. Project Structure
### 1) 기본 구조


### 2) 상세 구조
```
.
├── apps
│   ├── agents
│   │   └── mi_agent                                # MI Agent (통합 검색)
│   │       ├── orchestration                       # 
│   │       │   ├── supervisors                     # 
│   │       │   │   └── search_supervisor.py        # 
│   │       │   ├── routers                         # 
│   │       │   │   └── dispatcher.py               # 
│   │       │   └── policies                        # 
│   │       │       └── retrieval_policy.py         # 
│   │       ├── subgraphs                           # 
│   │       │   ├── rdb_search                      #
│   │       │   │   ├── graph.py                    # 
│   │       │   │   ├── state.py                    #
│   │       │   │   └── nodes                       #
│   │       │   │       ├──prepare.py               # 
│   │       │   │       ├──gen_guard.py             # 
│   │       │   │       └──execute.py               # 
│   │       │   ├── web_search                      # 
│   │       │   │   ├── graph.py                    # 
│   │       │   │   ├── state.py                    #
│   │       │   │   └── nodes                       #
│   │       │   │       ├──prepare.py               # 
│   │       │   │       ├──gen_guard.py             # 
│   │       │   │       └──execute.py               # 
│   │       │   └── vdb_search                      # 
│   │       │       ├── graph.py                    # 
│   │       │       ├── state.py                    #
│   │       │       └── nodes                       #
│   │       │           ├──prepare.py               # 
│   │       │           ├──gen_guard.py             # 
│   │       │           └──execute.py               # 
│   │       ├── graph_builder.py                    # 
│   │       ├── nodes                               # 
│   │       ├── components                          # 
│   │       ├── tools                               # 
│   │       ├── state                               # 
│   │       ├── prompts                             # 
│   │       └── utils                               # 유틸리티
├── README.md
└── pyproject.toml                  # poetry의존성 관리 및 ruff관련 설정
```
***