import logging
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """데이터 전처리 유틸리티"""

    def convert_to_dataframe(self, raw_data: Any) -> Optional[pd.DataFrame]:
        """원시 데이터를 DataFrame으로 변환"""
        try:
            if isinstance(raw_data, list):
                if not raw_data:
                    return None

                # 리스트의 첫 번째 요소로 구조 판단
                first_item = raw_data[0]

                if isinstance(first_item, dict):
                    # 딕셔너리 리스트인 경우
                    df = pd.DataFrame(raw_data)
                else:
                    # 단순 값 리스트인 경우 (인덱스를 날짜로 가정)
                    df = pd.DataFrame(
                        {
                            "date": pd.date_range(
                                start="2024-01-01", periods=len(raw_data)
                            ),
                            "value": raw_data,
                        }
                    )

                return df

            elif isinstance(raw_data, dict):
                # 딕셔너리인 경우 DataFrame으로 변환 시도
                df = pd.DataFrame(raw_data)
                return df

            elif isinstance(raw_data, pd.DataFrame):
                # 이미 DataFrame인 경우
                return raw_data.copy()

            else:
                logger.warning(f"지원하지 않는 데이터 타입: {type(raw_data)}")
                return None

        except Exception as e:
            logger.error(f"DataFrame 변환 실패: {e}")
            return None

    def standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """컬럼명 표준화 (date, value)"""
        df_copy = df.copy()

        # 날짜 컬럼 찾기
        date_columns = [
            col
            for col in df_copy.columns
            if any(
                keyword in col.lower()
                for keyword in ["date", "time", "timestamp", "일자", "날짜"]
            )
        ]

        # 값 컬럼 찾기
        value_columns = [
            col
            for col in df_copy.columns
            if any(
                keyword in col.lower()
                for keyword in [
                    "value",
                    "price",
                    "amount",
                    "volume",
                    "가격",
                    "값",
                    "금액",
                ]
            )
        ]

        # 숫자 컬럼 찾기 (값 컬럼이 명확하지 않은 경우)
        if not value_columns:
            numeric_columns = df_copy.select_dtypes(
                include=[np.number]
            ).columns.tolist()
            if numeric_columns:
                value_columns = [numeric_columns[0]]  # 첫 번째 숫자 컬럼 사용

        # 표준 컬럼명으로 변경
        if date_columns:
            df_copy = df_copy.rename(columns={date_columns[0]: "date"})

        if value_columns:
            df_copy = df_copy.rename(columns={value_columns[0]: "value"})

        # date 컬럼을 datetime으로 변환
        if "date" in df_copy.columns:
            df_copy["date"] = pd.to_datetime(df_copy["date"], errors="coerce")

        # value 컬럼을 숫자로 변환
        if "value" in df_copy.columns:
            df_copy["value"] = pd.to_numeric(df_copy["value"], errors="coerce")

        # 필수 컬럼이 없는 경우 기본값 생성
        if "date" not in df_copy.columns:
            df_copy["date"] = pd.date_range(start="2024-01-01", periods=len(df_copy))

        if "value" not in df_copy.columns and len(df_copy.columns) > 0:
            # 첫 번째 숫자 컬럼을 value로 사용
            numeric_cols = df_copy.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                df_copy["value"] = df_copy[numeric_cols[0]]

        return df_copy[["date", "value"]].copy()

    def handle_missing_values(
        self, df: pd.DataFrame, method: str = "forward_fill"
    ) -> pd.DataFrame:
        """결측값 처리"""
        df_copy = df.copy()

        if method == "forward_fill":
            df_copy["value"] = df_copy["value"].fillna(method="ffill")
        elif method == "backward_fill":
            df_copy["value"] = df_copy["value"].fillna(method="bfill")
        elif method == "interpolate":
            df_copy["value"] = df_copy["value"].interpolate()
        elif method == "drop":
            df_copy = df_copy.dropna()

        # 여전히 NaN이 있으면 제거
        df_copy = df_copy.dropna()

        return df_copy


class StatisticalValidator:
    """통계적 검증 유틸리티"""

    def is_valid_timeseries(self, df: pd.DataFrame, min_points: int = 3) -> bool:
        """시계열 데이터 유효성 검증"""
        try:
            # 기본 구조 검증
            if df is None or len(df) < min_points:
                return False

            # 필수 컬럼 존재 여부
            if "date" not in df.columns or "value" not in df.columns:
                return False

            # 값의 유효성 검증
            if df["value"].isna().all():
                return False

            # 날짜의 유효성 검증
            if df["date"].isna().all():
                return False

            # 변동성 검증 (모든 값이 동일하지 않아야 함)
            if df["value"].nunique() <= 1:
                logger.warning("모든 값이 동일하여 분석이 제한적일 수 있습니다.")

            return True

        except Exception as e:
            logger.error(f"시계열 유효성 검증 실패: {e}")
            return False

    def detect_outliers(
        self, values: pd.Series, method: str = "iqr", threshold: float = 1.5
    ) -> pd.Series:
        """이상치 탐지"""
        try:
            if method == "iqr":
                Q1 = values.quantile(0.25)
                Q3 = values.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                outliers = (values < lower_bound) | (values > upper_bound)

            elif method == "zscore":
                z_scores = np.abs((values - values.mean()) / values.std())
                outliers = z_scores > threshold

            else:
                outliers = pd.Series([False] * len(values), index=values.index)

            return outliers

        except Exception as e:
            logger.error(f"이상치 탐지 실패: {e}")
            return pd.Series([False] * len(values), index=values.index)

    def assess_data_quality(self, df: pd.DataFrame) -> Dict:
        """데이터 품질 평가"""
        try:
            quality_report = {
                "total_records": len(df),
                "missing_values": {
                    "date": df["date"].isna().sum(),
                    "value": df["value"].isna().sum(),
                },
                "duplicate_dates": df["date"].duplicated().sum(),
                "value_statistics": {
                    "mean": df["value"].mean(),
                    "std": df["value"].std(),
                    "min": df["value"].min(),
                    "max": df["value"].max(),
                    "unique_values": df["value"].nunique(),
                },
                "date_range": {
                    "start": df["date"].min(),
                    "end": df["date"].max(),
                    "days": (df["date"].max() - df["date"].min()).days,
                },
            }

            # 이상치 탐지
            outliers = self.detect_outliers(df["value"])
            quality_report["outliers"] = {
                "count": outliers.sum(),
                "percentage": (outliers.sum() / len(df)) * 100,
            }

            # 데이터 품질 점수 (0-100)
            quality_score = 100

            # 결측값에 따른 감점
            missing_rate = (quality_report["missing_values"]["value"] / len(df)) * 100
            quality_score -= missing_rate * 2

            # 이상치에 따른 감점
            outlier_rate = quality_report["outliers"]["percentage"]
            quality_score -= min(outlier_rate * 0.5, 20)  # 최대 20점 감점

            # 중복 날짜에 따른 감점
            duplicate_rate = (quality_report["duplicate_dates"] / len(df)) * 100
            quality_score -= duplicate_rate

            quality_report["quality_score"] = max(0, quality_score)

            return quality_report

        except Exception as e:
            logger.error(f"데이터 품질 평가 실패: {e}")
            return {"error": str(e)}
