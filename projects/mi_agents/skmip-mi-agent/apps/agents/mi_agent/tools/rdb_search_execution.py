from __future__ import annotations

from collections.abc import Iterable
import contextlib
import json
import re
from typing import Any

from apps.agents.mi_agent.prompts.rdb_search_nl_to_sql import build_nl_to_sql_prompt
from apps.agents.mi_agent.prompts.rdb_search_select_target_table import build_select_table_prompt
from apps.agents.mi_agent.subgraphs.rdb_search.schemas import RDBSearchCandidate, RDBSearchResult, VDBSearchCandidate
from apps.common.exceptions.custom import RdbDataFetchError
from apps.common.logging.logger_config import logger
from apps.connectors.llm.llm_client import invoke_llm_function_call
from apps.connectors.mcp.mcp_adapter import mcp_call_tool, mcp_read_resource


async def execute_rdb_search_tool(rdb_search_candidate: RDBSearchCandidate) -> RDBSearchResult:
    company_code: str = rdb_search_candidate.company_code
    query: str = rdb_search_candidate.query
    target_data_info: Any = await _select_target_data(rdb_search_candidate)
    codes, db_table_info = await _read_metadata_codes(target_data_info["agtmtm_id"], company_code)
    table_schemas: list[str] = await _read_metadata_table_schema(db_table_info, company_code)
    sql = await _generate_sql(query=query, schemas=table_schemas, table_info=db_table_info, codes=codes)
    sql_execution_result: list[dict] = await _execute_sql(sql, company_code)
    rdb_search_output: RDBSearchResult = _convert_sql_result_to_output(
        query=query,
        table_name=db_table_info["table_name"],
        data_description=target_data_info["data_description"],
        codes=codes,
        sql=sql,
        sql_result=sql_execution_result,
    )
    return rdb_search_output


def _convert_sql_result_to_output(
    query: str,
    table_name: str,
    data_description: str,
    codes: list[dict],
    sql: str,
    sql_result: list[dict],
) -> RDBSearchResult:
    related_data: int = 0

    if sql_result:
        used_table = f"{table_name}: {data_description}"
        related_data = _find_related_data_source_nums(
            sql=sql,
            codes=codes,
        )
    else:
        logger.info(
            "SQL 실행 결과가 없습니다. used_tables, related_data를 초기화합니다.",
        )

    # nl2sql_result = json.dumps(
    #     {"query_target": query, "result": sql_result},
    #     ensure_ascii=False,
    # )
    nl2sql_result = {"query_target": query, "result": sql_result}
    rdb_search_output: RDBSearchResult = RDBSearchResult(
        used_table=used_table,
        metric_data=nl2sql_result,
        related_data=str(related_data),
        sql=sql,
    )
    return rdb_search_output


async def _execute_sql(sql: str, company_code: str) -> list[dict]:
    result = await mcp_call_tool(
        name="mysql_query",
        args={"query": sql},
    )

    return _collect_rows_from_mcp_result(result)


def _collect_rows_from_mcp_result(result: Any) -> list[dict]:
    rows: list[dict] = []

    contents = getattr(result, "content", []) or getattr(result, "contents", [])
    for content in contents:
        text = getattr(content, "text", None)
        if not text:
            continue
        parsed = json.loads(text)

        if isinstance(parsed, list):
            rows.extend(parsed)
        elif isinstance(parsed, dict):
            rows.append(parsed)
        else:
            msg = "Unexpected parsed type from MCP: %s"
            raise RdbDataFetchError(msg, type(parsed))

    return rows


async def _generate_sql(query: str, schemas: list[str], table_info: Any, codes: list[dict]) -> str:
    nl_to_sql_prompt: Any = build_nl_to_sql_prompt(
        query=query,
        schema_json=json.dumps(schemas, ensure_ascii=False),
        data_json=json.dumps(table_info, ensure_ascii=False),
        codes_json=json.dumps(codes, ensure_ascii=False),
    )
    sql = _extract_sql_from_response(nl_to_sql_prompt)
    sql = _maybe_fix_mojibake(sql)
    logger.info("\n[SQL 코드]\n%s", sql)
    return sql


def _find_related_data_source_nums(sql: str, codes) -> int:
    code_in_where = re.compile(r"WHERE\s+code\s*=\s*(['\"])(.*?)\1", re.IGNORECASE)
    m = code_in_where.search(sql)
    if not m:
        msg = "WHERE code = '...'\n패턴을 찾지 못했습니다."
        raise ValueError(msg)
    code_value = m.group(2).strip()
    code_key_full = f"code='{code_value}'"

    items = _normalize_codes(codes)
    related: int = 0

    for code_info in items:
        code_field = code_info.get("code")
        if code_field in (code_key_full, code_value):
            related = code_info.get("data_source_num")

    return related


