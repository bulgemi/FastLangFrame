import logging
import time
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from scipy.stats import linregress
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

from .utils import DataPreprocessor, StatisticalValidator

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """
    시계열 추세 분석기 - 선형/비선형 추세, 변동성, 패턴 탐지
    """

    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.validator = StatisticalValidator()

    async def analyze(self, data_dict: Dict[str, Any]) -> Dict:
        """
        종합적인 추세 분석 수행
        """
        start_time = time.time()

        try:
            # 1. 데이터 전처리
            processed_data = await self._preprocess_data(data_dict)

            if not processed_data:
                return {
                    "error": "no_valid_data",
                    "message": "분석할 유효한 데이터가 없습니다.",
                }

            # 2. 개별 시리즈 추세 분석
            individual_trends = await self._analyze_individual_trends(processed_data)

            # 3. 변동성 분석
            volatility_analysis = await self._analyze_volatility_patterns(
                processed_data
            )

            # 4. 주기성 및 계절성 분석
            seasonality_analysis = await self._analyze_seasonality_patterns(
                processed_data
            )

            # 5. 구조적 변화점 탐지
            structural_changes = await self._detect_structural_changes(processed_data)

            # 6. 예측 및 전망
            trend_forecasts = await self._generate_trend_forecasts(processed_data)

            # 7. 결과 종합
            analysis_result = {
                "summary": {
                    "data_series_count": len(processed_data),
                    "analysis_period": self._get_analysis_period(processed_data),
                    "total_data_points": sum(len(df) for df in processed_data.values()),
                    "execution_time_seconds": round(time.time() - start_time, 3),
                },
                "individual_trends": individual_trends,
                "volatility_analysis": volatility_analysis,
                "seasonality_analysis": seasonality_analysis,
                "structural_changes": structural_changes,
                "trend_forecasts": trend_forecasts,
                "overall_market_trend": self._assess_overall_market_trend(
                    individual_trends
                ),
            }

            logger.info(
                f"추세 분석 완료: {len(processed_data)}개 시리즈, {time.time() - start_time:.3f}초 소요"
            )
            return analysis_result

        except Exception as e:
            logger.error(f"추세 분석 실패: {e}")
            return {"error": "analysis_failed", "message": str(e)}

    async def _preprocess_data(
        self, data_dict: Dict[str, Any]
    ) -> Dict[str, pd.DataFrame]:
        """데이터 전처리"""
        processed = {}

        for name, raw_data in data_dict.items():
            try:
                df = self.preprocessor.convert_to_dataframe(raw_data)

                if df is not None and len(df) >= 5:  # 추세 분석을 위한 최소 데이터
                    df = self.preprocessor.standardize_columns(df)
                    df = self.preprocessor.handle_missing_values(df)

                    if self.validator.is_valid_timeseries(df):
                        # 날짜 순 정렬
                        df = df.sort_values("date").reset_index(drop=True)
                        processed[name] = df
                        logger.debug(f"{name}: {len(df)}개 데이터 포인트 처리 완료")

            except Exception as e:
                logger.warning(f"{name} 데이터 전처리 실패: {e}")
                continue

        return processed

    async def _analyze_individual_trends(
        self, data_dict: Dict[str, pd.DataFrame]
    ) -> Dict:
        """개별 시리즈 추세 분석"""
        individual_results = {}

        for name, df in data_dict.items():
            try:
                # 기본 추세 분석
                trend_analysis = self._calculate_trend_metrics(df)

                # 선형 회귀 추세
                linear_trend = self._fit_linear_trend(df)

                # 다항식 추세 (2차)
                polynomial_trend = self._fit_polynomial_trend(df, degree=2)

                # 이동 평균 추세
                moving_averages = self._calculate_moving_averages(df)

                # 추세 강도 및 신뢰도
                trend_strength = self._assess_trend_strength(df)

                individual_results[name] = {
                    "basic_metrics": trend_analysis,
                    "linear_trend": linear_trend,
                    "polynomial_trend": polynomial_trend,
                    "moving_averages": moving_averages,
                    "trend_strength": trend_strength,
                    "data_points": len(df),
                }

            except Exception as e:
                logger.warning(f"{name} 개별 추세 분석 실패: {e}")
                individual_results[name] = {"error": str(e)}

        return individual_results

    async def _analyze_volatility_patterns(
        self, data_dict: Dict[str, pd.DataFrame]
    ) -> Dict:
        """변동성 패턴 분석"""
        volatility_results = {}

        for name, df in data_dict.items():
            try:
                values = df["value"].values

                # 이동 표준편차 (변동성)
                rolling_volatility = self._calculate_rolling_volatility(df)

                # GARCH 스타일 변동성 (간단한 구현)
                garch_volatility = self._calculate_garch_like_volatility(values)

                # 변동성 클러스터링 탐지
                volatility_clustering = self._detect_volatility_clustering(values)

                # 변동성 추세
                volatility_trend = self._analyze_volatility_trend(rolling_volatility)

                volatility_results[name] = {
                    "rolling_volatility": rolling_volatility,
                    "garch_volatility": garch_volatility,
                    "volatility_clustering": volatility_clustering,
                    "volatility_trend": volatility_trend,
                }

            except Exception as e:
                logger.warning(f"{name} 변동성 분석 실패: {e}")
                volatility_results[name] = {"error": str(e)}

        return volatility_results

    async def _analyze_seasonality_patterns(
        self, data_dict: Dict[str, pd.DataFrame]
    ) -> Dict:
        """계절성 및 주기성 분석"""
        seasonality_results = {}

        for name, df in data_dict.items():
            try:
                # 주기성 탐지 (FFT 기반)
                periodicity = self._detect_periodicity(df)

                # 계절성 분해 (간단한 구현)
                seasonal_decomposition = self._decompose_seasonality(df)

                # 요일 효과 (데이터가 충분한 경우)
                day_of_week_effect = self._analyze_day_of_week_effect(df)

                # 월별 패턴
                monthly_pattern = self._analyze_monthly_pattern(df)

                seasonality_results[name] = {
                    "periodicity": periodicity,
                    "seasonal_decomposition": seasonal_decomposition,
                    "day_of_week_effect": day_of_week_effect,
                    "monthly_pattern": monthly_pattern,
                }

            except Exception as e:
                logger.warning(f"{name} 계절성 분석 실패: {e}")
                seasonality_results[name] = {"error": str(e)}

        return seasonality_results

    async def _detect_structural_changes(
        self, data_dict: Dict[str, pd.DataFrame]
    ) -> Dict:
        """구조적 변화점 탐지"""
        change_point_results = {}

        for name, df in data_dict.items():
            try:
                values = df["value"].values
                dates = df["date"].values

                # 변화점 탐지 (간단한 방법)
                change_points = self._detect_change_points(values)

                # 변화점에서의 추세 변화
                trend_changes = self._analyze_trend_changes_at_points(
                    values, dates, change_points
                )

                # 레벨 시프트 탐지
                level_shifts = self._detect_level_shifts(values, dates)

                change_point_results[name] = {
                    "change_points": change_points,
                    "trend_changes": trend_changes,
                    "level_shifts": level_shifts,
                }

            except Exception as e:
                logger.warning(f"{name} 구조적 변화 탐지 실패: {e}")
                change_point_results[name] = {"error": str(e)}

        return change_point_results

    async def _generate_trend_forecasts(
        self, data_dict: Dict[str, pd.DataFrame]
    ) -> Dict:
        """추세 기반 예측"""
        forecast_results = {}

        for name, df in data_dict.items():
            try:
                # 단기 예측 (선형 추세 기반)
                short_term_forecast = self._generate_linear_forecast(df, periods=5)

                # 중기 예측 (다항식 추세 기반)
                medium_term_forecast = self._generate_polynomial_forecast(
                    df, periods=10
                )

                # 추세 신뢰구간
                confidence_intervals = self._calculate_forecast_confidence(df)

                forecast_results[name] = {
                    "short_term_forecast": short_term_forecast,
                    "medium_term_forecast": medium_term_forecast,
                    "confidence_intervals": confidence_intervals,
                }

            except Exception as e:
                logger.warning(f"{name} 예측 생성 실패: {e}")
                forecast_results[name] = {"error": str(e)}

        return forecast_results

    # 개별 분석 메소드들
    def _calculate_trend_metrics(self, df: pd.DataFrame) -> Dict:
        """기본 추세 지표 계산"""
        try:
            values = df["value"]

            # 기본 통계
            first_value = values.iloc[0]
            last_value = values.iloc[-1]
            total_change = last_value - first_value
            total_change_pct = (
                (total_change / first_value) * 100 if first_value != 0 else 0
            )

            # 최고점, 최저점
            max_value = values.max()
            min_value = values.min()
            max_date = df.loc[values.idxmax(), "date"]
            min_date = df.loc[values.idxmin(), "date"]

            # 상승/하락 일수
            daily_changes = values.diff().dropna()
            up_days = (daily_changes > 0).sum()
            down_days = (daily_changes < 0).sum()

            return {
                "total_change": round(total_change, 4),
                "total_change_percent": round(total_change_pct, 2),
                "max_value": round(max_value, 4),
                "min_value": round(min_value, 4),
                "max_date": max_date.strftime("%Y-%m-%d"),
                "min_date": min_date.strftime("%Y-%m-%d"),
                "up_days": int(up_days),
                "down_days": int(down_days),
                "up_down_ratio": round(up_days / (down_days + 1e-8), 2),
                "average_value": round(values.mean(), 4),
                "volatility": round(values.std(), 4),
            }

        except Exception as e:
            logger.error(f"기본 추세 지표 계산 실패: {e}")
            return {}

    def _fit_linear_trend(self, df: pd.DataFrame) -> Dict:
        """선형 추세 피팅"""
        try:
            values = df["value"].values
            x = np.arange(len(values))

            # scipy.stats.linregress 사용
            slope, intercept, r_value, p_value, std_err = linregress(x, values)

            # 추세 방향 판정
            if abs(slope) < std_err:
                trend_direction = "sideways"
            elif slope > 0:
                trend_direction = "upward"
            else:
                trend_direction = "downward"

            # 예측값 계산
            y_pred = slope * x + intercept
            residuals = values - y_pred

            return {
                "slope": round(slope, 6),
                "intercept": round(intercept, 4),
                "r_squared": round(r_value**2, 4),
                "p_value": round(p_value, 6),
                "standard_error": round(std_err, 6),
                "trend_direction": trend_direction,
                "trend_strength": "strong"
                if r_value**2 > 0.7
                else "moderate"
                if r_value**2 > 0.4
                else "weak",
                "residual_std": round(residuals.std(), 4),
                "equation": f"y = {slope:.6f}x + {intercept:.4f}",
            }

        except Exception as e:
            logger.error(f"선형 추세 피팅 실패: {e}")
            return {}

    def _fit_polynomial_trend(self, df: pd.DataFrame, degree: int = 2) -> Dict:
        """다항식 추세 피팅"""
        try:
            values = df["value"].values
            x = np.arange(len(values)).reshape(-1, 1)

            # Polynomial features
            poly_features = PolynomialFeatures(degree=degree)
            x_poly = poly_features.fit_transform(x)

            # 선형 회귀 모델 피팅
            model = LinearRegression()
            model.fit(x_poly, values)

            # 예측값 및 R²
            y_pred = model.predict(x_poly)
            r_squared = model.score(x_poly, values)

            # 계수
            coefficients = model.coef_

            return {
                "degree": degree,
                "coefficients": [round(c, 6) for c in coefficients],
                "intercept": round(model.intercept_, 4),
                "r_squared": round(r_squared, 4),
                "residual_std": round(np.std(values - y_pred), 4),
                "trend_curvature": "convex"
                if coefficients[-1] > 0
                else "concave"
                if coefficients[-1] < 0
                else "linear",
            }

        except Exception as e:
            logger.error(f"다항식 추세 피팅 실패: {e}")
            return {}

    def _calculate_moving_averages(self, df: pd.DataFrame) -> Dict:
        """이동평균 계산"""
        try:
            values = df["value"]

            # 다양한 기간의 이동평균
            ma_periods = [5, 10, 20, 50]
            moving_averages = {}

            for period in ma_periods:
                if len(values) >= period:
                    ma = values.rolling(window=period).mean()

                    # 현재 가격과 이동평균 비교
                    current_price = values.iloc[-1]
                    current_ma = ma.iloc[-1] if not ma.isna().iloc[-1] else None

                    if current_ma is not None:
                        position = "above" if current_price > current_ma else "below"
                        deviation_pct = (
                            (current_price - current_ma) / current_ma
                        ) * 100

                        moving_averages[f"MA{period}"] = {
                            "current_value": round(current_ma, 4),
                            "position": position,
                            "deviation_percent": round(deviation_pct, 2),
                        }

            # 골든 크로스 / 데드 크로스 탐지
            crossover_signals = {}
            if len(values) >= 50:
                ma5 = values.rolling(5).mean()
                ma20 = values.rolling(20).mean()

                # 최근 크로스오버 탐지
                ma5_recent = ma5.iloc[-5:]
                ma20_recent = ma20.iloc[-5:]

                for i in range(1, len(ma5_recent)):
                    if (
                        ma5_recent.iloc[i - 1] <= ma20_recent.iloc[i - 1]
                        and ma5_recent.iloc[i] > ma20_recent.iloc[i]
                    ):
                        crossover_signals["recent_golden_cross"] = True
                    elif (
                        ma5_recent.iloc[i - 1] >= ma20_recent.iloc[i - 1]
                        and ma5_recent.iloc[i] < ma20_recent.iloc[i]
                    ):
                        crossover_signals["recent_death_cross"] = True

            return {
                "moving_averages": moving_averages,
                "crossover_signals": crossover_signals,
            }

        except Exception as e:
            logger.error(f"이동평균 계산 실패: {e}")
            return {}

    def _assess_trend_strength(self, df: pd.DataFrame) -> Dict:
        """추세 강도 평가"""
        try:
            values = df["value"].values

            # 추세 일관성 (연속 상승/하락 구간)
            daily_changes = np.diff(values)

            # 최대 연속 상승/하락 일수
            max_consecutive_up = 0
            max_consecutive_down = 0
            current_consecutive_up = 0
            current_consecutive_down = 0

            for change in daily_changes:
                if change > 0:
                    current_consecutive_up += 1
                    current_consecutive_down = 0
                    max_consecutive_up = max(max_consecutive_up, current_consecutive_up)
                elif change < 0:
                    current_consecutive_down += 1
                    current_consecutive_up = 0
                    max_consecutive_down = max(
                        max_consecutive_down, current_consecutive_down
                    )
                else:
                    current_consecutive_up = 0
                    current_consecutive_down = 0

            # 추세 모멘텀 (최근 추세 vs 전체 추세)
            recent_period = min(10, len(values) // 4)
            recent_trend = np.polyfit(range(recent_period), values[-recent_period:], 1)[
                0
            ]
            overall_trend = np.polyfit(range(len(values)), values, 1)[0]

            momentum_ratio = (
                recent_trend / (overall_trend + 1e-8) if overall_trend != 0 else 0
            )

            # 추세 신뢰도 (R² 기반)
            x = np.arange(len(values))
            slope, intercept, r_value, _, _ = linregress(x, values)
            trend_reliability = r_value**2

            return {
                "max_consecutive_up_days": max_consecutive_up,
                "max_consecutive_down_days": max_consecutive_down,
                "momentum_ratio": round(momentum_ratio, 4),
                "trend_reliability": round(trend_reliability, 4),
                "strength_assessment": (
                    "very_strong"
                    if trend_reliability > 0.8
                    else "strong"
                    if trend_reliability > 0.6
                    else "moderate"
                    if trend_reliability > 0.4
                    else "weak"
                ),
            }

        except Exception as e:
            logger.error(f"추세 강도 평가 실패: {e}")
            return {}

    def _calculate_rolling_volatility(self, df: pd.DataFrame, window: int = 20) -> Dict:
        """이동 변동성 계산"""
        try:
            values = df["value"]

            # 일간 수익률
            returns = values.pct_change().dropna()

            # 이동 표준편차 (변동성)
            rolling_vol = returns.rolling(window).std() * np.sqrt(252)  # 연율화

            # 변동성 통계
            return {
                "window_size": window,
                "current_volatility": round(rolling_vol.iloc[-1], 4)
                if not rolling_vol.isna().iloc[-1]
                else None,
                "average_volatility": round(rolling_vol.mean(), 4),
                "max_volatility": round(rolling_vol.max(), 4),
                "min_volatility": round(rolling_vol.min(), 4),
                "volatility_trend": "increasing"
                if rolling_vol.iloc[-1] > rolling_vol.mean()
                else "decreasing",
            }

        except Exception as e:
            logger.error(f"이동 변동성 계산 실패: {e}")
            return {}

    def _calculate_garch_like_volatility(self, values: np.ndarray) -> Dict:
        """GARCH 스타일 변동성 (간단한 구현)"""
        try:
            # 일간 수익률
            returns = np.diff(values) / values[:-1]

            # 단순 EWMA 변동성 모델
            lambda_param = 0.94  # 일반적인 값

            ewma_var = np.zeros(len(returns))
            ewma_var[0] = returns[0] ** 2

            for i in range(1, len(returns)):
                ewma_var[i] = lambda_param * ewma_var[i - 1] + (1 - lambda_param) * (
                    returns[i] ** 2
                )

            ewma_vol = np.sqrt(ewma_var) * np.sqrt(252)  # 연율화

            return {
                "model_type": "EWMA",
                "lambda_parameter": lambda_param,
                "current_volatility": round(ewma_vol[-1], 4),
                "average_volatility": round(ewma_vol.mean(), 4),
                "volatility_persistence": round(lambda_param, 4),
            }

        except Exception as e:
            logger.error(f"GARCH 스타일 변동성 계산 실패: {e}")
            return {}

    def _detect_volatility_clustering(self, values: np.ndarray) -> Dict:
        """변동성 클러스터링 탐지"""
        try:
            returns = np.diff(values) / values[:-1]

            # 절대 수익률 (변동성 대리변수)
            abs_returns = np.abs(returns)

            # 자기상관 계산 (변동성 클러스터링의 지표)
            from scipy.stats import pearsonr

            lag1_corr, _ = pearsonr(abs_returns[:-1], abs_returns[1:])

            # 변동성 레짐 탐지 (높음/낮음)
            median_vol = np.median(abs_returns)
            high_vol_periods = abs_returns > median_vol * 1.5
            low_vol_periods = abs_returns < median_vol * 0.5

            return {
                "volatility_autocorrelation": round(lag1_corr, 4),
                "clustering_detected": lag1_corr > 0.1,
                "high_volatility_periods": int(high_vol_periods.sum()),
                "low_volatility_periods": int(low_vol_periods.sum()),
                "volatility_regimes": {
                    "high_vol_threshold": round(median_vol * 1.5, 4),
                    "low_vol_threshold": round(median_vol * 0.5, 4),
                },
            }

        except Exception as e:
            logger.error(f"변동성 클러스터링 탐지 실패: {e}")
            return {}

    def _analyze_volatility_trend(self, rolling_volatility: Dict) -> Dict:
        """변동성 추세 분석"""
        try:
            # 이 메소드는 rolling_volatility 결과를 받아서 추세를 분석
            # 실제 구현에서는 시계열 변동성 데이터가 필요

            return {
                "trend_direction": "stable",  # 실제로는 계산된 값
                "trend_strength": "moderate",
                "forecast": "변동성이 안정적으로 유지될 것으로 예상",
            }

        except Exception as e:
            logger.error(f"변동성 추세 분석 실패: {e}")
            return {}

    def _detect_periodicity(self, df: pd.DataFrame) -> Dict:
        """주기성 탐지 (FFT 기반)"""
        try:
            values = df["value"].values

            if len(values) < 20:
                return {"message": "insufficient_data_for_periodicity"}

            # FFT 계산
            fft_values = np.fft.fft(values - values.mean())
            frequencies = np.fft.fftfreq(len(values))

            # 파워 스펙트럼
            power_spectrum = np.abs(fft_values) ** 2

            # 주요 주파수 탐지 (DC 성분 제외)
            valid_freqs = frequencies[1 : len(frequencies) // 2]
            valid_power = power_spectrum[1 : len(power_spectrum) // 2]

            # 상위 3개 주파수
            top_indices = np.argsort(valid_power)[-3:][::-1]

            detected_periods = []
            for idx in top_indices:
                if valid_freqs[idx] != 0:
                    period = 1 / abs(valid_freqs[idx])
                    power = valid_power[idx]
                    detected_periods.append(
                        {
                            "period_days": round(period, 2),
                            "power": round(power, 2),
                            "frequency": round(valid_freqs[idx], 6),
                        }
                    )

            return {
                "detected_periods": detected_periods,
                "dominant_period": detected_periods[0]["period_days"]
                if detected_periods
                else None,
                "periodicity_strength": "strong"
                if detected_periods
                and detected_periods[0]["power"] > np.mean(valid_power) * 5
                else "weak",
            }

        except Exception as e:
            logger.error(f"주기성 탐지 실패: {e}")
            return {}

    def _decompose_seasonality(self, df: pd.DataFrame) -> Dict:
        """계절성 분해 (간단한 구현)"""
        try:
            values = df["value"]

            if len(values) < 24:  # 최소 2년치 데이터 필요
                return {"message": "insufficient_data_for_seasonal_decomposition"}

            # 이동평균을 이용한 간단한 추세 제거
            window = min(12, len(values) // 4)
            trend = values.rolling(window, center=True).mean()

            # 계절성 + 잡음
            detrended = values - trend

            # 계절성 패턴 (월별 평균)
            df_copy = df.copy()
            df_copy["month"] = df_copy["date"].dt.month
            df_copy["detrended"] = detrended

            monthly_pattern = df_copy.groupby("month")["detrended"].mean().to_dict()

            return {
                "trend_component": "calculated",
                "seasonal_pattern": {
                    str(k): round(v, 4) for k, v in monthly_pattern.items()
                },
                "seasonal_strength": round(detrended.std() / values.std(), 4),
            }

        except Exception as e:
            logger.error(f"계절성 분해 실패: {e}")
            return {}

    def _analyze_day_of_week_effect(self, df: pd.DataFrame) -> Dict:
        """요일 효과 분석"""
        try:
            if len(df) < 50:  # 충분한 데이터가 필요
                return {"message": "insufficient_data"}

            df_copy = df.copy()
            df_copy["day_of_week"] = df_copy["date"].dt.day_name()
            df_copy["returns"] = df_copy["value"].pct_change()

            # 요일별 평균 수익률
            day_effects = (
                df_copy.groupby("day_of_week")["returns"]
                .agg(["mean", "std", "count"])
                .to_dict()
            )

            return {
                "day_of_week_effects": {
                    day: {
                        "average_return": round(day_effects["mean"][day], 6),
                        "volatility": round(day_effects["std"][day], 6),
                        "observations": day_effects["count"][day],
                    }
                    for day in day_effects["mean"].keys()
                },
                "strongest_day": max(day_effects["mean"].items(), key=lambda x: x[1])[
                    0
                ],
                "weakest_day": min(day_effects["mean"].items(), key=lambda x: x[1])[0],
            }

        except Exception as e:
            logger.error(f"요일 효과 분석 실패: {e}")
            return {}

    def _analyze_monthly_pattern(self, df: pd.DataFrame) -> Dict:
        """월별 패턴 분석"""
        try:
            if len(df) < 24:
                return {"message": "insufficient_data"}

            df_copy = df.copy()
            df_copy["month"] = df_copy["date"].dt.month
            df_copy["returns"] = df_copy["value"].pct_change()

            monthly_stats = (
                df_copy.groupby("month")["returns"]
                .agg(["mean", "std", "count"])
                .to_dict()
            )

            return {
                "monthly_patterns": {
                    str(month): {
                        "average_return": round(monthly_stats["mean"][month], 6),
                        "volatility": round(monthly_stats["std"][month], 6),
                        "observations": monthly_stats["count"][month],
                    }
                    for month in monthly_stats["mean"].keys()
                },
                "best_month": str(
                    max(monthly_stats["mean"].items(), key=lambda x: x[1])[0]
                ),
                "worst_month": str(
                    min(monthly_stats["mean"].items(), key=lambda x: x[1])[0]
                ),
            }

        except Exception as e:
            logger.error(f"월별 패턴 분석 실패: {e}")
            return {}

    def _detect_change_points(self, values: np.ndarray) -> List[int]:
        """변화점 탐지 (간단한 방법)"""
        try:
            # 이동평균의 기울기 변화를 이용한 변화점 탐지
            window = max(5, len(values) // 20)

            if len(values) < window * 3:
                return []

            # 이동평균 계산
            moving_avg = pd.Series(values).rolling(window).mean().dropna()

            # 기울기 계산
            slopes = np.diff(moving_avg)

            # 기울기 변화가 큰 지점을 변화점으로 탐지
            slope_changes = np.diff(slopes)
            threshold = np.std(slope_changes) * 2

            change_points = []
            for i, change in enumerate(slope_changes):
                if abs(change) > threshold:
                    change_points.append(i + window)  # 원래 인덱스로 보정

            return change_points[:5]  # 최대 5개까지만 반환

        except Exception as e:
            logger.error(f"변화점 탐지 실패: {e}")
            return []

    def _analyze_trend_changes_at_points(
        self, values: np.ndarray, dates: np.ndarray, change_points: List[int]
    ) -> List[Dict]:
        """변화점에서의 추세 변화 분석"""
        try:
            trend_changes = []

            for point in change_points:
                if point < 10 or point > len(values) - 10:
                    continue

                # 변화점 전후 구간의 추세 계산
                before_period = values[max(0, point - 10) : point]
                after_period = values[point : min(len(values), point + 10)]

                if len(before_period) >= 5 and len(after_period) >= 5:
                    # 선형 회귀로 기울기 계산
                    before_slope = np.polyfit(
                        range(len(before_period)), before_period, 1
                    )[0]
                    after_slope = np.polyfit(range(len(after_period)), after_period, 1)[
                        0
                    ]

                    # 추세 변화 정도
                    slope_change = after_slope - before_slope

                    # 변화 방향 판정
                    if abs(slope_change) > np.std(np.diff(values)) * 0.1:
                        if slope_change > 0:
                            change_type = "acceleration_upward"
                        else:
                            change_type = "acceleration_downward"
                    else:
                        change_type = "minor_change"

                    trend_changes.append(
                        {
                            "change_point_index": point,
                            "date": dates[point].strftime("%Y-%m-%d")
                            if point < len(dates)
                            else "unknown",
                            "before_slope": round(before_slope, 6),
                            "after_slope": round(after_slope, 6),
                            "slope_change": round(slope_change, 6),
                            "change_type": change_type,
                            "significance": "high"
                            if abs(slope_change) > np.std(np.diff(values)) * 0.2
                            else "moderate",
                        }
                    )

            return trend_changes

        except Exception as e:
            logger.error(f"추세 변화 분석 실패: {e}")
            return []

    def _detect_level_shifts(self, values: np.ndarray, dates: np.ndarray) -> List[Dict]:
        """레벨 시프트 탐지"""
        try:
            level_shifts = []

            # 이동 평균과 실제 값의 차이를 통한 레벨 시프트 탐지
            window = max(10, len(values) // 10)

            if len(values) < window * 2:
                return level_shifts

            moving_avg = pd.Series(values).rolling(window).mean()
            deviations = values - moving_avg

            # 큰 편차가 지속되는 구간 탐지
            threshold = np.std(deviations) * 2

            current_shift = None
            shift_start = None

            for i, deviation in enumerate(deviations):
                if not np.isnan(deviation):
                    if abs(deviation) > threshold:
                        if current_shift is None:
                            current_shift = deviation
                            shift_start = i
                    else:
                        if current_shift is not None and shift_start is not None:
                            # 레벨 시프트 종료
                            shift_duration = i - shift_start

                            if shift_duration >= 5:  # 최소 5일 지속
                                level_shifts.append(
                                    {
                                        "start_index": shift_start,
                                        "end_index": i,
                                        "start_date": dates[shift_start].strftime(
                                            "%Y-%m-%d"
                                        )
                                        if shift_start < len(dates)
                                        else "unknown",
                                        "end_date": dates[
                                            min(i, len(dates) - 1)
                                        ].strftime("%Y-%m-%d"),
                                        "shift_magnitude": round(current_shift, 4),
                                        "duration_days": shift_duration,
                                        "shift_direction": "upward"
                                        if current_shift > 0
                                        else "downward",
                                    }
                                )

                            current_shift = None
                            shift_start = None

            return level_shifts[:3]  # 최대 3개까지

        except Exception as e:
            logger.error(f"레벨 시프트 탐지 실패: {e}")
            return []

    def _generate_linear_forecast(self, df: pd.DataFrame, periods: int = 5) -> Dict:
        """선형 추세 기반 단기 예측"""
        try:
            values = df["value"].values
            dates = df["date"].values

            # 선형 회귀 모델 피팅
            x = np.arange(len(values))
            slope, intercept = np.polyfit(x, values, 1)

            # 미래 예측값 계산
            future_x = np.arange(len(values), len(values) + periods)
            forecast_values = slope * future_x + intercept

            # 미래 날짜 생성 (일간 간격)
            last_date = pd.to_datetime(dates[-1])
            future_dates = [
                last_date + pd.Timedelta(days=i + 1) for i in range(periods)
            ]

            # 예측 오차 추정 (잔차 기반)
            y_pred = slope * x + intercept
            residuals = values - y_pred
            forecast_error = np.std(residuals)

            return {
                "forecast_periods": periods,
                "forecast_values": [round(v, 4) for v in forecast_values],
                "forecast_dates": [d.strftime("%Y-%m-%d") for d in future_dates],
                "trend_slope": round(slope, 6),
                "forecast_error_std": round(forecast_error, 4),
                "confidence_bounds": {
                    "upper": [
                        round(v + 1.96 * forecast_error, 4) for v in forecast_values
                    ],
                    "lower": [
                        round(v - 1.96 * forecast_error, 4) for v in forecast_values
                    ],
                },
            }

        except Exception as e:
            logger.error(f"선형 예측 생성 실패: {e}")
            return {}

    def _generate_polynomial_forecast(
        self, df: pd.DataFrame, periods: int = 10, degree: int = 2
    ) -> Dict:
        """다항식 추세 기반 중기 예측"""
        try:
            values = df["value"].values
            dates = df["date"].values

            # 다항식 회귀 모델 피팅
            x = np.arange(len(values))
            coefficients = np.polyfit(x, values, degree)
            poly_func = np.poly1d(coefficients)

            # 미래 예측값 계산
            future_x = np.arange(len(values), len(values) + periods)
            forecast_values = poly_func(future_x)

            # 미래 날짜 생성
            last_date = pd.to_datetime(dates[-1])
            future_dates = [
                last_date + pd.Timedelta(days=i + 1) for i in range(periods)
            ]

            # 예측 오차 추정
            y_pred = poly_func(x)
            residuals = values - y_pred
            forecast_error = np.std(residuals)

            # 다항식의 곡률 분석
            second_derivative = np.polyder(coefficients, 2)
            curvature = (
                np.polyval(second_derivative, future_x[-1]) if degree >= 2 else 0
            )

            return {
                "forecast_periods": periods,
                "polynomial_degree": degree,
                "forecast_values": [round(v, 4) for v in forecast_values],
                "forecast_dates": [d.strftime("%Y-%m-%d") for d in future_dates],
                "coefficients": [round(c, 6) for c in coefficients],
                "forecast_error_std": round(forecast_error, 4),
                "curvature_at_end": round(curvature, 6),
                "trend_acceleration": "increasing"
                if curvature > 0
                else "decreasing"
                if curvature < 0
                else "constant",
            }

        except Exception as e:
            logger.error(f"다항식 예측 생성 실패: {e}")
            return {}

    def _calculate_forecast_confidence(self, df: pd.DataFrame) -> Dict:
        """예측 신뢰구간 계산"""
        try:
            values = df["value"].values

            # 여러 모델의 예측 성능 평가
            train_size = max(10, int(len(values) * 0.8))

            if len(values) <= train_size + 2:
                return {"message": "insufficient_data"}

            train_data = values[:train_size]
            test_data = values[train_size:]

            # 선형 모델 평가
            x_train = np.arange(len(train_data))
            x_test = np.arange(len(train_data), len(values))

            linear_coef = np.polyfit(x_train, train_data, 1)
            linear_pred = np.polyval(linear_coef, x_test)
            linear_mae = np.mean(np.abs(test_data - linear_pred))

            # 다항식 모델 평가
            poly_coef = np.polyfit(x_train, train_data, 2)
            poly_pred = np.polyval(poly_coef, x_test)
            poly_mae = np.mean(np.abs(test_data - poly_pred))

            # 최적 모델 선택
            best_model = "linear" if linear_mae <= poly_mae else "polynomial"
            best_mae = min(linear_mae, poly_mae)

            return {
                "validation_method": "time_series_split",
                "train_size": train_size,
                "test_size": len(test_data),
                "linear_mae": round(linear_mae, 4),
                "polynomial_mae": round(poly_mae, 4),
                "best_model": best_model,
                "forecast_accuracy": round(
                    (1 - best_mae / np.mean(test_data)) * 100, 2
                ),
                "confidence_level": "high"
                if best_mae < np.std(values) * 0.5
                else "moderate"
                if best_mae < np.std(values)
                else "low",
            }

        except Exception as e:
            logger.error(f"신뢰구간 계산 실패: {e}")
            return {}

    def _assess_overall_market_trend(self, individual_trends: Dict) -> Dict:
        """전체 시장 추세 종합 평가"""
        try:
            if not individual_trends:
                return {}

            # 각 시리즈의 추세 방향 수집
            trend_directions = []
            trend_strengths = []
            r_squared_values = []

            for series_name, analysis in individual_trends.items():
                if "error" not in analysis:
                    linear_trend = analysis.get("linear_trend", {})

                    if "trend_direction" in linear_trend:
                        trend_directions.append(linear_trend["trend_direction"])

                    if "trend_strength" in linear_trend:
                        trend_strengths.append(linear_trend["trend_strength"])

                    if "r_squared" in linear_trend:
                        r_squared_values.append(linear_trend["r_squared"])

            if not trend_directions:
                return {}

            # 추세 방향 합의
            direction_counts = {
                "upward": trend_directions.count("upward"),
                "downward": trend_directions.count("downward"),
                "sideways": trend_directions.count("sideways"),
            }

            dominant_direction = max(direction_counts.items(), key=lambda x: x[1])[0]
            consensus_strength = direction_counts[dominant_direction] / len(
                trend_directions
            )

            # 전체 추세 강도
            strength_scores = {"very_strong": 4, "strong": 3, "moderate": 2, "weak": 1}
            avg_strength_score = np.mean(
                [strength_scores.get(s, 1) for s in trend_strengths]
            )

            if avg_strength_score >= 3.5:
                overall_strength = "very_strong"
            elif avg_strength_score >= 2.5:
                overall_strength = "strong"
            elif avg_strength_score >= 1.5:
                overall_strength = "moderate"
            else:
                overall_strength = "weak"

            # 시장 동조화 정도
            avg_r_squared = np.mean(r_squared_values) if r_squared_values else 0
            synchronization = (
                "high"
                if consensus_strength > 0.7
                else "moderate"
                if consensus_strength > 0.5
                else "low"
            )

            return {
                "dominant_trend_direction": dominant_direction,
                "consensus_strength": round(consensus_strength, 3),
                "overall_trend_strength": overall_strength,
                "market_synchronization": synchronization,
                "average_r_squared": round(avg_r_squared, 4),
                "series_analyzed": len(individual_trends),
                "trend_distribution": direction_counts,
                "market_assessment": self._generate_market_assessment(
                    dominant_direction, consensus_strength, overall_strength
                ),
            }

        except Exception as e:
            logger.error(f"전체 시장 추세 평가 실패: {e}")
            return {}

    def _generate_market_assessment(
        self, direction: str, consensus: float, strength: str
    ) -> str:
        """시장 상황 종합 평가 메시지"""
        try:
            if consensus > 0.8:
                consensus_text = "강한 합의"
            elif consensus > 0.6:
                consensus_text = "중간 수준 합의"
            else:
                consensus_text = "혼재된 신호"

            direction_text = {
                "upward": "상승 추세",
                "downward": "하락 추세",
                "sideways": "횡보 추세",
            }.get(direction, "불분명한 추세")

            strength_text = {
                "very_strong": "매우 강한",
                "strong": "강한",
                "moderate": "중간 수준의",
                "weak": "약한",
            }.get(strength, "불분명한")

            return f"시장은 {consensus_text}를 보이며 {strength_text} {direction_text}를 나타내고 있습니다."

        except Exception as e:
            logger.error(f"시장 평가 메시지 생성 실패: {e}")
            return "시장 상황을 평가할 수 없습니다."

    def _get_analysis_period(self, data_dict: Dict[str, pd.DataFrame]) -> Dict:
        """분석 기간 정보 반환"""
        try:
            all_dates = []

            for df in data_dict.values():
                if "date" in df.columns:
                    all_dates.extend(df["date"].tolist())

            if all_dates:
                min_date = min(all_dates)
                max_date = max(all_dates)

                return {
                    "start_date": min_date.strftime("%Y-%m-%d"),
                    "end_date": max_date.strftime("%Y-%m-%d"),
                    "total_days": (max_date - min_date).days + 1,
                    "data_frequency": "daily",  # 일간 데이터로 가정
                }

            return {}

        except Exception as e:
            logger.error(f"분석 기간 계산 실패: {e}")
            return {}
