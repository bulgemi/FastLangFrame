import logging
import time
from typing import Any, Dict

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

from .utils import DataPreprocessor, StatisticalValidator

logger = logging.getLogger(__name__)


class CorrelationAnalyzer:
    """
    하이브리드 상관관계 분석기 - 정확한 통계 계산 + 비즈니스 해석
    """

    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.validator = StatisticalValidator()

    async def analyze(
        self, data_dict: Dict[str, Any], comparison_specs: Dict = None
    ) -> Dict:
        """
        종합적인 상관관계 분석 수행
        """
        start_time = time.time()

        try:
            # 1. 데이터 전처리
            processed_data = await self._preprocess_data(data_dict)

            if len(processed_data) < 2:
                return {
                    "error": "insufficient_data",
                    "message": "상관관계 분석을 위해서는 최소 2개의 데이터셋이 필요합니다.",
                }

            # 2. 기본 상관관계 매트릭스
            correlation_matrix = self._calculate_correlation_matrix(processed_data)

            # 3. 쌍별 상세 분석
            pair_analyses = await self._analyze_pairs(processed_data, comparison_specs)

            # 4. 시계열 상관관계 (데이터가 충분한 경우)
            rolling_correlations = await self._calculate_rolling_correlations(
                processed_data
            )

            # 5. 선행-후행 관계 분석
            lead_lag_analysis = await self._analyze_lead_lag_relationships(
                processed_data
            )

            # 6. 결과 종합
            analysis_result = {
                "summary": {
                    "data_series_count": len(processed_data),
                    "analysis_period": self._get_analysis_period(processed_data),
                    "total_data_points": sum(len(df) for df in processed_data.values()),
                    "execution_time_seconds": round(time.time() - start_time, 3),
                },
                "correlation_matrix": correlation_matrix,
                "pair_analyses": pair_analyses,
                "rolling_correlations": rolling_correlations,
                "lead_lag_analysis": lead_lag_analysis,
                "statistical_significance": self._assess_significance(
                    correlation_matrix, processed_data
                ),
            }

            logger.info(
                f"상관관계 분석 완료: {len(processed_data)}개 시리즈, {time.time() - start_time:.3f}초 소요"
            )
            return analysis_result

        except Exception as e:
            logger.error(f"상관관계 분석 실패: {e}")
            return {"error": "analysis_failed", "message": str(e)}

    async def _preprocess_data(
        self, data_dict: Dict[str, Any]
    ) -> Dict[str, pd.DataFrame]:
        """데이터 전처리 및 정규화"""
        processed = {}

        for name, raw_data in data_dict.items():
            try:
                # 원시 데이터를 DataFrame으로 변환
                df = self.preprocessor.convert_to_dataframe(raw_data)

                if df is not None and len(df) >= 3:  # 최소 3개 데이터 포인트
                    # 날짜 및 값 컬럼 표준화
                    df = self.preprocessor.standardize_columns(df)

                    # 결측값 처리
                    df = self.preprocessor.handle_missing_values(df)

                    # 데이터 유효성 검증
                    if self.validator.is_valid_timeseries(df):
                        processed[name] = df
                        logger.debug(f"{name}: {len(df)}개 데이터 포인트 처리 완료")

            except Exception as e:
                logger.warning(f"{name} 데이터 전처리 실패: {e}")
                continue

        return processed

    def _calculate_correlation_matrix(self, data_dict: Dict[str, pd.DataFrame]) -> Dict:
        """상관관계 매트릭스 계산"""
        try:
            # 모든 데이터를 하나의 DataFrame으로 병합
            combined_df = self._merge_dataframes(data_dict)

            if combined_df.empty:
                return {}

            # Pearson 및 Spearman 상관계수 계산
            pearson_matrix = combined_df.corr(method="pearson")
            spearman_matrix = combined_df.corr(method="spearman")

            return {
                "pearson": pearson_matrix.to_dict(),
                "spearman": spearman_matrix.to_dict(),
                "data_points": len(combined_df),
            }

        except Exception as e:
            logger.error(f"상관관계 매트릭스 계산 실패: {e}")
            return {}

    async def _analyze_pairs(
        self, data_dict: Dict[str, pd.DataFrame], comparison_specs: Dict = None
    ) -> Dict:
        """쌍별 상세 분석"""
        pair_results = {}
        series_names = list(data_dict.keys())

        # comparison_specs가 있으면 지정된 쌍만, 없으면 모든 조합
        if comparison_specs and "pairs" in comparison_specs:
            pairs_to_analyze = [
                (pair["lhs"], pair["rhs"]) for pair in comparison_specs["pairs"]
            ]
        else:
            pairs_to_analyze = [
                (series_names[i], series_names[j])
                for i in range(len(series_names))
                for j in range(i + 1, len(series_names))
            ]

        for name1, name2 in pairs_to_analyze:
            if name1 in data_dict and name2 in data_dict:
                pair_key = f"{name1}_vs_{name2}"

                try:
                    # 회귀 분석
                    regression_result = self._perform_regression_analysis(
                        data_dict[name1], data_dict[name2]
                    )

                    # 상관관계 세부 분석
                    correlation_detail = self._detailed_correlation_analysis(
                        data_dict[name1], data_dict[name2]
                    )

                    pair_results[pair_key] = {
                        "regression": regression_result,
                        "correlation_detail": correlation_detail,
                    }

                except Exception as e:
                    logger.warning(f"{pair_key} 쌍별 분석 실패: {e}")
                    continue

        return pair_results

    def _perform_regression_analysis(
        self, df1: pd.DataFrame, df2: pd.DataFrame
    ) -> Dict:
        """회귀 분석 수행"""
        try:
            from sklearn.linear_model import LinearRegression
            from sklearn.metrics import r2_score

            # 데이터 병합
            merged = pd.merge(
                df1[["date", "value"]].rename(columns={"value": "x"}),
                df2[["date", "value"]].rename(columns={"value": "y"}),
                on="date",
                how="inner",
            ).dropna()

            if len(merged) < 3:
                return {"error": "insufficient_data"}

            X = merged[["x"]]
            y = merged["y"]

            # 선형 회귀
            model = LinearRegression()
            model.fit(X, y)
            y_pred = model.predict(X)

            # 통계 지표
            correlation, p_value = pearsonr(merged["x"], merged["y"])
            r_squared = r2_score(y, y_pred)

            return {
                "correlation": round(correlation, 4),
                "p_value": round(p_value, 6),
                "r_squared": round(r_squared, 4),
                "slope": round(model.coef_[0], 4),
                "intercept": round(model.intercept_, 4),
                "equation": f"y = {model.coef_[0]:.4f}x + {model.intercept_:.4f}",
                "data_points": len(merged),
                "residual_std": round(np.std(y - y_pred), 4),
            }

        except Exception as e:
            logger.error(f"회귀 분석 실패: {e}")
            return {"error": str(e)}

    async def _calculate_rolling_correlations(
        self, data_dict: Dict[str, pd.DataFrame], window: int = 30
    ) -> Dict:
        """이동 상관관계 계산"""
        rolling_results = {}

        try:
            series_names = list(data_dict.keys())

            for i in range(len(series_names)):
                for j in range(i + 1, len(series_names)):
                    name1, name2 = series_names[i], series_names[j]

                    # 데이터 병합
                    merged = pd.merge(
                        data_dict[name1][["date", "value"]].rename(
                            columns={"value": name1}
                        ),
                        data_dict[name2][["date", "value"]].rename(
                            columns={"value": name2}
                        ),
                        on="date",
                        how="inner",
                    ).sort_values("date")

                    if len(merged) >= window:
                        # 이동 상관관계 계산
                        rolling_corr = merged[name1].rolling(window).corr(merged[name2])

                        # NaN 제거 후 결과 저장
                        valid_data = merged[~rolling_corr.isna()].copy()
                        valid_data["rolling_correlation"] = rolling_corr[
                            ~rolling_corr.isna()
                        ]

                        if len(valid_data) > 0:
                            rolling_results[f"{name1}_vs_{name2}"] = {
                                "window_size": window,
                                "data_points": len(valid_data),
                                "mean_correlation": round(
                                    valid_data["rolling_correlation"].mean(), 4
                                ),
                                "correlation_std": round(
                                    valid_data["rolling_correlation"].std(), 4
                                ),
                                "min_correlation": round(
                                    valid_data["rolling_correlation"].min(), 4
                                ),
                                "max_correlation": round(
                                    valid_data["rolling_correlation"].max(), 4
                                ),
                                "latest_correlation": round(
                                    valid_data["rolling_correlation"].iloc[-1], 4
                                ),
                                "trend": "increasing"
                                if valid_data["rolling_correlation"].iloc[-1]
                                > valid_data["rolling_correlation"].mean()
                                else "decreasing",
                            }

            return rolling_results

        except Exception as e:
            logger.error(f"이동 상관관계 계산 실패: {e}")
            return {}

    async def _analyze_lead_lag_relationships(
        self, data_dict: Dict[str, pd.DataFrame], max_lag: int = 10
    ) -> Dict:
        """선행-후행 관계 분석"""
        lead_lag_results = {}

        try:
            series_names = list(data_dict.keys())

            for i in range(len(series_names)):
                for j in range(i + 1, len(series_names)):
                    name1, name2 = series_names[i], series_names[j]

                    # 양방향 선행-후행 분석
                    forward_result = self._calculate_lead_lag(
                        data_dict[name1], data_dict[name2], max_lag
                    )
                    reverse_result = self._calculate_lead_lag(
                        data_dict[name2], data_dict[name1], max_lag
                    )

                    if forward_result and reverse_result:
                        # 더 강한 관계를 보이는 방향 선택
                        if (
                            forward_result["max_abs_correlation"]
                            >= reverse_result["max_abs_correlation"]
                        ):
                            best_result = forward_result
                            leader, follower = name1, name2
                        else:
                            best_result = reverse_result
                            leader, follower = name2, name1

                        lead_lag_results[f"{leader}_leads_{follower}"] = {
                            "leader": leader,
                            "follower": follower,
                            "optimal_lag_days": best_result["optimal_lag"],
                            "max_correlation": best_result["max_correlation"],
                            "relationship_strength": self._assess_correlation_strength(
                                best_result["max_correlation"]
                            ),
                            "statistical_significance": best_result["p_value"] < 0.05
                            if "p_value" in best_result
                            else False,
                        }

            return lead_lag_results

        except Exception as e:
            logger.error(f"선행-후행 관계 분석 실패: {e}")
            return {}

    def _calculate_lead_lag(
        self, leader_df: pd.DataFrame, follower_df: pd.DataFrame, max_lag: int
    ) -> Dict:
        """개별 선행-후행 관계 계산"""
        try:
            merged = pd.merge(
                leader_df[["date", "value"]].rename(columns={"value": "leader"}),
                follower_df[["date", "value"]].rename(columns={"value": "follower"}),
                on="date",
                how="inner",
            ).sort_values("date")

            if len(merged) < max_lag + 5:
                return {}

            lag_correlations = []

            for lag in range(0, max_lag + 1):
                try:
                    if lag == 0:
                        corr, p_val = pearsonr(merged["leader"], merged["follower"])
                    else:
                        leader_shifted = merged["leader"].shift(lag)
                        valid_mask = ~(
                            leader_shifted.isna() | merged["follower"].isna()
                        )

                        if valid_mask.sum() < 3:
                            continue

                        corr, p_val = pearsonr(
                            leader_shifted[valid_mask], merged["follower"][valid_mask]
                        )

                    lag_correlations.append(
                        {
                            "lag": lag,
                            "correlation": corr,
                            "p_value": p_val,
                            "abs_correlation": abs(corr),
                        }
                    )

                except Exception:
                    continue

            if not lag_correlations:
                return {}

            # 최적 지연 시간 찾기
            best_lag = max(lag_correlations, key=lambda x: x["abs_correlation"])

            return {
                "lag_correlations": lag_correlations,
                "optimal_lag": best_lag["lag"],
                "max_correlation": best_lag["correlation"],
                "max_abs_correlation": best_lag["abs_correlation"],
                "p_value": best_lag["p_value"],
            }

        except Exception as e:
            logger.error(f"개별 선행-후행 계산 실패: {e}")
            return {}

    # 유틸리티 메소드들
    def _merge_dataframes(self, data_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """여러 DataFrame을 날짜 기준으로 병합"""
        combined_df = pd.DataFrame()

        for name, df in data_dict.items():
            if "date" in df.columns and "value" in df.columns:
                temp_df = df[["date", "value"]].copy()
                temp_df.columns = ["date", name]

                if combined_df.empty:
                    combined_df = temp_df
                else:
                    combined_df = pd.merge(combined_df, temp_df, on="date", how="outer")

        # 날짜 컬럼 제외하고 숫자 데이터만 반환
        numeric_cols = combined_df.select_dtypes(include=[np.number]).columns
        return combined_df[numeric_cols]

    def _get_analysis_period(self, data_dict: Dict[str, pd.DataFrame]) -> Dict:
        """분석 기간 정보 반환"""
        all_dates = []

        for df in data_dict.values():
            if "date" in df.columns:
                all_dates.extend(df["date"].tolist())

        if all_dates:
            return {
                "start_date": min(all_dates).strftime("%Y-%m-%d"),
                "end_date": max(all_dates).strftime("%Y-%m-%d"),
                "total_days": (max(all_dates) - min(all_dates)).days,
            }

        return {}

    def _assess_significance(
        self, correlation_matrix: Dict, data_dict: Dict[str, pd.DataFrame]
    ) -> Dict:
        """통계적 유의성 평가"""
        if not correlation_matrix or "pearson" not in correlation_matrix:
            return {}

        significance_results = {}
        min_sample_size = min(len(df) for df in data_dict.values())

        # 임계 상관계수 계산 (95% 신뢰수준)
        if min_sample_size > 2:
            critical_r = 1.96 / np.sqrt(min_sample_size - 2)

            significance_results = {
                "critical_correlation_95pct": round(critical_r, 4),
                "sample_size": min_sample_size,
                "significance_threshold": 0.05,
                "interpretation": {
                    "strong": "|r| > 0.7",
                    "moderate": "0.4 < |r| < 0.7",
                    "weak": "0.2 < |r| < 0.4",
                    "very_weak": "|r| < 0.2",
                },
            }

        return significance_results

    def _assess_correlation_strength(self, correlation: float) -> str:
        """상관관계 강도 평가"""
        abs_corr = abs(correlation)

        if abs_corr > 0.8:
            return "very_strong"
        elif abs_corr > 0.6:
            return "strong"
        elif abs_corr > 0.4:
            return "moderate"
        elif abs_corr > 0.2:
            return "weak"
        else:
            return "very_weak"

    def _detailed_correlation_analysis(
        self, df1: pd.DataFrame, df2: pd.DataFrame
    ) -> Dict:
        """상관관계 세부 분석"""
        try:
            merged = pd.merge(
                df1[["date", "value"]].rename(columns={"value": "series1"}),
                df2[["date", "value"]].rename(columns={"value": "series2"}),
                on="date",
                how="inner",
            ).dropna()

            if len(merged) < 3:
                return {"error": "insufficient_data"}

            # 다양한 상관계수 계산
            pearson_corr, pearson_p = pearsonr(merged["series1"], merged["series2"])
            spearman_corr, spearman_p = spearmanr(merged["series1"], merged["series2"])

            # 분위수별 상관관계
            q25 = merged["series1"].quantile(0.25)
            q75 = merged["series1"].quantile(0.75)

            lower_quartile = merged[merged["series1"] <= q25]
            upper_quartile = merged[merged["series1"] >= q75]

            lower_corr = (
                pearsonr(lower_quartile["series1"], lower_quartile["series2"])[0]
                if len(lower_quartile) >= 3
                else None
            )
            upper_corr = (
                pearsonr(upper_quartile["series1"], upper_quartile["series2"])[0]
                if len(upper_quartile) >= 3
                else None
            )

            return {
                "pearson_correlation": round(pearson_corr, 4),
                "pearson_p_value": round(pearson_p, 6),
                "spearman_correlation": round(spearman_corr, 4),
                "spearman_p_value": round(spearman_p, 6),
                "data_points": len(merged),
                "correlation_strength": self._assess_correlation_strength(pearson_corr),
                "quartile_analysis": {
                    "lower_quartile_correlation": round(lower_corr, 4)
                    if lower_corr
                    else None,
                    "upper_quartile_correlation": round(upper_corr, 4)
                    if upper_corr
                    else None,
                    "correlation_consistency": "consistent"
                    if (
                        lower_corr and upper_corr and abs(lower_corr - upper_corr) < 0.3
                    )
                    else "variable",
                },
            }

        except Exception as e:
            logger.error(f"상관관계 세부 분석 실패: {e}")
            return {"error": str(e)}
