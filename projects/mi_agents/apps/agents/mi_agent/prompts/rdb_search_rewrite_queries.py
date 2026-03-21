def build_rdb_search_queries_prompt(rewritten_query: str, output_example: str) -> str:
    return f"""
당신의 역할:
- 사용자의 자연어 질문을 데이터 검색에 적합한 단일 질의들로 **필요할 때만** 분리하고,
- 각 질의에 대해 Azure AI Search full text 검색에 바로 사용할 수 있는 search_text를 생성한다.

출력 규격(반드시 JSON 배열):
{output_example}

핵심 규칙(속성 묶기):
- **같은 대상**(자산/상품/코드/만기/거래소/시간 제약이 동일) 안에서 **여러 속성(지표/필드)**을 요청하면, **하나의 query 객체로 묶어라.**
  - 예: "2025-06-05 Henry Hub 1개월물의 종가, 정산가, 시가" → 하나의 query
- **대상이 다르면 분리**한다. (자산/코드/만기/거래소가 다르면 대상이 다름)
  - 예: "Henry Hub와 Dubai Crude 근월물 종가" → 대상 2개이므로 2개 query
- **시간 표현 분리 기준**:
  - 하나의 연속된 기간(예: 2025-01-01~2025-01-31), 동일 대상의 소수 시점 비교(예: 2025-06-05와 2025-06-06) 등은 **하나의 query**로 유지한다.
  - 완전히 **서로 다른 대상 + 서로 다른 시점**이 뒤섞여 있으면 **대상 기준으로만 분리**하고, 시간 표현은 각 query 문장에 명시한다.
- 속성(지표)을 **세부 항목별로 쪼개서 별도 query로 만들지 마라.** (예: 종가·정산가·시가 각각으로 분리 금지)

질의 분리 규칙(대상 중심):
1) 핵심 대상 식별: 자산/상품명, 코드(symbol), 거래소, 만기/월물(근월물/1M/Front month 등), 통화 등.
2) 같은 대상이면 **단일 query**로 유지하고, 요청된 **여러 속성**은 query 문장에 모두 포함한다.
3) 다른 대상이면 **대상별로만** 분리한다. (속성 기준 분리 금지)
4) 모호하면 원문 의미를 유지하되 가능한 한 구체화한다(상품/기간/만기/속성 등).
5) **날짜/기간 표현은 query에 반드시 포함한다.** (YYYY-MM-DD, YYYY/MM/DD, YYYY년 M월, YYYY년 M월 D일 등 원문 그대로)

search_text 작성 규칙:
- 목적: Azure AI Search full text 검색 최적화(대상 판별과 관련 문서/테이블/사전 검색).
- 키워드 개수: 8~12개. 과도한 일반어 제거. **대소문자/중복 제거**.
- 구분: **공백만** 사용. 쉼표·따옴표·괄호 금지. 멀티워드도 따옴표 없이 공백으로 둔다(예: Henry Hub).
- 포함 요소:
  - 핵심 엔티티(자산/지표/코드/거래소), 도메인 용어(선물/futures 등)
  - **요청된 모든 속성의 동의어 세트**(예: 종가/정산가/시가 → closing price/settlement/open 등)
  - 만기/월물 표기 동의어(근월물/front month/near month/1개월물/1M/prompt month 등)
  - 필요 시 한국어/영어 변형(HenryHub / Henry Hub)
- **날짜/기간 표기는 search_text에서 제외한다.**
- 예시 속성 동의어(필요 시 활용):
  - 종가: 종가 최종거래가격 close closing "last trade" last price trdprc
  - 정산가: 정산가 정산가격 settlement settle "settlement price"
  - 시가: 시가 개장가 open "opening price" open price open_prc
  - 고가/저가: 고가 high 저가 low
  - 거래량: 거래량 volume vol
  - 근월물 계열: 근월물 최근월물 front month near month 1개월물 1M prompt month

검증 규칙:
- 각 객체의 "query"에는 입력 질의의 날짜/기간이 반드시 포함되어야 한다.
- 각 객체의 "search_text"에는 날짜/기간이 포함되면 안 된다.

예시 A) 속성 다중 요청(분리 금지):
입력: "2025-06-05 Henry Hub 1개월물의 종가, 정산가, 시가 가격 알려줘"
출력:
[
  {{
    "query": "2025-06-05 Henry Hub 1개월물의 종가, 정산가, 시가를 알려줘",
    "search_text": "HenryHub Henry Hub 1개월물 front month near month 천연가스 선물 futures 가격 종가 closing 정산가 settlement 시가 open"
  }}
]

예시 B) 대상 2개(대상 기준 분리):
입력: "2025-06-05 Henry Hub 1개월물과 Dubai Crude 근월물의 종가 알려줘"
출력:
[
  {{
    "query": "2025-06-05 Henry Hub 1개월물 종가 알려줘",
    "search_text": "HenryHub Henry Hub 1개월물 front month near month 천연가스 선물 futures 가격 종가 closing"
  }},
  {{
    "query": "2025-06-05 Dubai Crude 근월물 종가 알려줘",
    "search_text": "Dubai crude 두바이유 근월물 front month 원유 석유 선물 futures 가격 종가 closing"
  }}
]

예시 C) 동일 대상, 두 시점 비교(단일 query 유지):
입력: "2025-06-05와 2025-06-06 Henry Hub 1개월물 종가와 거래량 알려줘"
출력:
[
  {{
    "query": "2025-06-05와 2025-06-06 Henry Hub 1개월물의 종가와 거래량을 알려줘",
    "search_text": "HenryHub Henry Hub 1개월물 front month 천연가스 선물 futures 가격 종가 closing 거래량 volume vol"
  }}
]

이제 아래 사용자 질의에 대해 위 규칙을 적용해 결과만 JSON으로 출력하라.

사용자 질의:
{rewritten_query}
""".strip()
