import json
import logging
import time
from pathlib import Path

import pytest
from langgraph.graph import END, START, StateGraph

from mari_agent.graph.nodes import (
    RewriteQueryNode,
)
from mari_agent.graph.states import MariGraphState
from test.utils import (
    COMMON_FILE_RESULT_NAME,
    common_headers,
    rewrite_headers,
    save_test_result_to_csv,
)

# 로거 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@pytest.fixture(scope="session")
def graph():
    builder = StateGraph(MariGraphState)
    rewrite_query_node = RewriteQueryNode()
    builder.add_node(rewrite_query_node.name, rewrite_query_node)
    builder.add_edge(START, rewrite_query_node.name)
    builder.add_edge(rewrite_query_node.name, END)
    graph = builder.compile()
    return graph


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query",
    [
        "브렌트유 가격과 두바이유 가격의 차이는?",
        # "헨리허브 가격과 JKM 가격의 차이는?"
    ],
)
async def test_base_query(graph, query):
    start_time = time.time()
    input = {
        "query": query.strip(),
        "histories": [
            {"role": "user", "content": "미국 10년물 국채금리 흐름 알려줘."},
            {
                "role": "assistant",
                "content": "미국 10년물 국채금리는 현재 4.5%입니다.",
            },
        ],
        "thread_id": "test-thread-001",
    }
    result = await graph.ainvoke(input=input)
    end_time = time.time()
    response_time = end_time - start_time

    assert result and isinstance(result, dict), "Result should not be empty"
    assert "rewrite_query" in result, "rewrite_query should be in result"
    rewrite_query = result["rewrite_query"]

    logger.info("- Rewritten query: %s", rewrite_query.rewritten_query)
    logger.info(
        "- Period queries: %s",
        json.dumps(
            [pq.model_dump() for pq in rewrite_query.period_queries],
            indent=2,
            ensure_ascii=False,
        ),
    )
    logger.info("- Response time: %s", f"{response_time:.2f}")


@pytest.mark.asyncio
async def test_query_from_file(graph):
    """CSV 파일에서 쿼리를 읽어 리라이트 노드를 테스트합니다."""
    test_data_dir = Path(__file__).parent / "sample_data"
    input_file = test_data_dir / f"{COMMON_FILE_RESULT_NAME}.csv"
    output_file = test_data_dir / f"{COMMON_FILE_RESULT_NAME}_1_rewritten_query.csv"

    if not input_file.exists():
        pytest.skip(f"Input file not found: {input_file}")

    with open(input_file, "r", encoding="utf-8") as f:
        queries = [line.strip() for line in f.readlines() if line.strip()]

    if not queries:
        pytest.skip("No queries found in input file")

    base_input = {
        "histories": [
            {"role": "user", "content": "미국 10년물 국채금리 흐름 알려줘."},
            {"role": "assistant", "content": "미국 10년물 국채금리는 현재 4.5%입니다."},
            {"role": "user", "content": "최근 1년간 추이도 알려줘."},
        ],
        "thread_id": "test-thread-001",
    }

    all_headers = common_headers + rewrite_headers

    for idx, query in enumerate(queries, 1):
        try:
            start_time = time.time()

            # 입력 데이터 구성
            test_input = {
                **base_input,
                "query": query,
            }

            # 그래프 실행
            result = await graph.ainvoke(input=test_input)
            end_time = time.time()
            response_time = end_time - start_time

            # 결과 검증
            assert result and isinstance(result, dict), (
                f"Query {idx}: Result should not be empty"
            )
            assert "rewrite_query" in result, (
                f"Query {idx}: rewrite_query should be in result"
            )

            rewrite_query = result["rewrite_query"]

            save_row = {
                "query": query,
                "rewrite_resp_time": f"{response_time:.2f}",
                "rewritten_query": rewrite_query.rewritten_query,
                "period_queries": str(
                    [pq.model_dump() for pq in rewrite_query.period_queries]
                ),
            }

            save_test_result_to_csv(
                file_path=output_file, headers=all_headers, row=save_row
            )

            logger.info(
                f"Query {idx}/{len(queries)}: '{query[:50]}...' processed in {response_time:.2f}s"
            )

        except Exception as e:
            logger.error(f"Query {idx}: Error processing '{query[:50]}...': {e}")
            continue

    logger.info(
        f"Completed processing {len(queries)} queries. Results saved to: {output_file}"
    )
