import asyncio

from mari_agent.graph.llms import ainvoke_llm
from mari_agent.graph.prompts.prompt_manager import build_formatted_prompts


async def evaluate_answer(query, expected_answer, actual_answer):
    input_data = {
        "query": query,
        "expected_answer": expected_answer,
        "actual_answer": actual_answer,
    }
    messages = await build_formatted_prompts(
        company_code=2011,
        node_name="EvaluationTest",
        **input_data,
    )
    response = await ainvoke_llm(
        messages=messages,
    )
    return response


# 테스트 함수 예시
async def test_answer_evaluation():
    query = """
    Q20. 과거 가격 변동 사례를 분석해, 향후 가격 방향성을 예측할 수있는 지표를 제시해줘
    """
    expected_answer = """
시기	사건/요인	ASP 변화(%)	영향 방향	예측 지표
2018 Q2	미·중 무역분쟁	7	상승 압력	무역지수, 공급망 위험지수
2020 Q2	팬데믹 수요 급등	12	상승 압력	서버 CAPEX YoY, 재고일수
2022 Q1	우크라 전쟁	4	상승 압력	원자재 공급지수, 운송비
2023 Q1	공급과잉	-10	하락 압력	가동률, 재고일수
이 지표 조합으로 가격 방향성을 예측 가능이 가능합니다				
① 주요 고객 CAPEX 변화율② 글로벌 DRAM 재고일수③ 주요 원자재·물류비 지수④ 지정학 리스크 지수⑤ DDR5/HBM 신규 채택률				
"""
    actual_answer = """
  
## 2024-12~2025-12 DRAM·NAND 가격 변동 및 향후 방향 예측 지표 분석

2024년 12월부터 2025년 12월까지 DRAM과 NAND 시장은 AI 서버 및 고부가가치 메모리(HBM, DDR5 등) 수요 급증, 공급사 재고 감소, 제품 믹스 변화에 따라 가격이 크게 변동하였습니다. SK하이닉스, 삼성전자, 마이크론 모두 DRAM과 NAND ASP(평균판매단가)와 비트 출하량이 동반 상승하는 구간이 있었으며, 특히 HBM과 DDR5 등 고부가 제품 비중 확대가 ASP 상승을 견인했습니다. DRAM 공급사 재고가 역사적 저점에 근접하면서, 2025년 하반기에는 가격 강세가 더욱 두드러졌습니다. 반면, NAND는 일부 분기에서 출하량 감소에도 불구하고 고부가 SSD 믹스 효과로 ASP가 상승하는 등 제품 믹스가 가격 방향성에 중요한 예측 지표로 작용했습니다. [web_1][web_2][web_3][web_4][web_5][web_12][web_22][web_31][web_34][web_100]

---

## 주요 지표

- **SK하이닉스**
  - 2025년 3분기 DRAM 시장점유율 **33.2%**, 매출 **$13.75B** (QoQ +12.4%)
  - DRAM ASP **중간 한 자릿수(%) QoQ 상승**, 비트 출하량 **고한 자릿수(%) QoQ 증가**
  - HBM, DDR5 등 고부가 제품 비중 확대, 2026년 HBM 공급 계약 대부분 완료, 재고는 2주 미만(역사적 저점)
  - NAND는 비트 출하량 감소(중간 한 자릿수 % QoQ 감소)에도 불구하고, 엔터프라이즈 SSD 믹스 효과로 ASP **10%대 초반 QoQ 상승** [web_1][web_3][web_4][web_22][web_31][web_76]

- **삼성전자**
  - 2025년 3분기 DRAM 매출 **$13.5B** (QoQ +30.4%), 시장점유율 **32.6%**
  - HBM 비트 출하량 **85% QoQ 증가**, DRAM ASP **중간 두 자릿수(%) QoQ 상승**
  - DDR5, LPDDR5 등 고용량 제품 믹스 확대, 재고 급감, DRAM/NAND 모두 고부가 제품 중심 믹스 전략 [web_2][web_9][web_12][web_17][web_21][web_29]

- **마이크론**
  - 2025년 3분기 DRAM 매출 **$10.65B** (QoQ +53.2%), 시장점유율 **25.7%**
  - DRAM ASP **30% QoQ 상승**, 비트 출하량 **저~중 두 자릿수(%) QoQ 증가**
  - HBM3E/4 출하량 급증, 2026년까지 HBM 공급 완판, DRAM 재고 124일(목표치 하회), NAND는 비트 출하량 감소(중간 한 자릿수 % QoQ 감소)에도 ASP **고 한 자릿수(%) QoQ 상승** [web_3][web_12][web_16][web_67][web_100]

- **공통 예측 지표**
  - **ASP(평균판매단가)**: 고부가 제품 믹스 확대, 공급 부족, 재고 감소 시 상승
  - **비트 출하량**: AI 서버, 데이터센터 수요 급증 시 동반 증가
  - **재고**: 2025년 하반기 DRAM/NAND 재고 모두 역사적 저점, 가격 강세 신호
  - **제품 믹스(HBM, DDR5, LPDDR5 등)**: 고부가 제품 비중이 ASP와 수익성에 직접적 영향

## 시계열 데이터

**2024-12~2025-12 DRAM/NAND 시장 주요 지표 및 변동 요약**  
(출처: [web_1][web_2][web_3][web_4][web_5][web_12][web_22][web_31][web_34][web_100])

| date         | 주요 지표 및 변동 요약                                                                 | 원인/영향 요인 및 이벤트 설명                                                                                 |
|--------------|--------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| 2024-12      | DRAM/NAND ASP 동반 상승, 비트 출하량 증가, HBM/DDR5 믹스 확대                          | AI 서버 수요 폭증, 고부가 제품 믹스 효과, 공급사 재고 감소 시작 [web_1][web_2][web_3]                        |
| 2025-01~03   | DRAM ASP +10% 내외, 비트 출하량 +20% 내외, NAND ASP +7~15% 상승, 일부 NAND 출하 감소   | DRAM/NAND 재고 급감, AI/서버용 SSD 수요 견조, HBM3E/DDR5 출하 본격화 [web_8][web_11][web_12][web_14][web_16]|
| 2025-04~06   | DRAM/NAND 재고 역사적 저점, DRAM ASP 추가 상승, NAND ASP 고정/상승, HBM 공급계약 조기 완료 | DRAM/NAND 공급 부족, 2026년까지 HBM/DDR5 등 고부가 제품 공급계약 조기 소진, 가격 강세 지속 [web_22][web_31][web_43]|
| 2025-07~09   | DRAM/NAND ASP 강세 지속, DRAM 비트 출하량 증가세 둔화, NAND 일부 출하 감소              | DRAM/NAND 공급사 재고 2~4주 수준, AI/서버 수요 지속, 일부 모바일/PC 수요 약세 [web_54][web_67][web_76][web_100]|
| 2025-10~12   | DRAM/NAND ASP 고점, DRAM/NAND 재고 최저치, HBM/DDR5 믹스 40% 이상, 2026년 공급계약 대부분 완료 | DRAM/NAND 공급 부족 심화, AI/서버용 고부가 제품 믹스 극대화, 가격 추가 상승 압력 [web_70][web_73][web_76][web_100]|


"""

    result = await evaluate_answer(query, expected_answer, actual_answer)
    print("LLM 평가 결과:\n", result.content)


if __name__ == "__main__":
    asyncio.run(test_answer_evaluation())
