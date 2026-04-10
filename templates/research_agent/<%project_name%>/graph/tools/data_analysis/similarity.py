import logging
import time
from typing import Any, Dict, List, Type

import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine, euclidean
from scipy.stats import pearsonr

from <%project_name%>.common.types.nodes import (
    DataAnalysisToolNodeInput,
    DataAnalysisToolNodeOutput,
)
from <%project_name%>.graph.prompts.prompt_manager import build_formatted_prompts
from <%project_name%>.graph.tools.data_analysis.utils import (
    DataPreprocessor,
    StatisticalValidator,
)
from <%project_name%>.graph.tools.tool_manager import BaseAnalysisTool

logger = logging.getLogger(__name__)


class TimeSeriesTrendTool(BaseAnalysisTool):
    @property
    def name(self) -> str:
        return "timeseries_trend"

    @property
    def description(self) -> str:
        return "Analyze time series data trends and anomalies"

    @property
    def input_type(self) -> Type[DataAnalysisToolNodeInput]:
        return DataAnalysisToolNodeInput

    @property
    def output_type(self) -> Type[DataAnalysisToolNodeOutput]:
        return DataAnalysisToolNodeOutput

    async def analyze(
        self, input_data: DataAnalysisToolNodeInput
    ) -> DataAnalysisToolNodeOutput:
        # 시계열 분석 로직
        return DataAnalysisToolNodeOutput(...)


