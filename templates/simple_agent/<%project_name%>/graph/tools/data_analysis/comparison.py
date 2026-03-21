import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, ttest_ind

logger = logging.getLogger(__name__)


class ComparisonAnalyzer:
    """
    체계적인 비교 분석기 - comparison_specs 기반 데이터 비교 및 분석
    """

    def __init__(self):
        self.supported_operations = [
            "spread",
            "ratio",
            "correlation",
            "diff",
            "percentage_change",
            "z_score",
            "log_ratio",
            "volatility_ratio",
            "sharpe_ratio",
        ]
        self.alignment_methods = [
            "inner",
            "outer",
            "left",
            "right",
            "forward_fill",
            "backward_fill",
        ]

    async def analyze(
        self, data_bundle: Any, comparison_specs: Dict, step_config: Dict = None
    ) -> Dict:
        """
        종합적인 비교 분석 수행

        Args:
            data_bundle: 원시 데이터 번들
            comparison_specs: 비교 분석 명세
            step_config: 추가 설정 옵션

        Returns:
            비교 분석 결과
        """
        start_time = time.time()

        try:
            # 입력 검증
            validation_result = self._validate_comparison_specs(comparison_specs)
            if not validation_result["is_valid"]:
                return {
                    "error": "invalid_specs",
                    "message": validation_result["message"],
                    "details": validation_result["details"],
                }

            # cohorts별 데이터 추출
            cohort_data = await self._extract_cohort_data(
                data_bundle, comparison_specs["cohorts"]
            )

            if not cohort_data:
                return {
                    "error": "no_data_extracted",
                    "message": "추출된 코호트 데이터가 없습니다.",
                }

            # pairs별 비교 연산 수행
            comparison_results = await self._execute_pairwise_comparisons(
                cohort_data,
                comparison_specs["pairs"],
                comparison_specs.get("alignment", {}),
            )

            # 통계적 유의성 검정
            statistical_tests = await self._perform_statistical_tests(
                cohort_data, comparison_specs["pairs"]
            )

            # 시계열 비교 분석 (시간에 따른 관계 변화)
            temporal_analysis = await self._analyze_temporal_relationships(
                cohort_data,
                comparison_specs["pairs"],
                comparison_specs.get("alignment", {}),
            )

            # 결과 종합
            final_result = {
                "summary": {
                    "cohorts_analyzed": len(cohort_data),
                    "pairs_compared": len(comparison_specs["pairs"]),
                    "operations_performed": sum(
                        len(pair["ops"]) for pair in comparison_specs["pairs"]
                    ),
                    "execution_time_seconds": round(time.time() - start_time, 3),
                    "analysis_period": self._get_analysis_period(cohort_data),
                },
                "cohort_data_summary": self._summarize_cohort_data(cohort_data),
                "comparison_results": comparison_results,
                "statistical_tests": statistical_tests,
                "temporal_analysis": temporal_analysis,
                "recommendations": self._generate_recommendations(
                    comparison_results, statistical_tests
                ),
            }

            logger.info(
                f"비교 분석 완료: {len(cohort_data)}개 코호트, {time.time() - start_time:.3f}초 소요"
            )
            return final_result

        except Exception as e:
            logger.error(f"비교 분석 실패: {e}")
            return {
                "error": "analysis_failed",
                "message": str(e),
                "execution_time_seconds": round(time.time() - start_time, 3),
            }

    def _validate_comparison_specs(self, comparison_specs: Dict) -> Dict:
        """비교 분석 명세 검증"""
        try:
            validation_details = []

            # 필수 키 확인
            required_keys = ["cohorts", "pairs"]
            for key in required_keys:
                if key not in comparison_specs:
                    validation_details.append(f"필수 키 '{key}'가 누락되었습니다.")

            if validation_details:
                return {
                    "is_valid": False,
                    "message": "필수 키가 누락되었습니다.",
                    "details": validation_details,
                }

            # cohorts 검증
            cohorts = comparison_specs["cohorts"]
            if not isinstance(cohorts, list) or len(cohorts) < 2:
                validation_details.append("최소 2개의 코호트가 필요합니다.")

            cohort_ids = set()
            for i, cohort in enumerate(cohorts):
                if not isinstance(cohort, dict):
                    validation_details.append(f"코호트 {i}는 딕셔너리여야 합니다.")
                    continue

                if "id" not in cohort:
                    validation_details.append(f"코호트 {i}에 'id'가 누락되었습니다.")
                else:
                    if cohort["id"] in cohort_ids:
                        validation_details.append(f"중복된 코호트 ID: {cohort['id']}")
                    cohort_ids.add(cohort["id"])

            # pairs 검증
            pairs = comparison_specs["pairs"]
            if not isinstance(pairs, list) or len(pairs) == 0:
                validation_details.append("최소 1개의 페어가 필요합니다.")

            for i, pair in enumerate(pairs):
                if not isinstance(pair, dict):
                    validation_details.append(f"페어 {i}는 딕셔너리여야 합니다.")
                    continue

                required_pair_keys = ["lhs", "rhs", "ops"]
                for key in required_pair_keys:
                    if key not in pair:
                        validation_details.append(
                            f"페어 {i}에 '{key}'가 누락되었습니다."
                        )

                # 코호트 ID 존재 확인
                if "lhs" in pair and pair["lhs"] not in cohort_ids:
                    validation_details.append(
                        f"페어 {i}의 lhs '{pair['lhs']}'에 해당하는 코호트가 없습니다."
                    )

                if "rhs" in pair and pair["rhs"] not in cohort_ids:
                    validation_details.append(
                        f"페어 {i}의 rhs '{pair['rhs']}'에 해당하는 코호트가 없습니다."
                    )

                # 연산 검증
                if "ops" in pair:
                    if not isinstance(pair["ops"], list):
                        validation_details.append(
                            f"페어 {i}의 ops는 리스트여야 합니다."
                        )
                    else:
                        for op in pair["ops"]:
                            if op not in self.supported_operations:
                                validation_details.append(f"지원하지 않는 연산: {op}")

            return {
                "is_valid": len(validation_details) == 0,
                "message": "검증 통과" if len(validation_details) == 0 else "검증 실패",
                "details": validation_details,
            }

        except Exception as e:
            logger.error(f"명세 검증 실패: {e}")
            return {
                "is_valid": False,
                "message": f"검증 중 오류 발생: {e}",
                "details": [],
            }

    async def _extract_cohort_data(
        self, data_bundle: Any, cohorts: List[Dict]
    ) -> Dict[str, pd.DataFrame]:
        """코호트별 데이터 추출"""
        cohort_data = {}

        for cohort in cohorts:
            try:
                cohort_id = cohort["id"]
                filters = cohort.get("filters", {})

                # 데이터 추출
                extracted_data = self._extract_data(data_bundle, filters)

                if extracted_data is not None and len(extracted_data) > 0:
                    # DataFrame으로 변환 및 표준화
                    df = self._standardize_data_format(extracted_data, cohort_id)

                    if df is not None and len(df) > 0:
                        cohort_data[cohort_id] = df
                        logger.debug(
                            f"코호트 '{cohort_id}': {len(df)}개 데이터 포인트 추출"
                        )
                    else:
                        logger.warning(f"코호트 '{cohort_id}': 유효한 데이터 없음")
                else:
                    logger.warning(f"코호트 '{cohort_id}': 데이터 추출 실패")

            except Exception as e:
                logger.error(
                    f"코호트 '{cohort.get('id', 'unknown')}' 데이터 추출 실패: {e}"
                )
                continue

        return cohort_data

    def _extract_data(self, data_bundle: Any, filters: Dict) -> Any:
        """필터 조건에 따라 데이터 추출"""
        try:
            # data_bundle이 딕셔너리인 경우
            if isinstance(data_bundle, dict):
                # 필터 조건 매칭 로직
                if "source" in filters:
                    source = filters["source"]
                    if source in data_bundle:
                        return data_bundle[source]

                # 기본적으로 첫 번째 유효한 데이터 반환
                for key, value in data_bundle.items():
                    if value and isinstance(value, (list, dict)):
                        return value

            # data_bundle에 속성이 있는 경우 (예: web_results, rdb_results 등)
            elif hasattr(data_bundle, "__dict__"):
                # web_results 확인
                if hasattr(data_bundle, "web_results") and data_bundle.web_results:
                    for source, data in data_bundle.web_results.items():
                        if self._matches_filters(source, data, filters):
                            return data

                # rdb_results 확인
                if hasattr(data_bundle, "rdb_results") and data_bundle.rdb_results:
                    for table, data in data_bundle.rdb_results.items():
                        if self._matches_filters(table, data, filters):
                            return data

                # vector_results 확인
                if (
                    hasattr(data_bundle, "vector_results")
                    and data_bundle.vector_results
                ):
                    for index, data in data_bundle.vector_results.items():
                        if self._matches_filters(index, data, filters):
                            return data

            # 리스트인 경우 직접 반환
            elif isinstance(data_bundle, list):
                return data_bundle

            logger.warning(f"필터 조건에 맞는 데이터를 찾을 수 없습니다: {filters}")
            return None

        except Exception as e:
            logger.error(f"데이터 추출 실패: {e}")
            return None

    def _matches_filters(self, source_name: str, data: Any, filters: Dict) -> bool:
        """데이터가 필터 조건과 매치되는지 확인"""
        try:
            # 소스명 기반 매칭
            if "source" in filters:
                if filters["source"].lower() in source_name.lower():
                    return True

            # 키워드 기반 매칭
            if "keywords" in filters:
                keywords = filters["keywords"]
                if isinstance(keywords, str):
                    keywords = [keywords]

                for keyword in keywords:
                    if keyword.lower() in source_name.lower():
                        return True

            # 벤치마크 기반 매칭 (에너지 데이터 특화)
            if "benchmark" in filters:
                benchmark = filters["benchmark"].lower()
                if benchmark in source_name.lower():
                    return True

            # 상품 기반 매칭
            if "commodity" in filters:
                commodity = filters["commodity"].lower()
                if commodity in source_name.lower():
                    return True

            # 기본적으로 False 반환
            return len(filters) == 0  # 필터가 없으면 모든 데이터 매칭

        except Exception as e:
            logger.error(f"필터 매칭 확인 실패: {e}")
            return False

    def _standardize_data_format(
        self, raw_data: Any, cohort_id: str
    ) -> Optional[pd.DataFrame]:
        """데이터를 표준 DataFrame 형식으로 변환"""
        try:
            if isinstance(raw_data, list):
                if not raw_data:
                    return None

                # 첫 번째 항목으로 구조 판단
                first_item = raw_data[0]

                if isinstance(first_item, dict):
                    df = pd.DataFrame(raw_data)
                else:
                    # 단순 값 리스트
                    df = pd.DataFrame(
                        {
                            "date": pd.date_range(
                                start="2024-01-01", periods=len(raw_data)
                            ),
                            "value": raw_data,
                        }
                    )

            elif isinstance(raw_data, dict):
                df = pd.DataFrame(raw_data)

            elif isinstance(raw_data, pd.DataFrame):
                df = raw_data.copy()

            else:
                logger.warning(f"지원하지 않는 데이터 형식: {type(raw_data)}")
                return None

            # 컬럼 표준화
            df = self._standardize_columns(df)

            # 데이터 검증 및 정리
            if "date" in df.columns and "value" in df.columns:
                # 날짜 변환
                df["date"] = pd.to_datetime(df["date"], errors="coerce")

                # 숫자 변환
                df["value"] = pd.to_numeric(df["value"], errors="coerce")

                # NaN 제거
                df = df.dropna(subset=["date", "value"])

                # 날짜순 정렬
                df = df.sort_values("date").reset_index(drop=True)

                # 중복 날짜 제거 (마지막 값 유지)
                df = df.drop_duplicates(subset=["date"], keep="last")

                if len(df) > 0:
                    return df[["date", "value"]].copy()

            logger.warning(
                f"코호트 '{cohort_id}': 유효한 date/value 컬럼을 찾을 수 없습니다."
            )
            return None

        except Exception as e:
            logger.error(f"데이터 형식 표준화 실패 (코호트: {cohort_id}): {e}")
            return None

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """컬럼명을 표준 형식(date, value)으로 변환"""
        df_copy = df.copy()

        # 날짜 컬럼 탐지
        date_keywords = ["date", "time", "timestamp", "일자", "날짜", "dt"]
        date_col = None

        for col in df_copy.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in date_keywords):
                date_col = col
                break

        # 값 컬럼 탐지
        value_keywords = ["value", "price", "amount", "close", "settle", "가격", "값"]
        value_col = None

        for col in df_copy.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in value_keywords):
                value_col = col
                break

        # 숫자 컬럼 중에서 값 컬럼 찾기
        if not value_col:
            numeric_cols = df_copy.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                value_col = numeric_cols[0]

        # 컬럼명 변경
        rename_dict = {}
        if date_col and date_col != "date":
            rename_dict[date_col] = "date"
        if value_col and value_col != "value":
            rename_dict[value_col] = "value"

        if rename_dict:
            df_copy = df_copy.rename(columns=rename_dict)

        # 기본 컬럼 생성 (없는 경우)
        if "date" not in df_copy.columns:
            df_copy["date"] = pd.date_range(start="2024-01-01", periods=len(df_copy))

        if "value" not in df_copy.columns:
            numeric_cols = df_copy.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                df_copy["value"] = df_copy[numeric_cols[0]]

        return df_copy

    async def _execute_pairwise_comparisons(
        self,
        cohort_data: Dict[str, pd.DataFrame],
        pairs: List[Dict],
        alignment_config: Dict,
    ) -> Dict:
        """페어별 비교 연산 수행"""
        comparison_results = {}

        for pair in pairs:
            try:
                lhs_id = pair["lhs"]
                rhs_id = pair["rhs"]
                operations = pair["ops"]

                if lhs_id not in cohort_data or rhs_id not in cohort_data:
                    logger.warning(f"페어 데이터 누락: {lhs_id} 또는 {rhs_id}")
                    continue

                lhs_data = cohort_data[lhs_id]
                rhs_data = cohort_data[rhs_id]

                # 데이터 정렬
                aligned_lhs, aligned_rhs, alignment_info = self._align_data(
                    lhs_data, rhs_data, alignment_config
                )

                if len(aligned_lhs) == 0 or len(aligned_rhs) == 0:
                    logger.warning(f"정렬 후 데이터 없음: {lhs_id} vs {rhs_id}")
                    continue

                # 각 연산 수행
                pair_results = {
                    "alignment_info": alignment_info,
                    "data_points": len(aligned_lhs),
                    "operations": {},
                }

                for op in operations:
                    try:
                        operation_result = self._perform_operation(
                            op, aligned_lhs, aligned_rhs, lhs_id, rhs_id
                        )
                        pair_results["operations"][op] = operation_result

                    except Exception as e:
                        logger.error(f"연산 '{op}' 실패 ({lhs_id} vs {rhs_id}): {e}")
                        pair_results["operations"][op] = {
                            "error": str(e),
                            "status": "failed",
                        }

                comparison_results[f"{lhs_id}_vs_{rhs_id}"] = pair_results

            except Exception as e:
                logger.error(
                    f"페어 비교 실패 ({pair.get('lhs', 'unknown')} vs {pair.get('rhs', 'unknown')}): {e}"
                )
                continue

        return comparison_results

    def _align_data(
        self, lhs_data: pd.DataFrame, rhs_data: pd.DataFrame, alignment_config: Dict
    ) -> Tuple[pd.Series, pd.Series, Dict]:
        """두 데이터셋을 정렬 규칙에 따라 정렬"""
        try:
            # 기본 정렬 방식
            method = alignment_config.get("method", "inner")
            frequency = alignment_config.get("frequency", "daily")
            missing_handling = alignment_config.get("missing", "forward_fill")

            # 데이터 병합
            merged = pd.merge(
                lhs_data.set_index("date")[["value"]].rename(columns={"value": "lhs"}),
                rhs_data.set_index("date")[["value"]].rename(columns={"value": "rhs"}),
                left_index=True,
                right_index=True,
                how=method,
            )

            # 결측값 처리
            if missing_handling == "forward_fill":
                merged = merged.fillna(method="ffill")
            elif missing_handling == "backward_fill":
                merged = merged.fillna(method="bfill")
            elif missing_handling == "interpolate":
                merged = merged.interpolate()
            elif missing_handling == "drop":
                merged = merged.dropna()

            # 최종 NaN 제거
            merged = merged.dropna()

            # 정렬 정보
            alignment_info = {
                "method": method,
                "frequency": frequency,
                "missing_handling": missing_handling,
                "original_lhs_count": len(lhs_data),
                "original_rhs_count": len(rhs_data),
                "aligned_count": len(merged),
                "alignment_period": {
                    "start": merged.index.min().strftime("%Y-%m-%d")
                    if len(merged) > 0
                    else None,
                    "end": merged.index.max().strftime("%Y-%m-%d")
                    if len(merged) > 0
                    else None,
                },
            }

            return merged["lhs"], merged["rhs"], alignment_info

        except Exception as e:
            logger.error(f"데이터 정렬 실패: {e}")
            return pd.Series(), pd.Series(), {"error": str(e)}

    def _perform_operation(
        self,
        operation: str,
        lhs_values: pd.Series,
        rhs_values: pd.Series,
        lhs_id: str,
        rhs_id: str,
    ) -> Dict:
        """개별 연산 수행"""
        try:
            result_data = {}

            if operation == "spread":
                # 스프레드 (차이)
                spread_values = lhs_values - rhs_values
                result_data = {
                    "values": spread_values.tolist(),
                    "dates": spread_values.index.strftime("%Y-%m-%d").tolist(),
                    "statistics": {
                        "mean": float(spread_values.mean()),
                        "std": float(spread_values.std()),
                        "min": float(spread_values.min()),
                        "max": float(spread_values.max()),
                        "current": float(spread_values.iloc[-1])
                        if len(spread_values) > 0
                        else None,
                    },
                    "interpretation": f"{lhs_id}가 {rhs_id}보다 평균 {spread_values.mean():.4f} 높음",
                }

            elif operation == "ratio":
                # 비율
                ratio_values = lhs_values / rhs_values.replace(0, np.nan)
                ratio_values = ratio_values.dropna()

                result_data = {
                    "values": ratio_values.tolist(),
                    "dates": ratio_values.index.strftime("%Y-%m-%d").tolist(),
                    "statistics": {
                        "mean": float(ratio_values.mean()),
                        "std": float(ratio_values.std()),
                        "min": float(ratio_values.min()),
                        "max": float(ratio_values.max()),
                        "current": float(ratio_values.iloc[-1])
                        if len(ratio_values) > 0
                        else None,
                    },
                    "interpretation": f"{lhs_id}는 {rhs_id}의 평균 {ratio_values.mean():.4f}배",
                }

            elif operation == "correlation":
                # 상관관계
                corr_coef, p_value = pearsonr(lhs_values, rhs_values)

                result_data = {
                    "correlation_coefficient": float(corr_coef),
                    "p_value": float(p_value),
                    "significance": p_value < 0.05,
                    "strength": self._assess_correlation_strength(corr_coef),
                    "interpretation": f"{lhs_id}와 {rhs_id}의 상관계수: {corr_coef:.4f}",
                }

            elif operation == "percentage_change":
                # 퍼센트 변화
                pct_change_lhs = lhs_values.pct_change().dropna()
                pct_change_rhs = rhs_values.pct_change().dropna()
                pct_diff = pct_change_lhs - pct_change_rhs

                result_data = {
                    "lhs_pct_change": pct_change_lhs.tolist(),
                    "rhs_pct_change": pct_change_rhs.tolist(),
                    "pct_change_difference": pct_diff.tolist(),
                    "dates": pct_diff.index.strftime("%Y-%m-%d").tolist(),
                    "statistics": {
                        "mean_diff": float(pct_diff.mean()),
                        "std_diff": float(pct_diff.std()),
                    },
                }

            elif operation == "z_score":
                # Z-점수 비교
                z_lhs = (lhs_values - lhs_values.mean()) / lhs_values.std()
                z_rhs = (rhs_values - rhs_values.mean()) / rhs_values.std()
                z_diff = z_lhs - z_rhs

                result_data = {
                    "z_score_lhs": z_lhs.tolist(),
                    "z_score_rhs": z_rhs.tolist(),
                    "z_score_difference": z_diff.tolist(),
                    "dates": z_diff.index.strftime("%Y-%m-%d").tolist(),
                    "interpretation": f"표준화된 차이의 평균: {z_diff.mean():.4f}",
                }

            elif operation == "volatility_ratio":
                # 변동성 비율
                vol_lhs = lhs_values.rolling(window=30).std().dropna()
                vol_rhs = rhs_values.rolling(window=30).std().dropna()
                vol_ratio = (vol_lhs / vol_rhs.replace(0, np.nan)).dropna()

                result_data = {
                    "volatility_ratio": vol_ratio.tolist(),
                    "dates": vol_ratio.index.strftime("%Y-%m-%d").tolist(),
                    "statistics": {
                        "mean": float(vol_ratio.mean()),
                        "current": float(vol_ratio.iloc[-1])
                        if len(vol_ratio) > 0
                        else None,
                    },
                    "interpretation": f"{lhs_id}의 변동성이 {rhs_id}의 평균 {vol_ratio.mean():.4f}배",
                }

            else:
                result_data = {
                    "error": f"지원하지 않는 연산: {operation}",
                    "supported_operations": self.supported_operations,
                }

            result_data["operation"] = operation
            result_data["status"] = (
                "success" if "error" not in result_data else "failed"
            )

            return result_data

        except Exception as e:
            logger.error(f"연산 '{operation}' 수행 실패: {e}")
            return {"operation": operation, "status": "failed", "error": str(e)}

    async def _perform_statistical_tests(
        self, cohort_data: Dict[str, pd.DataFrame], pairs: List[Dict]
    ) -> Dict:
        """통계적 유의성 검정"""
        test_results = {}

        for pair in pairs:
            try:
                lhs_id = pair["lhs"]
                rhs_id = pair["rhs"]

                if lhs_id not in cohort_data or rhs_id not in cohort_data:
                    continue

                lhs_values = cohort_data[lhs_id]["value"]
                rhs_values = cohort_data[rhs_id]["value"]

                # t-검정 (평균 차이)
                t_stat, t_p_value = ttest_ind(lhs_values, rhs_values)

                # 기술통계
                descriptive_stats = {
                    "lhs_mean": float(lhs_values.mean()),
                    "rhs_mean": float(rhs_values.mean()),
                    "lhs_std": float(lhs_values.std()),
                    "rhs_std": float(rhs_values.std()),
                    "mean_difference": float(lhs_values.mean() - rhs_values.mean()),
                }

                test_results[f"{lhs_id}_vs_{rhs_id}"] = {
                    "t_test": {
                        "t_statistic": float(t_stat),
                        "p_value": float(t_p_value),
                        "significant": t_p_value < 0.05,
                        "interpretation": "평균에 유의한 차이 있음"
                        if t_p_value < 0.05
                        else "평균에 유의한 차이 없음",
                    },
                    "descriptive_statistics": descriptive_stats,
                }

            except Exception as e:
                logger.error(
                    f"통계 검정 실패 ({pair.get('lhs', 'unknown')} vs {pair.get('rhs', 'unknown')}): {e}"
                )
                continue

        return test_results

    async def _analyze_temporal_relationships(
        self,
        cohort_data: Dict[str, pd.DataFrame],
        pairs: List[Dict],
        alignment_config: Dict,
    ) -> Dict:
        """시계열 관계 분석 (시간에 따른 관계 변화)"""
        temporal_results = {}

        for pair in pairs:
            try:
                lhs_id = pair["lhs"]
                rhs_id = pair["rhs"]

                if lhs_id not in cohort_data or rhs_id not in cohort_data:
                    continue

                lhs_data = cohort_data[lhs_id]
                rhs_data = cohort_data[rhs_id]

                # 데이터 정렬
                aligned_lhs, aligned_rhs, _ = self._align_data(
                    lhs_data, rhs_data, alignment_config
                )

                if len(aligned_lhs) < 30:  # 최소 30일 데이터 필요
                    continue

                # 이동 상관관계
                window = min(30, len(aligned_lhs) // 3)
                rolling_corr = aligned_lhs.rolling(window).corr(aligned_rhs).dropna()

                # 이동 스프레드
                rolling_spread = (
                    (aligned_lhs - aligned_rhs).rolling(window).mean().dropna()
                )

                temporal_results[f"{lhs_id}_vs_{rhs_id}"] = {
                    "rolling_correlation": {
                        "window": window,
                        "values": rolling_corr.tolist(),
                        "dates": rolling_corr.index.strftime("%Y-%m-%d").tolist(),
                        "current": float(rolling_corr.iloc[-1])
                        if len(rolling_corr) > 0
                        else None,
                        "trend": "increasing"
                        if rolling_corr.iloc[-1] > rolling_corr.mean()
                        else "decreasing",
                    },
                    "rolling_spread": {
                        "window": window,
                        "values": rolling_spread.tolist(),
                        "dates": rolling_spread.index.strftime("%Y-%m-%d").tolist(),
                        "current": float(rolling_spread.iloc[-1])
                        if len(rolling_spread) > 0
                        else None,
                        "volatility": float(rolling_spread.std()),
                    },
                }

            except Exception as e:
                logger.error(
                    f"시계열 관계 분석 실패 ({pair.get('lhs', 'unknown')} vs {pair.get('rhs', 'unknown')}): {e}"
                )
                continue

        return temporal_results

    # 유틸리티 메서드들
    def _summarize_cohort_data(self, cohort_data: Dict[str, pd.DataFrame]) -> Dict:
        """코호트 데이터 요약"""
        summary = {}

        for cohort_id, df in cohort_data.items():
            summary[cohort_id] = {
                "data_points": len(df),
                "date_range": {
                    "start": df["date"].min().strftime("%Y-%m-%d"),
                    "end": df["date"].max().strftime("%Y-%m-%d"),
                },
                "value_statistics": {
                    "mean": float(df["value"].mean()),
                    "std": float(df["value"].std()),
                    "min": float(df["value"].min()),
                    "max": float(df["value"].max()),
                    "current": float(df["value"].iloc[-1]),
                },
            }

        return summary

    def _get_analysis_period(self, cohort_data: Dict[str, pd.DataFrame]) -> Dict:
        """전체 분석 기간 정보"""
        try:
            all_dates = []
            for df in cohort_data.values():
                all_dates.extend(df["date"].tolist())

            if all_dates:
                return {
                    "start": min(all_dates).strftime("%Y-%m-%d"),
                    "end": max(all_dates).strftime("%Y-%m-%d"),
                    "total_days": (max(all_dates) - min(all_dates)).days + 1,
                }

            return {}
        except:
            return {}

    def _assess_correlation_strength(self, correlation: float) -> str:
        """상관관계 강도 평가"""
        abs_corr = abs(correlation)

        if abs_corr > 0.8:
            return "매우 강함"
        elif abs_corr > 0.6:
            return "강함"
        elif abs_corr > 0.4:
            return "중간"
        elif abs_corr > 0.2:
            return "약함"
        else:
            return "매우 약함"

    def _generate_recommendations(
        self, comparison_results: Dict, statistical_tests: Dict
    ) -> List[str]:
        """분석 결과 기반 권장사항 생성"""
        recommendations = []

        try:
            for pair_key, results in comparison_results.items():
                operations = results.get("operations", {})

                # 스프레드 분석 권장사항
                if "spread" in operations:
                    spread_stats = operations["spread"].get("statistics", {})
                    current_spread = spread_stats.get("current")
                    mean_spread = spread_stats.get("mean")

                    if current_spread is not None and mean_spread is not None:
                        if abs(current_spread - mean_spread) > 2 * spread_stats.get(
                            "std", 0
                        ):
                            recommendations.append(
                                f"{pair_key}: 현재 스프레드가 평균에서 크게 벗어남 (현재: {current_spread:.4f}, 평균: {mean_spread:.4f})"
                            )

                # 상관관계 권장사항
                if "correlation" in operations:
                    corr_data = operations["correlation"]
                    if corr_data.get("significance", False):
                        strength = corr_data.get("strength", "")
                        recommendations.append(
                            f"{pair_key}: {strength} 상관관계 확인됨 (r={corr_data.get('correlation_coefficient', 0):.4f})"
                        )

            if not recommendations:
                recommendations.append("특별한 권장사항이 발견되지 않았습니다.")

        except Exception as e:
            logger.error(f"권장사항 생성 실패: {e}")
            recommendations.append("권장사항 생성 중 오류가 발생했습니다.")

        return recommendations


# 사용 예시
async def example_usage():
    """사용 예시"""

    # 샘플 데이터
    sample_data_bundle = {
        "web_results": {
            "wti_prices": [
                {"date": "2024-01-01", "value": 75.0},
                {"date": "2024-01-02", "value": 76.5},
                {"date": "2024-01-03", "value": 74.2},
            ],
            "brent_prices": [
                {"date": "2024-01-01", "value": 79.0},
                {"date": "2024-01-02", "value": 80.1},
                {"date": "2024-01-03", "value": 78.5},
            ],
        }
    }

    # 비교 분석 명세
    comparison_specs = {
        "cohorts": [
            {"id": "WTI", "desc": "WTI 원유 가격", "filters": {"source": "wti_prices"}},
            {
                "id": "Brent",
                "desc": "Brent 원유 가격",
                "filters": {"source": "brent_prices"},
            },
        ],
        "pairs": [
            {"lhs": "Brent", "rhs": "WTI", "ops": ["spread", "ratio", "correlation"]}
        ],
        "alignment": {
            "method": "inner",
            "frequency": "daily",
            "missing": "forward_fill",
        },
    }

    # 분석 실행
    analyzer = ComparisonAnalyzer()
    results = await analyzer.analyze(sample_data_bundle, comparison_specs)

    print("비교 분석 결과:", results)


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
