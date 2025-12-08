import asyncio
import logging
from typing import Any, List

from apps.agents.mi_agent.subgraphs.rdb_search.schemas import RDBSearchResult, RDBSearchResults
from apps.agents.mi_agent.subgraphs.rdb_search.state import RDBSearchCandidate, RDBSearchState
from apps.agents.mi_agent.tools.rdb_search_execution import execute_rdb_search_tool


logger = logging.getLogger(__name__)


async def execute_rdb_search_node(state: RDBSearchState) -> RDBSearchState:
    tasks =  [
        asyncio.create_task(_run_one(item, state.company_code)) for item in state.cantidate_items
    ]
    rdb_search_result: RDBSearchResult = None
    rdb_search_results: RDBSearchResults = RDBSearchResults()
    sqls : list[str] = []
    for task in asyncio.as_completed(tasks):
        rdb_search_result = await task
        rdb_search_results.metric_data.append(rdb_search_result.metric_data)
        rdb_search_results.used_tables.append(rdb_search_result.used_table)
        sqls.append(rdb_search_result.sql)
        rdb_search_results.related_data.append(rdb_search_result.related_data)
    
    state.rdb_search_results = RDBSearchResults(
        metric_data=rdb_search_results.metric_data,
        used_tables=list(set(rdb_search_results.used_tables)),
        sqls= "\n".join(sqls),
        related_data= rdb_search_results.related_data,
    )

    return state


async def _run_one(cantidate_item: RDBSearchCandidate, company_code: str) -> RDBSearchResult:
    try:
        rdb_search_output: RDBSearchResult = await execute_rdb_search_tool(
            RDBSearchCandidate(
                query=cantidate_item.query,
                company_code=company_code,
                vdb_search_candidates=cantidate_item.vdb_search_candidates,
            ),
        )
    except Exception as e:
        logger.error(
            f"[RDB 병렬수행] item 처리 실패: {cantidate_item.get('query')} - {e}",
        )
        raise
    else:
        return rdb_search_output
    finally:
        await asyncio.sleep(0.5)