class SimilarityAnalyzer:
    """
    시계열 유사도 분석기 - 다양한 유사도 지표 계산
    """

    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.validator = StatisticalValidator()

    async def analyze(self, data_dict: Dict[str, Any]) -> Dict:
        """종합적인 유사도 분석 수행"""
        start_time = time.time()

        try:
            # 데이터 전처리
            processed_data = await self._preprocess_data(data_dict)

            if len(processed_data) < 2:
                return {
                    "error": "insufficient_data",
                    "message": "유사도 분석을 위해서는 최소 2개의 데이터셋이 필요합니다.",
                }

            # 유사도 매트릭스 계산
            similarity_matrix = self._calculate_similarity_matrix(processed_data)

            # 쌍별 상세 유사도 분석
            pairwise_analysis = self._analyze_pairwise_similarity(processed_data)

            # 패턴 유사도 분석
            pattern_similarity = self._analyze_pattern_similarity(processed_data)

            # 시간 지연 유사도
            time_lagged_similarity = self._analyze_time_lagged_similarity(
                processed_data
            )

            result = {
                "summary": {
                    "data_series_count": len(processed_data),
                    "execution_time_seconds": round(time.time() - start_time, 3),
                },
                "similarity_matrix": similarity_matrix,
                "pairwise_analysis": pairwise_analysis,
                "pattern_similarity": pattern_similarity,
                "time_lagged_similarity": time_lagged_similarity,
            }

            logger.info(f"유사도 분석 완료: {len(processed_data)}개 시리즈")
            return result

        except Exception as e:
            logger.error(f"유사도 분석 실패: {e}")
            return {"error": "analysis_failed", "message": str(e)}

    async def _preprocess_data(
        self, data_dict: Dict[str, Any]
    ) -> Dict[str, pd.DataFrame]:
        """데이터 전처리"""
        processed = {}

        for name, raw_data in data_dict.items():
            try:
                df = self.preprocessor.convert_to_dataframe(raw_data)

                if df is not None and len(df) >= 3:
                    df = self.preprocessor.standardize_columns(df)
                    df = self.preprocessor.handle_missing_values(df)

                    if self.validator.is_valid_timeseries(df):
                        processed[name] = df

            except Exception as e:
                logger.warning(f"{name} 데이터 전처리 실패: {e}")
                continue

        return processed

    def _calculate_similarity_matrix(self, data_dict: Dict[str, pd.DataFrame]) -> Dict:
        """다양한 유사도 지표의 매트릭스 계산"""
        try:
            series_names = list(data_dict.keys())
            n_series = len(series_names)

            # 초기화
            cosine_matrix = np.zeros((n_series, n_series))
            pearson_matrix = np.zeros((n_series, n_series))
            euclidean_matrix = np.zeros((n_series, n_series))

            for i, name1 in enumerate(series_names):
                for j, name2 in enumerate(series_names):
                    if i == j:
                        cosine_matrix[i, j] = 1.0
                        pearson_matrix[i, j] = 1.0
                        euclidean_matrix[i, j] = 0.0
                    else:
                        # 데이터 정렬 및 병합
                        merged = self._merge_series_for_comparison(
                            data_dict[name1], data_dict[name2]
                        )

                        if len(merged) >= 3:
                            series1 = merged["series1"].values
                            series2 = merged["series2"].values

                            # 코사인 유사도
                            cosine_sim = 1 - cosine(series1, series2)
                            cosine_matrix[i, j] = cosine_sim

                            # 피어슨 상관계수
                            pearson_corr, _ = pearsonr(series1, series2)
                            pearson_matrix[i, j] = pearson_corr

                            # 정규화된 유클리드 거리 (유사도로 변환)
                            euclidean_dist = euclidean(series1, series2)
                            max_possible_dist = np.sqrt(len(series1)) * (
                                np.max(series1) - np.min(series1)
                            )
                            euclidean_sim = 1 - (euclidean_dist / max_possible_dist)
                            euclidean_matrix[i, j] = euclidean_sim

            return {
                "cosine_similarity": {
                    "matrix": cosine_matrix.tolist(),
                    "series_names": series_names,
                },
                "pearson_correlation": {
                    "matrix": pearson_matrix.tolist(),
                    "series_names": series_names,
                },
                "euclidean_similarity": {
                    "matrix": euclidean_matrix.tolist(),
                    "series_names": series_names,
                },
            }

        except Exception as e:
            logger.error(f"유사도 매트릭스 계산 실패: {e}")
            return {}

    def _merge_series_for_comparison(
        self, df1: pd.DataFrame, df2: pd.DataFrame
    ) -> pd.DataFrame:
        """두 시계열 데이터를 비교를 위해 병합"""
        try:
            merged = pd.merge(
                df1[["date", "value"]].rename(columns={"value": "series1"}),
                df2[["date", "value"]].rename(columns={"value": "series2"}),
                on="date",
                how="inner",
            ).sort_values("date")

            # 결측값 제거
            merged = merged.dropna()

            return merged

        except Exception as e:
            logger.error(f"시계열 병합 실패: {e}")
            return pd.DataFrame()

    def _analyze_pairwise_similarity(self, data_dict: Dict[str, pd.DataFrame]) -> Dict:
        """쌍별 상세 유사도 분석"""
        try:
            pairwise_results = {}
            series_names = list(data_dict.keys())

            for i in range(len(series_names)):
                for j in range(i + 1, len(series_names)):
                    name1, name2 = series_names[i], series_names[j]
                    pair_key = f"{name1}_vs_{name2}"

                    # 데이터 병합
                    merged = self._merge_series_for_comparison(
                        data_dict[name1], data_dict[name2]
                    )

                    if len(merged) < 3:
                        pairwise_results[pair_key] = {"error": "insufficient_data"}
                        continue

                    series1 = merged["series1"].values
                    series2 = merged["series2"].values

                    # 다양한 유사도 지표 계산
                    similarity_metrics = self._calculate_comprehensive_similarity(
                        series1, series2
                    )

                    # 시계열별 통계적 특성 비교
                    statistical_comparison = self._compare_statistical_properties(
                        series1, series2
                    )

                    # 방향성 분석 (상승/하락 패턴 유사성)
                    directional_similarity = self._analyze_directional_similarity(
                        series1, series2
                    )

                    # 변동성 유사도
                    volatility_similarity = self._analyze_volatility_similarity(
                        series1, series2
                    )

                    pairwise_results[pair_key] = {
                        "data_points": len(merged),
                        "analysis_period": {
                            "start": merged["date"].min().strftime("%Y-%m-%d"),
                            "end": merged["date"].max().strftime("%Y-%m-%d"),
                        },
                        "similarity_metrics": similarity_metrics,
                        "statistical_comparison": statistical_comparison,
                        "directional_similarity": directional_similarity,
                        "volatility_similarity": volatility_similarity,
                    }

            return pairwise_results

        except Exception as e:
            logger.error(f"쌍별 유사도 분석 실패: {e}")
            return {}

    def _calculate_comprehensive_similarity(
        self, series1: np.ndarray, series2: np.ndarray
    ) -> Dict:
        """종합적인 유사도 지표 계산"""
        try:
            # 피어슨 상관계수
            pearson_corr, pearson_p = pearsonr(series1, series2)

            # 스피어만 상관계수
            from scipy.stats import spearmanr

            spearman_corr, spearman_p = spearmanr(series1, series2)

            # 코사인 유사도
            cosine_sim = 1 - cosine(series1, series2)

            # 정규화된 유클리드 유사도
            euclidean_dist = euclidean(series1, series2)
            max_range = max(np.ptp(series1), np.ptp(series2))  # peak-to-peak
            euclidean_sim = (
                1 - (euclidean_dist / (np.sqrt(len(series1)) * max_range))
                if max_range > 0
                else 1.0
            )

            # 동적 시간 왜곡 (DTW) 근사
            dtw_similarity = self._calculate_dtw_similarity(series1, series2)

            # 평균 절대 퍼센트 오차 (MAPE) 기반 유사도
            mape = (
                np.mean(
                    np.abs((series1 - series2) / np.where(series1 != 0, series1, 1e-8))
                )
                * 100
            )
            mape_similarity = max(0, 1 - mape / 100)

            return {
                "pearson_correlation": {
                    "value": round(pearson_corr, 4),
                    "p_value": round(pearson_p, 6),
                    "strength": self._assess_correlation_strength(pearson_corr),
                },
                "spearman_correlation": {
                    "value": round(spearman_corr, 4),
                    "p_value": round(spearman_p, 6),
                    "strength": self._assess_correlation_strength(spearman_corr),
                },
                "cosine_similarity": {
                    "value": round(cosine_sim, 4),
                    "interpretation": "높은 방향성 유사도"
                    if cosine_sim > 0.8
                    else "중간 방향성 유사도"
                    if cosine_sim > 0.5
                    else "낮은 방향성 유사도",
                },
                "euclidean_similarity": {
                    "value": round(euclidean_sim, 4),
                    "interpretation": "높은 크기 유사도"
                    if euclidean_sim > 0.8
                    else "중간 크기 유사도"
                    if euclidean_sim > 0.5
                    else "낮은 크기 유사도",
                },
                "dtw_similarity": dtw_similarity,
                "mape_similarity": {
                    "value": round(mape_similarity, 4),
                    "mape_percent": round(mape, 2),
                    "interpretation": "매우 유사"
                    if mape < 10
                    else "유사"
                    if mape < 25
                    else "다소 다름",
                },
            }

        except Exception as e:
            logger.error(f"종합 유사도 계산 실패: {e}")
            return {}

    def _calculate_dtw_similarity(
        self, series1: np.ndarray, series2: np.ndarray
    ) -> Dict:
        """동적 시간 왜곡 유사도 계산 (단순화 버전)"""
        try:
            # DTW 거리 계산 (단순화된 버전)
            n, m = len(series1), len(series2)

            # 너무 긴 시계열의 경우 샘플링
            if n > 100 or m > 100:
                step = max(n // 100, m // 100, 1)
                series1_sampled = series1[::step]
                series2_sampled = series2[::step]
            else:
                series1_sampled = series1
                series2_sampled = series2

            # 정규화
            series1_norm = (series1_sampled - np.mean(series1_sampled)) / (
                np.std(series1_sampled) + 1e-8
            )
            series2_norm = (series2_sampled - np.mean(series2_sampled)) / (
                np.std(series2_sampled) + 1e-8
            )

            # 단순화된 DTW 거리 (제한된 경로)
            dtw_distance = self._simple_dtw_distance(series1_norm, series2_norm)

            # 유사도로 변환
            max_possible_distance = (
                max(len(series1_norm), len(series2_norm)) * 2
            )  # 대략적인 최대 거리
            dtw_similarity = 1 - (dtw_distance / max_possible_distance)
            dtw_similarity = max(0, min(1, dtw_similarity))

            return {
                "value": round(dtw_similarity, 4),
                "dtw_distance": round(dtw_distance, 4),
                "interpretation": "시간 축 유연성을 고려한 유사도",
                "note": "단순화된 DTW 알고리즘 사용",
            }

        except Exception as e:
            logger.error(f"DTW 유사도 계산 실패: {e}")
            return {"error": str(e)}

    def _simple_dtw_distance(self, s1: np.ndarray, s2: np.ndarray) -> float:
        """단순화된 DTW 거리 계산"""
        try:
            n, m = len(s1), len(s2)

            # DTW 행렬 초기화
            dtw_matrix = np.full((n + 1, m + 1), float("inf"))
            dtw_matrix[0, 0] = 0

            # DTW 계산
            for i in range(1, n + 1):
                for j in range(1, m + 1):
                    cost = abs(s1[i - 1] - s2[j - 1])
                    dtw_matrix[i, j] = cost + min(
                        dtw_matrix[i - 1, j],  # 삽입
                        dtw_matrix[i, j - 1],  # 삭제
                        dtw_matrix[i - 1, j - 1],  # 매치
                    )

            return dtw_matrix[n, m]

        except Exception as e:
            logger.error(f"단순 DTW 계산 실패: {e}")
            return float("inf")

    def _compare_statistical_properties(
        self, series1: np.ndarray, series2: np.ndarray
    ) -> Dict:
        """통계적 특성 비교"""
        try:
            stats1 = {
                "mean": np.mean(series1),
                "std": np.std(series1),
                "min": np.min(series1),
                "max": np.max(series1),
                "skewness": self._calculate_skewness(series1),
                "kurtosis": self._calculate_kurtosis(series1),
            }

            stats2 = {
                "mean": np.mean(series2),
                "std": np.std(series2),
                "min": np.min(series2),
                "max": np.max(series2),
                "skewness": self._calculate_skewness(series2),
                "kurtosis": self._calculate_kurtosis(series2),
            }

            # 통계적 차이 계산
            differences = {}
            similarity_scores = {}

            for key in stats1.keys():
                val1, val2 = stats1[key], stats2[key]

                # 절대 차이
                abs_diff = abs(val1 - val2)
                differences[f"{key}_difference"] = round(abs_diff, 4)

                # 상대 차이 (퍼센트)
                if val1 != 0:
                    rel_diff = abs((val2 - val1) / val1) * 100
                    differences[f"{key}_relative_difference_pct"] = round(rel_diff, 2)

                # 유사도 점수 (0-1)
                if key in ["mean", "std"]:
                    max_val = max(abs(val1), abs(val2))
                    similarity = 1 - (abs_diff / max_val) if max_val > 0 else 1.0
                    similarity_scores[f"{key}_similarity"] = round(
                        max(0, similarity), 4
                    )

            return {
                "series1_stats": {k: round(v, 4) for k, v in stats1.items()},
                "series2_stats": {k: round(v, 4) for k, v in stats2.items()},
                "differences": differences,
                "similarity_scores": similarity_scores,
                "overall_statistical_similarity": round(
                    np.mean(list(similarity_scores.values())), 4
                ),
            }

        except Exception as e:
            logger.error(f"통계적 특성 비교 실패: {e}")
            return {}

    def _analyze_directional_similarity(
        self, series1: np.ndarray, series2: np.ndarray
    ) -> Dict:
        """방향성 유사도 분석 (상승/하락 패턴)"""
        try:
            # 변화율 계산
            changes1 = np.diff(series1)
            changes2 = np.diff(series2)

            # 방향 분류 (상승: 1, 하락: -1, 횡보: 0)
            directions1 = np.sign(changes1)
            directions2 = np.sign(changes2)

            # 방향 일치도
            direction_matches = (directions1 == directions2).sum()
            total_periods = len(directions1)
            direction_agreement = direction_matches / total_periods

            # 상승/하락 기간별 분석
            up_periods1 = (directions1 > 0).sum()
            down_periods1 = (directions1 < 0).sum()
            flat_periods1 = (directions1 == 0).sum()

            up_periods2 = (directions2 > 0).sum()
            down_periods2 = (directions2 < 0).sum()
            flat_periods2 = (directions2 == 0).sum()

            # 강도 기반 방향성 분석 (큰 변화만 고려)
            threshold = max(np.std(changes1), np.std(changes2)) * 0.5

            significant_changes1 = changes1[np.abs(changes1) > threshold]
            significant_changes2 = changes2[np.abs(changes1) > threshold]

            if len(significant_changes1) > 0 and len(significant_changes2) > 0:
                significant_direction_corr = pearsonr(
                    significant_changes1, significant_changes2
                )[0]
            else:
                significant_direction_corr = 0

            return {
                "overall_direction_agreement": round(direction_agreement, 4),
                "direction_agreement_pct": round(direction_agreement * 100, 2),
                "pattern_distribution": {
                    "series1": {
                        "upward_periods": up_periods1,
                        "downward_periods": down_periods1,
                        "sideways_periods": flat_periods1,
                    },
                    "series2": {
                        "upward_periods": up_periods2,
                        "downward_periods": down_periods2,
                        "sideways_periods": flat_periods2,
                    },
                },
                "significant_moves_correlation": round(significant_direction_corr, 4),
                "interpretation": self._interpret_directional_similarity(
                    direction_agreement, significant_direction_corr
                ),
            }

        except Exception as e:
            logger.error(f"방향성 유사도 분석 실패: {e}")
            return {}

    def _analyze_volatility_similarity(
        self, series1: np.ndarray, series2: np.ndarray
    ) -> Dict:
        """변동성 유사도 분석"""
        try:
            # 단순 변동성 (표준편차)
            volatility1 = np.std(series1)
            volatility2 = np.std(series2)

            # 이동 변동성 (rolling standard deviation)
            window = min(10, len(series1) // 4)
            if window >= 3:
                rolling_vol1 = pd.Series(series1).rolling(window).std().dropna()
                rolling_vol2 = pd.Series(series2).rolling(window).std().dropna()

                if len(rolling_vol1) > 0 and len(rolling_vol2) > 0:
                    rolling_vol_corr = pearsonr(rolling_vol1, rolling_vol2)[0]
                    avg_rolling_vol1 = np.mean(rolling_vol1)
                    avg_rolling_vol2 = np.mean(rolling_vol2)
                else:
                    rolling_vol_corr = 0
                    avg_rolling_vol1 = volatility1
                    avg_rolling_vol2 = volatility2
            else:
                rolling_vol_corr = 0
                avg_rolling_vol1 = volatility1
                avg_rolling_vol2 = volatility2

            # 변동성 비율
            vol_ratio = volatility2 / volatility1 if volatility1 > 0 else 1.0

            # 변동성 유사도 점수
            vol_similarity = (
                1 - abs(volatility1 - volatility2) / max(volatility1, volatility2)
                if max(volatility1, volatility2) > 0
                else 1.0
            )
            vol_similarity = max(0, vol_similarity)

            return {
                "static_volatility": {
                    "series1_std": round(volatility1, 4),
                    "series2_std": round(volatility2, 4),
                    "volatility_ratio": round(vol_ratio, 4),
                    "volatility_similarity": round(vol_similarity, 4),
                },
                "dynamic_volatility": {
                    "rolling_window": window,
                    "rolling_volatility_correlation": round(rolling_vol_corr, 4),
                    "avg_rolling_vol1": round(avg_rolling_vol1, 4),
                    "avg_rolling_vol2": round(avg_rolling_vol2, 4),
                },
                "interpretation": self._interpret_volatility_similarity(
                    vol_similarity, rolling_vol_corr
                ),
            }

        except Exception as e:
            logger.error(f"변동성 유사도 분석 실패: {e}")
            return {}

    def _analyze_pattern_similarity(self, data_dict: Dict[str, pd.DataFrame]) -> Dict:
        """패턴 유사도 분석"""
        try:
            pattern_results = {}
            series_names = list(data_dict.keys())

            for i in range(len(series_names)):
                for j in range(i + 1, len(series_names)):
                    name1, name2 = series_names[i], series_names[j]
                    pair_key = f"{name1}_vs_{name2}"

                    # 데이터 병합
                    merged = self._merge_series_for_comparison(
                        data_dict[name1], data_dict[name2]
                    )

                    if len(merged) < 10:  # 패턴 분석을 위해서는 더 많은 데이터 필요
                        pattern_results[pair_key] = {
                            "error": "insufficient_data_for_pattern_analysis"
                        }
                        continue

                    series1 = merged["series1"].values
                    series2 = merged["series2"].values

                    # 추세 패턴 유사도
                    trend_similarity = self._analyze_trend_pattern_similarity(
                        series1, series2
                    )

                    # 주기성 패턴 유사도
                    cyclical_similarity = self._analyze_cyclical_pattern_similarity(
                        series1, series2
                    )

                    # 극값 패턴 유사도 (피크와 밸리)
                    extrema_similarity = self._analyze_extrema_pattern_similarity(
                        series1, series2, merged["date"].values
                    )

                    pattern_results[pair_key] = {
                        "trend_pattern": trend_similarity,
                        "cyclical_pattern": cyclical_similarity,
                        "extrema_pattern": extrema_similarity,
                    }

            return pattern_results

        except Exception as e:
            logger.error(f"패턴 유사도 분석 실패: {e}")
            return {}

    def _analyze_time_lagged_similarity(
        self, data_dict: Dict[str, pd.DataFrame], max_lag: int = 10
    ) -> Dict:
        """시간 지연 유사도 분석"""
        try:
            lagged_results = {}
            series_names = list(data_dict.keys())

            for i in range(len(series_names)):
                for j in range(i + 1, len(series_names)):
                    name1, name2 = series_names[i], series_names[j]
                    pair_key = f"{name1}_vs_{name2}"

                    # 데이터 병합
                    merged = self._merge_series_for_comparison(
                        data_dict[name1], data_dict[name2]
                    )

                    if len(merged) < max_lag + 5:
                        lagged_results[pair_key] = {
                            "error": "insufficient_data_for_lag_analysis"
                        }
                        continue

                    series1 = merged["series1"].values
                    series2 = merged["series2"].values

                    # 다양한 지연에 대한 유사도 계산
                    lag_analysis = self._calculate_lagged_similarities(
                        series1, series2, max_lag
                    )

                    # 최적 지연 시간 찾기
                    optimal_lag_info = self._find_optimal_lag(lag_analysis)

                    lagged_results[pair_key] = {
                        "max_lag_tested": max_lag,
                        "lag_analysis": lag_analysis,
                        "optimal_lag": optimal_lag_info,
                        "interpretation": self._interpret_lag_analysis(
                            optimal_lag_info
                        ),
                    }

            return lagged_results

        except Exception as e:
            logger.error(f"시간 지연 유사도 분석 실패: {e}")
            return {}

    def _calculate_lagged_similarities(
        self, series1: np.ndarray, series2: np.ndarray, max_lag: int
    ) -> List[Dict]:
        """다양한 지연에 대한 유사도 계산"""
        try:
            lag_results = []

            for lag in range(-max_lag, max_lag + 1):
                if lag == 0:
                    # 동시 상관관계
                    corr_coef, p_value = pearsonr(series1, series2)
                    cosine_sim = 1 - cosine(series1, series2)
                    data_points = len(series1)

                elif lag > 0:
                    # series1이 series2보다 lag만큼 앞선다
                    s1_shifted = series1[:-lag]
                    s2_current = series2[lag:]

                else:  # lag < 0
                    # series2가 series1보다 |lag|만큼 앞선다
                    s1_current = series1[-lag:]
                    s2_shifted = series2[:lag]

                if lag != 0:
                    if len(s1_shifted if lag > 0 else s1_current) >= 3:
                        if lag > 0:
                            corr_coef, p_value = pearsonr(s1_shifted, s2_current)
                            cosine_sim = 1 - cosine(s1_shifted, s2_current)
                            data_points = len(s1_shifted)
                        else:
                            corr_coef, p_value = pearsonr(s1_current, s2_shifted)
                            cosine_sim = 1 - cosine(s1_current, s2_shifted)
                            data_points = len(s1_current)
                    else:
                        continue

                lag_results.append(
                    {
                        "lag": lag,
                        "pearson_correlation": round(corr_coef, 4),
                        "p_value": round(p_value, 6),
                        "cosine_similarity": round(cosine_sim, 4),
                        "abs_correlation": round(abs(corr_coef), 4),
                        "data_points": data_points,
                    }
                )

            return lag_results

        except Exception as e:
            logger.error(f"지연 유사도 계산 실패: {e}")
            return []

    def _find_optimal_lag(self, lag_analysis: List[Dict]) -> Dict:
        """최적 지연 시간 찾기"""
        try:
            if not lag_analysis:
                return {}

            # 절대 상관계수가 가장 높은 지연
            best_by_correlation = max(lag_analysis, key=lambda x: x["abs_correlation"])

            # 코사인 유사도가 가장 높은 지연
            best_by_cosine = max(lag_analysis, key=lambda x: x["cosine_similarity"])

            # 통계적 유의성을 고려한 최적 지연
            significant_lags = [lag for lag in lag_analysis if lag["p_value"] < 0.05]

            if significant_lags:
                best_significant = max(
                    significant_lags, key=lambda x: x["abs_correlation"]
                )
            else:
                best_significant = best_by_correlation

            return {
                "best_correlation_lag": best_by_correlation,
                "best_cosine_lag": best_by_cosine,
                "best_significant_lag": best_significant,
                "has_significant_lag": len(significant_lags) > 0,
                "recommendation": self._recommend_optimal_lag(
                    best_by_correlation, best_significant
                ),
            }

        except Exception as e:
            logger.error(f"최적 지연 찾기 실패: {e}")
            return {}

    # 유틸리티 메서드들
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

    def _calculate_skewness(self, data: np.ndarray) -> float:
        """왜도 계산"""
        try:
            from scipy.stats import skew

            return skew(data)
        except:
            # 수동 계산
            mean_val = np.mean(data)
            std_val = np.std(data)
            if std_val > 0:
                return np.mean(((data - mean_val) / std_val) ** 3)
            return 0

    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """첨도 계산"""
        try:
            from scipy.stats import kurtosis

            return kurtosis(data, fisher=True)  # excess kurtosis
        except:
            # 수동 계산
            mean_val = np.mean(data)
            std_val = np.std(data)
            if std_val > 0:
                return np.mean(((data - mean_val) / std_val) ** 4) - 3
            return 0

    def _interpret_directional_similarity(
        self, direction_agreement: float, significant_corr: float
    ) -> str:
        """방향성 유사도 해석"""
        if direction_agreement > 0.8:
            return "매우 높은 방향성 일치"
        elif direction_agreement > 0.6:
            return "높은 방향성 일치"
        elif direction_agreement > 0.4:
            return "중간 수준 방향성 일치"
        else:
            return "낮은 방향성 일치"

    def _interpret_volatility_similarity(
        self, vol_similarity: float, rolling_corr: float
    ) -> str:
        """변동성 유사도 해석"""
        if vol_similarity > 0.8 and rolling_corr > 0.6:
            return "매우 유사한 변동성 패턴"
        elif vol_similarity > 0.6:
            return "유사한 변동성 수준"
        else:
            return "다른 변동성 특성"

    def _interpret_lag_analysis(self, optimal_lag_info: Dict) -> str:
        """지연 분석 결과 해석"""
        if not optimal_lag_info:
            return "지연 분석 불가"

        best_lag = optimal_lag_info.get("best_correlation_lag", {})
        lag = best_lag.get("lag", 0)
        correlation = best_lag.get("abs_correlation", 0)

        if correlation < 0.3:
            return "유의미한 시간 지연 관계 없음"
        elif lag == 0:
            return "동시 관계가 가장 강함"
        elif lag > 0:
            return f"첫 번째 시계열이 {lag}일 선행"
        else:
            return f"두 번째 시계열이 {abs(lag)}일 선행"

    def _recommend_optimal_lag(self, best_corr: Dict, best_sig: Dict) -> str:
        """최적 지연 추천"""
        if best_corr["abs_correlation"] > 0.6:
            return f"지연 {best_corr['lag']}일 권장 (상관계수: {best_corr['pearson_correlation']:.3f})"
        else:
            return "유의미한 지연 관계 없음"

    # 추가 패턴 분석 메서드들 (단순화 버전)
    def _analyze_trend_pattern_similarity(
        self, series1: np.ndarray, series2: np.ndarray
    ) -> Dict:
        """추세 패턴 유사도 분석"""
        try:
            # 선형 추세 계산
            x = np.arange(len(series1))
            trend1 = np.polyfit(x, series1, 1)[0]  # 기울기
            trend2 = np.polyfit(x, series2, 1)[0]

            # 추세 방향 일치도
            trend_direction_match = np.sign(trend1) == np.sign(trend2)

            # 추세 강도 유사도
            trend_strength_similarity = 1 - abs(trend1 - trend2) / (
                max(abs(trend1), abs(trend2)) + 1e-8
            )

            return {
                "trend1_slope": round(trend1, 6),
                "trend2_slope": round(trend2, 6),
                "direction_match": trend_direction_match,
                "strength_similarity": round(max(0, trend_strength_similarity), 4),
            }
        except:
            return {"error": "trend_analysis_failed"}

    def _analyze_cyclical_pattern_similarity(
        self, series1: np.ndarray, series2: np.ndarray
    ) -> Dict:
        """주기성 패턴 유사도 분석 (단순화)"""
        try:
            # 자기상관 기반 주기성 탐지 (단순화)
            max_lag = min(len(series1) // 4, 20)

            autocorr1 = [
                pearsonr(
                    series1[:-i] if i > 0 else series1,
                    series1[i:] if i > 0 else series1,
                )[0]
                for i in range(1, max_lag)
            ]
            autocorr2 = [
                pearsonr(
                    series2[:-i] if i > 0 else series2,
                    series2[i:] if i > 0 else series2,
                )[0]
                for i in range(1, max_lag)
            ]

            # 자기상관 패턴 유사도
            if len(autocorr1) > 0 and len(autocorr2) > 0:
                autocorr_similarity = pearsonr(autocorr1, autocorr2)[0]
            else:
                autocorr_similarity = 0

            return {
                "autocorr_pattern_similarity": round(autocorr_similarity, 4),
                "interpretation": "유사한 주기성"
                if abs(autocorr_similarity) > 0.5
                else "다른 주기성",
            }
        except:
            return {"error": "cyclical_analysis_failed"}

    def _analyze_extrema_pattern_similarity(
        self, series1: np.ndarray, series2: np.ndarray, dates: np.ndarray
    ) -> Dict:
        """극값 패턴 유사도 분석"""
        try:
            from scipy.signal import find_peaks

            # 피크 탐지
            peaks1, _ = find_peaks(series1, height=np.percentile(series1, 75))
            peaks2, _ = find_peaks(series2, height=np.percentile(series2, 75))

            # 밸리 탐지 (음수로 변환 후 피크 찾기)
            valleys1, _ = find_peaks(-series1, height=-np.percentile(series1, 25))
            valleys2, _ = find_peaks(-series2, height=-np.percentile(series2, 25))

            # 극값 발생 시기 유사도 (단순화)
            extrema_time_similarity = 0
            if len(peaks1) > 0 and len(peaks2) > 0:
                # 피크 발생 간격 유사도 계산 (단순화)
                extrema_time_similarity = 0.5  # 플레이스홀더

            return {
                "peaks_count": {"series1": len(peaks1), "series2": len(peaks2)},
                "valleys_count": {"series1": len(valleys1), "series2": len(valleys2)},
                "extrema_timing_similarity": round(extrema_time_similarity, 4),
            }
        except:
            return {"error": "extrema_analysis_failed"}


class TimeseriesTrendNode(BaseAnalysisTool):
    """
    스프레드/변동·이상치/전후 비교, 특정 기간의 시계열 데이터를 수집하여 트렌드를 요약하거나 비교
    """

    name: str = "TimeseriesTrendNode"
    description: str = "시계열 데이터의 패턴과 트렌드를 분석하여 유사 구간을 찾고 예측 인사이트를 도출합니다... 📈"
    input_type: type = DataAnalysisToolNodeInput
    output_type: type = DataAnalysisToolNodeOutput

    async def analyze(
        self, input_data: DataAnalysisToolNodeInput
    ) -> DataAnalysisToolNodeOutput:
        logger.info(f"[DEBUG] 현재 대화 히스토리: {input.histories}")
        current_data = input.similarity_mcp_search_results
        historical_data = input.similarity_historical_results
        # 웹 소스는 나중에 사용할 수 있도록 저장하지만 현재는 사용되지 않음
        # web_sources = input.web_results

        # 유사 구간 최대 3개 추출
        # current_df, historical_df, similar_patterns_df = analyze_similarity_patterns(
        #     current_data=current_data, historical_data=historical_data, top_n=3
        # )
        import numpy as np

        current_df, historical_df, similar_patterns_df = np(), np(), np()

        logger.info(
            f"[유사 구간 추출 완료] 유사도 기반 유사 구간 수: {len(similar_patterns_df)}"
        )
        # 유사 구간 데이터 저장
        # save_dataframe_to_json(similar_patterns_df, folder="./retrieved_data", prefix="similar_patterns")

        # RDB 데이터가 부족하거나 유사패턴이 없음 → LLM 판단 기반 프롬프트
        output = DataAnalysisToolNodeOutput()
        if current_df.empty or historical_df.empty or similar_patterns_df.empty:
            logger.info(
                "RDB 데이터 부족 또는 유사패턴 없음: build_similarity_prompt 사용"
            )
            input = input.model_dump() | {"tools_desc": ""}
            messages = await build_formatted_prompts(
                company_code=2020,  # state.req_input.company_code,
                node_name=self.name,
                prompt_tags=[],
                output_type=self.output_type,
                **input,
            )
            output = {}  # await ainvoke_react_agent(messages=messages, tools=[])

            output.charts = []  # 차트는 빈 리스트로
            output = {
                "messages": [
                    {
                        "content": {
                            "text": output.response or "결과 없음",
                            "charts": [],  # 차트는 빈 리스트
                            "sources": output.web_sources or [],
                            "vector_sources": output.vector_metadata or [],
                            "related_data": output.related_data or [],
                        },
                        "usage": output.usage or {},
                        "sql_query": output.sql_query or "",
                        "used_tables": output.used_tables or [],
                        "rewrite": output.rewrite or "",
                    }
                ]
            }
            return output

        input.similarity_current_data = current_df.to_dict(orient="list")
        input.similarity_historical_data = historical_df.to_dict(orient="list")
        input.similar_patterns = similar_patterns_df.to_dict(orient="records")

        output = {}  # await ainvoke_react_agent(messages=messages, tools=[])

        # MCP 데이터가 있을 때만 차트 생성
        output = {}  # await ainvoke_react_agent(messages=messages, tools=[])

        results: dict = {
            "messages": [
                {
                    "content": {
                        "text": output.response or "결과 없음",
                        "charts": output.charts or [],
                        "sources": output.web_sources or [],
                        "vector_sources": output.vector_metadata or [],
                        "related_data": output.related_data or [],
                    },
                    "usage": output.usage or {},
                    "sql_query": output.sql_query or "",
                    "used_tables": output.used_tables or [],
                    "rewrite": output.rewrite or "",
                }
            ]
        }
        return DataAnalysisToolNodeOutput(results=results)
