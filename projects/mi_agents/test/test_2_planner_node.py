import ast
import csv
import logging
import time
from pathlib import Path

import pytest
from langgraph.graph import END, START, StateGraph

from mari_agent.common.types.nodes import PlannerNodeOutput, RewriteQueryNodeOutput
from mari_agent.graph.nodes import (
    PlannerNode,
    RewriteQueryNode,
)
from mari_agent.graph.states import MariGraphState
from test.utils import (
    COMMON_FILE_RESULT_NAME,
    common_headers,
    planner_headers,
    save_test_result_to_csv,
)

# 로거 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@pytest.fixture(scope="session")
def graph():
    builder = StateGraph(MariGraphState)
    rewrite_query_node = RewriteQueryNode()
    planner_node = PlannerNode()
    builder.add_node(rewrite_query_node.name, rewrite_query_node)
    builder.add_node(planner_node.name, planner_node)
    builder.add_edge(START, rewrite_query_node.name)
    builder.add_edge(rewrite_query_node.name, planner_node.name)
    builder.add_edge(planner_node.name, END)
    graph = builder.compile()
    return graph


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query",
    [
        # "브렌트유 가격과 두바이유 가격의 차이는?",
        "헨리허브 가격과 JKM 가격의 차이는?"
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
    assert "planner" in result, "planner should be in result"
    planner: PlannerNodeOutput = result["planner"]
    logger.info("\n- Response time: %s", f"{response_time:.2f}")
    logger.info("\n- objective: %s", planner.objective)
    logger.info(
        "\n- collect_steps: %s", [step.model_dump() for step in planner.collect_steps]
    )
    logger.info(
        "\n- analysis_steps: %s",
        [step.model_dump() for step in planner.analysis_steps],
    )


@pytest.mark.asyncio
async def test_query_from_file():
    """CSV 파일에서 재작성된 쿼리 정보를 읽어 플래너 노드를 테스트합니다."""
    test_data_dir = Path(__file__).parent / "sample_data"
    input_file = test_data_dir / f"{COMMON_FILE_RESULT_NAME}_1_rewritten_query.csv"
    output_file = test_data_dir / f"{COMMON_FILE_RESULT_NAME}_2_planner.csv"

    if not input_file.exists():
        pytest.skip(f"Input file not found: {input_file}")

    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rewrite_infos = list(reader)

    if not rewrite_infos:
        pytest.skip("No test data found in CSV file")

    planner_node = PlannerNode()
    all_headers = common_headers + planner_headers

    for row_idx, rewrite_info in enumerate(rewrite_infos, 1):
        try:
            start_time = time.time()

            query = rewrite_info.get("query", "").strip()
            rewritten_query = rewrite_info.get("rewritten_query", "").strip()
            period_queries = ast.literal_eval(rewrite_info.get("period_queries", "[]"))

            rewrite_output = RewriteQueryNodeOutput(
                rewritten_query=rewritten_query, period_queries=period_queries
            )
            test_state = MariGraphState(
                query=query,
                rewrite_query=rewrite_output,
                thread_id="test-thread-001",
            )

            result_state = await planner_node(test_state)
            end_time = time.time()
            response_time = end_time - start_time
            assert result_state and hasattr(result_state, "planner"), (
                f"Row {row_idx}: planner should be in result state"
            )

            planner: PlannerNodeOutput = result_state.planner

            # 결과 저장을 위한 row 데이터 준비
            save_row = {
                "query": query,
                # 새로운 플래너 결과 추가
                "plann_resp_time": f"{response_time:.2f}",
                "objective": planner.objective,
                # "assumptions": getattr(planner, "assumptions", ""),
                # "comparison_specs": str(planner.comparison_specs),
                "collect_steps": str(
                    [step.model_dump() for step in planner.collect_steps]
                ),
                "analysis_steps": str(
                    [step.model_dump() for step in planner.analysis_steps]
                ),
            }

            save_test_result_to_csv(
                file_path=output_file, headers=all_headers, row=save_row
            )

            logger.info(
                f"Row {row_idx}/{len(rewrite_infos)}: Processed query '{query[:50]}...' in {response_time:.2f}s"
            )

        except Exception as e:
            logger.error(f"Row {row_idx}: Error processing query: {e}")
            # 에러가 발생해도 다음 행 계속 처리
            continue

    logger.info(
        f"Completed processing {len(rewrite_infos)} queries. Results saved to: {output_file}"
    )
