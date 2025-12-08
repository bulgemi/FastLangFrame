from __future__ import annotations

import json
import re
from typing import Any

from apps.agents.mi_agent.prompts.rdb_search_rewrite_queries import (
    build_rdb_search_queries_prompt,
)
from apps.agents.mi_agent.subgraphs.rdb_search.schemas import RDBSearchQuery
from apps.common.exceptions.custom import LLMInvalidResponseError
from apps.common.values.enums import ModelPreference
from apps.connectors.llm.llm_client import invoke_llm_function_call


RDB_SEARCH_QUERY_OUTPUT_EXAMPLE = """
[
    {
    "query": "<정제된 자연어 질의>",
    "search_text": "<검색용 키워드 문자열>"
    }
]
""".strip()


def prepare_rdb_search_queries(
    rewritten_query: str,
) -> list[RDBSearchQuery]:
    prompt: str = build_rdb_search_queries_prompt(
        rewritten_query=rewritten_query,
        output_example=RDB_SEARCH_QUERY_OUTPUT_EXAMPLE,
    )
    return _build_query_items_from_prompt(prompt)


def _build_query_items_from_prompt(prompt: str) -> list[RDBSearchQuery]:
    response: dict[str, Any] = invoke_llm_function_call(
        messages=[{"role": "user", "content": prompt}],
        preference=ModelPreference.QUALITY,
        temperature=0.0,
    )

    context = response.get("content")

    if len(context) < 1:
        raise LLMInvalidResponseError(detail=f"prompt:{prompt}, return context:{context}")

    return _parse_llm_query_items(
        str(context),
    )


def _parse_llm_query_items(raw_text: str) -> list[RDBSearchQuery]:
    cleaned_text: str = _strip_code_fence(raw_text.strip())

    try:
        data: Any = json.loads(cleaned_text)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", cleaned_text, flags=re.DOTALL)
        data = json.loads(match.group(0)) if match else []

    if not isinstance(data, list):
        data = [data]

    rdb_search_queries: list[RDBSearchQuery] = []
    for item in data:
        if not isinstance(item, dict):
            item = {"query": str(item), "search_text": ""}

        q: str = (item.get("query") or "").strip()
        st_raw: str = item.get("search_text") or ""
        st: str = _normalize_search_text_tokens(st_raw)

        # rewrite_query_with_rdb()와 동일: q와 st 둘 다 있어야 포함
        if q and st:
            rdb_search_queries.append(RDBSearchQuery(query=q, search_text=st))

    return rdb_search_queries


def _strip_code_fence(text: str) -> str:
    """``` 또는 ```json 코드 펜스를 제거한다."""
    return re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )


def _normalize_search_text_tokens(
    search_text: str,
    max_tokens: int = 12,
) -> str:
    """search_text를 벡터/풀텍스트 검색에 적합하도록 정제한다.

    - 구두점/괄호 제거 및 공백 정리
    - 날짜 토큰 제거
    - 대소문자 무시 중복 제거
    - 토큰 수를 [min_tokens, max_tokens] 범위 내로 보정 (현재는 최대만 사용)
    """
    # 1) 따옴표/쉼표/괄호 제거 → 공백 단일화
    normalized: str = search_text.replace(",", " ")
    normalized = normalized.replace('"', " ").replace("'", " ")
    normalized = re.sub(r"[(){}\[\]]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    # 2) 토큰화
    tokens: list[str] = normalized.split()

    # 3) 날짜 패턴 제거 (YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD, YYYY년 M월, YYYY년 M월 D일, YYYY-MM, YYYY/MM, YYYY.MM)
    date_patterns: tuple[str, ...] = (
        r"\b\d{4}[-/.]\d{2}[-/.]\d{2}\b",  # 2025-06-05 / 2025/06/05 / 2025.06.05
        r"\b\d{4}[-/.]\d{2}\b",  # 2025-06 / 2025/06 / 2025.06
        r"\b\d{4}년\s*\d{1,2}월(\s*\d{1,2}일)?\b",  # 2025년 6월 / 2025년 6월 5일
    )

    def is_date_token(token: str) -> bool:
        stripped = token.strip()
        return any(re.search(pattern, stripped) for pattern in date_patterns)

    tokens_without_date: list[str] = [t for t in tokens if t and not is_date_token(t)]

    # 4) 중복 제거(대소문자 무시)
    seen: set[str] = set()
    deduplicated_tokens: list[str] = []
    for token in tokens_without_date:
        key = token.lower()
        if key not in seen:
            seen.add(key)
            deduplicated_tokens.append(token)

    # 5) 길이 보정: 너무 길면 앞쪽 핵심 위주로 자르기 / 너무 짧으면 그대로 둠
    if len(deduplicated_tokens) > max_tokens:
        deduplicated_tokens = deduplicated_tokens[:max_tokens]
    # min_tokens는 현재 "권장값" 개념이라 강제 보정은 하지 않음

    # 6) 재조합
    return " ".join(deduplicated_tokens)
