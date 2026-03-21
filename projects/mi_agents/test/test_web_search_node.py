import json
import logging
import time

import pytest
from mari_agent.graph.tools.tool_nodes import WebSearchNode

from mari_agent.common.types.nodes import DataSearchToolNodeInput

# 로거 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 웹 서치 csv 헤더 정의
web_search_headers = [
    "web_search_resp_time",
    "data_count",
    "data_preview",
    "result_status",
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_query",
    [
        # {
        #     "objective": "What is the total LNG import volume of South Korea for the year 2025?",
        #     "period": {"start": "2025-01-01", "end": "2025-12-31"},
        #     "query": "South Korea LNG import volume",
        # },
        # {
        #     "objective": "Provide the Brent front-month settle price for 2025-09-29",
        #     "period": {"start": "2025-09-29", "end": "2025-09-29"},
        #     "query": "Brent front-month settle price",
        # },
        # {
        #     "objective": "미국 LNG 프로젝트 FID(최종 투자 결정) 현황 및 비교 분석",
        #     "period": {"start": "2024-10-01", "end": "2025-09-30"},
        #     "query": "US LNG project FID OR 'final investment decision'",
        # },
        {
            "objective": "Analyze the causes of JKM front-month price movements in 2024 using the JKM benchmark and assess metric.",
            "period": {"start": "2024-01-01", "end": "2024-06-30"},
            "query": "JKM price movement cause OR LNG market driver",
        },
    ],
)
async def test_web_search_node(test_query):
    """웹 서치 노드의 기본 기능을 테스트합니다."""
    start_time = time.time()
    period_query = {"period": test_query["period"], "query": test_query["query"]}

    agent = await WebSearchNode().as_agent()

    agent_input = {
        "messages": [
            {
                "role": "user",
                "content": f"""
다음 정보를 사용하여 웹 검색을 수행하고 결과를 분석해주세요:
목적: {test_query["objective"]}
기간별 질의: {period_query}
""",
            }
        ]
    }
    result = await agent.ainvoke(input=agent_input)

    end_time = time.time()
    response_time = end_time - start_time
    logger.info(f"response_time: {response_time:.2f}s")

    assert result, "Result should not be empty"
    content = result["messages"][-1].content
    logger.info(f"Raw result content: {repr(content)}")

    try:
        content = json.loads(content)
        for key, value in content.items():
            logger.info(f"{key}: {json.dumps(value, indent=2, ensure_ascii=False)}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        logger.info(f"Content that failed to parse: {content}")
        # JSON 파싱에 실패해도 테스트를 계속 진행
        assert len(content) > 0, "Content should not be empty even if not JSON"


@pytest.mark.asyncio
async def test_web_search_batch():
    """여러 쿼리를 배치로 처리하여 성능을 테스트합니다."""
    test_queries = [
        "최근 3개월간 브렌트유 가격 동향",
        "2024년 미국 천연가스 생산량 현황",
        "최근 1년간 중국 LNG 수입량 변화",
    ]

    results = []
    total_start_time = time.time()

    for idx, query in enumerate(test_queries, 1):
        try:
            start_time = time.time()

            period_query = {
                "period": {"start": "2024-01-01", "end": "2024-12-31"},
                "query": query,
            }

            web_search_tool_input = DataSearchToolNodeInput(
                objective=f"분석: {query}",
                period_query=period_query,
            )

            # WebSearchNode 인스턴스를 직접 생성하고 입력 데이터를 전달하여 agent 생성
            from mari_agent.graph.tools.tool_nodes import WebSearchNode

            web_search_node = WebSearchNode()
            agent = await web_search_node.as_agent(input_data=web_search_tool_input)

            agent_input = {
                "input": json.dumps(
                    web_search_tool_input.model_dump(), ensure_ascii=False
                )
            }
            result = await agent.ainvoke(input=agent_input)

            end_time = time.time()
            response_time = end_time - start_time

            content = result["messages"][-1].content
            content = json.loads(content)
            for key, value in content.items():
                value = json.dumps(value, indent=2, ensure_ascii=False)
                logger.info(f"{key}: {value}")
                results.append(
                    {
                        "query": query,
                        "key": len(content.get("data", [])),
                        "value": value,
                        "response_time": response_time,
                    }
                )

            logger.info(
                f"Batch {idx}/{len(test_queries)}: '{query[:30]}...' -> {len(content.get('data', []))} results in {response_time:.2f}s"
            )

        except Exception as e:
            logger.error(f"Batch query {idx} failed: {e}")
            results.append(
                {"query": query, "data_count": 0, "response_time": 0, "success": False}
            )

    total_time = time.time() - total_start_time
    successful_queries = sum(1 for r in results if r["success"])

    logger.info(
        f"Batch test completed: {successful_queries}/{len(test_queries)} successful in {total_time:.2f}s"
    )

    # 최소한 50% 이상의 쿼리가 성공해야 함
    assert successful_queries >= len(test_queries) * 0.5, (
        f"Too many failed queries: {successful_queries}/{len(test_queries)}"
    )
