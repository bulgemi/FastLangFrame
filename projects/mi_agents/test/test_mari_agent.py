import json
import logging
import time
from datetime import datetime
from pathlib import Path

import pytest
from langserve import RemoteRunnable

from mari_agent.graph_builder import builder

# 로거 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query",
    [
        # "최근 1개월간 미국 10년물 국채금리와 Henry Hub 가격흐름을 비교해줘.",
        # 최근 1년간 미국 LNG PJT FID 현황",
        # "2025년 한국 LNG 수입량 얼마야?",
        # "어제의 wti 가격을 알려줘",
        "2025년 한국 LNG 수입량 얼마야?"
    ],
)
async def test_mari_graph_ainvoke(query):
    input = {
        "query": "어제의 wti 가격을 알려줘",
        "thread_id": "test-thread-001",
    }
    t0 = time.perf_counter()
    result = await builder.ainvoke(
        input=input, config={"configurable": {"stream": "disable"}}
    )
    t1 = time.perf_counter()
    assert result, "Result should not be empty"
    result = json.dumps(result, indent=2, ensure_ascii=False)
    logger.info(f"Final Answer: {result}")
    logger.info(f"Elapsed_time={t1 - t0:.2f}s")


@pytest.mark.asyncio
async def test_mari_graph_ainvoke_query_from_file():
    """CSV 파일에서 쿼리를 읽어 mari agent를 테스트합니다."""
    import csv

    test_data_dir = Path(__file__).parent / "sample_data"
    now = time.strftime("%Y%m%d_%H%M")
    input_file = test_data_dir / "sk_ens_query_with_asis_answer_list.csv"
    output_file = test_data_dir / f"sk_ens_query_with_asis_answer_list_result_{now}.csv"

    if not input_file.exists():
        pytest.skip(f"Input file not found: {input_file}")

    test_cases = []
    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("query", "").strip():
                test_cases.append(
                    {
                        "query": row["query"].strip(),
                        "as_is_answer": row.get("as_is_answer", "").strip(),
                    }
                )

    if not test_cases:
        pytest.skip("No valid test cases found in input file")

    logger.info(f"Found {len(test_cases)} test cases to process")

    for idx, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        as_is_answer = test_case["as_is_answer"]
        try:
            start_time = time.time()
            logger.info(f"Processing query {idx}/{len(test_cases)}: {query[:50]}...")

            test_input = {"query": query}

            # 그래프 실행
            result = await builder.ainvoke(input=test_input)
            end_time = time.time()
            response_time = end_time - start_time

            # 결과 검증
            assert result and isinstance(result, dict), f"Query {idx}: Empty Result"

            save_row = {
                "query": query,
                "as_is_answer": as_is_answer,
                "response_time": response_time,
            }
            for key in result.keys():
                save_row[key] = result[key]

            all_headers = ["query", "as_is_answer", "response_time"] + list(
                result.keys()
            )
            save_test_result_to_csv(
                file_path=output_file, headers=all_headers, row=save_row
            )
        except Exception as e:
            logger.error(f"Query {idx}: Error processing '{query[:50]}...': {e}")
            continue


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query",
    [
        # "미국 LNG 수출 5월 감소(2025-06-02 보도)가 TTF·JKM 가격에 끼친 영향은?",
        # "최근 3개월 JKM 가격 추세 알려줘",
        # "2025년 한국 LNG 수입량 얼마야?"
        # "최근 3개월간 Brent유와 WTI유 가격 차이의 추세는 어떻게 변화했나요?",
        # "어제의 wti 가격을 알려줘",
        # "최근 1개월간 미국 10년물 국채금리와 Henry Hub 가격흐름을 비교해줘.",
        "최근 1년간 미국 LNG PJT FID 현황",
        # "WTI 1개월물과 Brent 1개월물이 하루에 6 % 이상 동반 급락한 최신 사례는?",
        # "미국 천연가스 working storage와 Net widhdrawals, nymex기준 henryhub의 open interest, 선물 정산가를 대상으로 최근 1년간 연관성을 알려줘"
    ],
)
async def test_mari_graph_remote_ainvoke(query):
    AX_CUSTM_AGENT_SERVING_ID = "c59a83ae-6afc-4aca-95be-14d6ffe5d4a5"
    endpoint = "http://localhost:18080"
    # endpoint = f"https://aip.sktai.io/api/v1/agent_gateway/{AX_CUSTM_AGENT_SERVING_ID}"
    api_key = "sk-d3aab9b636001cf28d9e95a6fbc58e36"

    headers = {
        "aip-user": "mi_test_user",
        "Authorization": f"Bearer {api_key}",
    }

    input = {
        "req_input": {
            "query": "오늘 wti 가격을 알려줘",
            "company_code": "2013",
            "user_num": 1004,
            "authorized_product_nums": [],
            "histories": [],
            "web_search_enabled": True,
        }
    }

    agent = RemoteRunnable(endpoint, headers=headers)
    t0 = time.perf_counter()
    output = await agent.ainvoke(input=input)

    t1 = time.perf_counter()
    elapsed_time = t1 - t0
    print(f"✅ 완료: {output} \n(소요 시간: {elapsed_time:.2f}초)")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query",
    [
        # "공급사별 매출·영업이익 실적을 비교하고 변화 요인을 분석해줘.",
        # "기관사별 판매량·매출·가격 실적을 DDR4·DDR5·LPDDR 등 제품군별로 비교 분석해줘.(OMDIA, Gartner, OOO 별로 비교)",
        # " 경쟁사 가격 변동 후 자사 판매량·점유율 변화를 분석해줘."
        # "24년 DRAM ASP 상승/하락의 핵심 원인을 분석해줘",
        # "가격이 하락/상승 전환한 주요 원인과 예측 가능한 트리거 포인트를 제시해줘.",
        # "D램 시장 수요·공급 변화와 변동 요인, 주요 트렌드를 요약해줘.",
        # "서버·PC·모바일 세그먼트별 D램 수요 성장률과 가격 상승률을 세분화해 정리해줘.",
        # "지정학적 리스크 측면에서 D램 가격에 영향을 미치는 주요 이슈를 정리해줘.",
        # "과거 데이터센터 투자 사이클과 D램 시황 간 상관관계를 분석해줘.",
        # "AI 서버 확산이 D램 제품 믹스(고용량·고속 제품)에 미친 영향을 정리해줘.",
        # "가격 상승/하락기의 삼성전자·마이크론 등의 경쟁사 D램 제품 전략을 비교 분석해줘.",
        # "가격 상승/하락기의 경쟁사들의 점유율 변화와 이에 따른 제품 믹스 전략을 분석해줘.",
        # "중국 메모리 업체들의 기술·생산 능력이 시장에 미친 영향을 분석해줘.",
        # "엔비디아 신제품 출시가 D램 시장에 미치는 영향을 매출/영업이익 등 정성적으로 분석·정리해줘.",
        # "서버·모바일·PC 고객 세그먼트별 매출·마진 데이터를 비교하고, 고수익 세그먼트 집중 전략을 제안해줘.",
        # "Top 10 고객 매출 비중과 변화 추이를 분석하고, 매출 편중 완화 방안을 제안해줘.",
        # "주요 고객사별 DDR5·LPDDR·DDR4 구매 패턴을 분석하고, 제품 믹스 최적화 방안을 제안해줘.",
        # "과거 수요 예측 오차 데이터를 기반으로 세그먼트별 수요 예측 정확도를 높이는 방법을 제안해줘.",
        # "세그먼트별 ASP를 분석하고 차분기·차년도 ASP Trend를 제시해줘.",
        # "과거 가격 변동 사례를 분석해, 향후 가격 방향성을 예측할 수있는 지표를 제시해줘",
        # "",
        # "",
        # "",
        # "우크라이나의 드론 공격으로 러시아 원유 수출 차질 우려관련 된 오늘 뉴스 알려줘",
        # "Brent유 1개월물의 최근 가격 알려줘",
        # "싱가포르 LSFO 크랙"
        # "안녕",
        # "원달러 가장최근날 값을 알려줘",
        # "똑바로 대답안하냐?",
        # "테스트 하기 싫어",
        # "케이팝 데몬 헌터스 ost알려줘",
        # "2025년 상반기 SOX 지수의 월별 변동성 및 급등락 요인은 무엇인가요?",
        # "선물&옵션 기준의 Brent Crude Oil Managed Money Long, Managed Money Short 2개의 데이터에 대해서 2025-10-14기준으로 Long-short(롱-숏 불균형)을 알려줘. 그리고 일주일 이전과의 변화도 알려줘."
        # "2025년 오늘까지 S&P500지수를 알려줘",### 핵심 분석 결과
        # "최근 일본 LNG 재고량?"
        # "直近の日本のLNG在庫量は？",
        # "最近中国的LNG库存量是多少？"
        # "최근 3개월 JKM 가격 추세 알려줘",
        # "2025년 한국 LNG 수입량 얼마야?",
        # "최근 3개월간 Brent유와 WTI유 가격 차이의 추세는 어떻게 변화했나요?",
        "어제의 wti 가격을 알려줘",
        # "3개월전 wti 가격을 알려줘",
        # "오늘 wti 가격을 알려줘",
        # "앞으로 WTI 가격 전망은 어떻게 평가되고 있나요?",
        # "2025년 11월 이후 WTI 가격 전망은 어떻게 평가되고 있나요?",
        # "반도체 지수 기준으로 최근 1년간 업황 분석해줘",
        # "최근 1개월간 미국 10년물 국채금리와 Henry Hub 가격흐름을 비교해줘.",
        # "최근 1년간 미국 LNG PJT FID 현황",
        # "WTI 1개월물과 Brent 1개월물이 하루에 6 % 이상 동반 급락한 최신 사례는?",
        # "미국 천연가스 working storage와 Net widhdrawals, nymex기준 henryhub의 open interest, 선물 정산가를 대상으로 최근 1년간 연관성을 알려줘"
        # "전세계 주요 LNG 수출국과 수입국은 어디야?",
        # "최근 1년간 브렌트유 가격 급등 구간별로 한국 수입 원가에 미친 영향은 어떠했나요?",
        # "최근 12주 미국 상업용 원유 재고(EIA) 증감 패턴을 알려줘."
        # "2025년 11월 이후 WTI 가격 전망은 어떻게 평가되고 있나요?"
        # "2025년 11월 이후 WTI 가격에 가장 큰 영향을 미칠 수 있는 지정학적·정책적 이벤트는 무엇인가요?",
        # "미국의 러시아·이란 제재 강화가 글로벌 원유 공급망에 미치는 정량적 영향은 어느 정도인가요?"
    ],
)
async def test_mari_graph_remote_astream(query):
    AX_CUSTM_AGENT_SERVING_ID = "c59a83ae-6afc-4aca-95be-14d6ffe5d4a5"
    endpoint = "http://localhost:18080"
    # endpoint = f"https://aip.sktai.io/api/v1/agent_gateway/{AX_CUSTM_AGENT_SERVING_ID}"
    api_key = "sk-d3aab9b636001cf28d9e95a6fbc58e36"

    headers = {
        "aip-user": "mi_test_user",
        "Authorization": f"Bearer {api_key}",
    }

    input = {
        "req_input": {
            "query": query,
            "company_code": "2013",  # sk_energy
            # "company_code": "2011", # sk_hynix
            "dept_code": "",
            "user_num": 1004,
            "authorized_product_nums": [100, 200],
            "histories": [
                {"content": "안녕", "type": "human"},
                {"content": "안녕하세요", "type": "ai"},
                {"content": "안녕하세요", "type": "ai"},
                {"content": "안녕하세요", "type": "ai"},
                {"content": "바보", "type": "ai"},
            ],
            "web_search_enabled": True,
        }
    }

    # 출력 파일 설정
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%m%d_%H%M%S")

    agent = RemoteRunnable(endpoint, headers=headers)

    t0 = time.perf_counter()
    if True:
        async for chunk in agent.astream(input=input):
            print(f"Received:\n{chunk}\n")
    else:
        chunk_count = 0
        output_file = output_dir / f"stream_{timestamp}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Query: {query}\n{'=' * 50}\n\n")

            async for chunk in agent.astream(input=input):
                chunk_count += 1

                if chunk_count % 5 == 0:
                    print(f"📝 {chunk_count} chunks...")

                f.write(f"--- Chunk {chunk_count} ---\n")
                if isinstance(chunk, dict):
                    f.write(json.dumps(chunk, indent=2, ensure_ascii=False))
                else:
                    f.write(str(chunk))
                f.write(f"\n{'-' * 20}\n")
                f.flush()

    t1 = time.perf_counter()
    elapsed_time = t1 - t0
    print(f"✅ 완료: (소요 시간: {elapsed_time:.2f}초)")