def _normalize_codes(codes) -> list[dict]:
    """다양한 입력 형태(codes)를 표준 dict 리스트로 정규화."""
    # case 1) 리스트이며 첫 원소가 JSON 배열 문자열
    if isinstance(codes, list) and codes and isinstance(codes[0], str) and codes[0].lstrip().startswith("["):
        return json.loads(codes[0])

    # case 2) codes 전체가 JSON 배열 문자열
    if isinstance(codes, str) and codes.lstrip().startswith("["):
        return json.loads(codes)

    # case 3) 이미 dict 리스트
    if isinstance(codes, Iterable) and codes and isinstance(next(iter(codes)), dict):
        return list(codes)

    # case 4) 리스트이며 각 원소가 JSON 객체 문자열
    if isinstance(codes, list) and all(isinstance(x, str) and x.strip().startswith("{") for x in codes):
        out = []
        for x in codes:
            with contextlib.suppress(Exception):
                out.append(json.loads(x))
        return out

    return []


def _maybe_fix_mojibake(text: str) -> str:
    if "ì" in text or "ê" in text:
        try:
            return text.encode("latin1").decode("utf-8")
        except UnicodeError:
            return text
    return text


async def _select_target_data(rdb_search_candidate: RDBSearchCandidate) -> Any:
    table_selection_prompt: str = build_select_table_prompt(
        query=rdb_search_candidate.query,
        table=_build_vdb_candidates_markdown_table(rdb_search_candidate.vdb_search_candidates),
    )
    target_table_info: Any = _extract_target_table_info(table_selection_prompt)
    return target_table_info


async def _read_metadata_table_schema(db_table_info: dict[str, str], company_code: str) -> list[str]:
    schemas: list[str] = []
    schema_res = await mcp_read_resource(
        uri=f"mimcp://database/schemas/{db_table_info['database_name']}/tables/{db_table_info['table_name']}/all"
    )
    schema_content = schema_res.contents[0] if hasattr(schema_res, "contents") else None
    if schema_content and hasattr(schema_content, "text"):
        schemas.append(schema_content.text)
    return schemas


async def _read_metadata_codes(
    agtmtm_id: str,
    company_code: str,
) -> tuple[
    list[dict],
    dict[str, str],
]:  # TODO: db조회 시, alias로 컬럼명 노출되지 않게 수정, db정보 조회 분리할까(distinct)..
    codes: list[dict] = []
    db_info: dict[str, str] | None = None
    codes_res = await mcp_read_resource(
        uri=f"mimcp://database/metas/codes/{agtmtm_id}",
    )
    codes_content = codes_res.contents[0] if hasattr(codes_res, "contents") else None

    parsed = json.loads(codes_content.text)

    first = parsed[0]
    db_name = first.get("database_name")
    table_name = first.get("table_name")
    if db_name or table_name:
        db_info = {
            "database_name": db_name,
            "table_name": table_name,
        }

    codes = [
        {
            "code": item.get("code"),
            "code_expn": item.get("code_expn"),
            "data_source_num": item.get("data_source_num"),
        }
        for item in parsed
    ]

    return codes, db_info


async def _read_metadata_db_table_info(db_table_info: dict[str, str], company_code: str) -> list[str]:
    schemas: list[str] = []
    schema_res = await mcp_read_resource(
        uri=f"mimcp://database/schemas/{db_table_info['database_name']}/tables/{db_table_info['table_name']}/all",
        company_code=company_code,
    )
    schema_content = schema_res.contents[0] if hasattr(schema_res, "contents") else None
    if schema_content and hasattr(schema_content, "text"):
        schemas.append(schema_content.text)
    return schemas


def _build_vdb_candidates_markdown_table(
    candidates: list[VDBSearchCandidate],
) -> str:
    if not candidates:
        return ""

    header = "| agtmtm_id | tbl_expn |"
    separator = "|----------:|:---------|"

    rows: list[str] = []
    for c in candidates:
        rows.append(f"| {c.agtmtm_id} | {c.tbl_expn} |")

    lines = [header, separator, *rows]
    return "\n".join(lines)





def _extract_sql_from_response(prompt: str) -> str:
    result = invoke_llm_function_call(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )

    response = result["content"]

    if "sql" in response:
        sql = re.search(r"```sql\n(.*?)```", response, re.DOTALL)
        return sql.group(1).strip() if sql else ""
    match = re.search(r"(SELECT|WITH)[\s\S]+?;", response)
    return match.group(0).strip() if match else ""


def _extract_target_table_info(prompt: str) -> Any:
    result = invoke_llm_function_call(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )

    llm_response: str = result["content"].strip()

    code_fence_re = re.compile(r"```(?:json|JSON|jsonc)?\s*\r?\n([\s\S]*?)```")
    m = code_fence_re.search(llm_response)
    raw = (m.group(1).strip() if m else llm_response)

    raw = re.sub(r",(\s*[}\]])", r"\1", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RdbDataFetchError("JSON 파싱 실패: %s | head=%r", str(e), raw[:240]) from e
