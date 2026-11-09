"""
AEROsense Time-Series Data Preparation Module
Handles chronological sorting, timestamp deduplication, missing value imputation,
sensor dataset extraction, sampling frequency verification, and chronological splitting.
"""

from typing import Dict, Any, Tuple, Optional, List
import pandas as pd
import numpy as np


class TimeSeriesDataPreparer:
    """Prepares and validates sensor time-series datasets for predictive modeling."""

    MIN_REQUIRED_SAMPLES = 100
    MIN_VARIANCE_THRESHOLD = 1e-4

    @staticmethod
    def assess_sensor_data_sufficiency(
        series: pd.Series,
        sensor_name: str,
    ) -> Dict[str, Any]:
        """
        Assess whether an individual sensor channel has sufficient valid,
        non-saturated historical readings for machine learning forecasting.
        """
        valid_s = series.dropna()
        total_count = len(series)
        valid_count = len(valid_s)
        missing_count = total_count - valid_count

        if valid_count < TimeSeriesDataPreparer.MIN_REQUIRED_SAMPLES:
            return {
                "sensor_name": sensor_name,
                "is_sufficient": False,
                "total_records": total_count,
                "valid_records": valid_count,
                "missing_records": missing_count,
                "variance": 0.0,
                "reason": f"Insufficient sample size ({valid_count} < {TimeSeriesDataPreparer.MIN_REQUIRED_SAMPLES}).",
            }

        variance = float(valid_s.var())
        unique_values_count = valid_s.nunique()

        # Check for sensor saturation or flatlined readings (e.g., PM2.5 ceiling at 560.9)
        most_frequent_pct = (valid_s.value_counts().iloc[0] / valid_count) if valid_count > 0 else 0.0

        if variance < TimeSeriesDataPreparer.MIN_VARIANCE_THRESHOLD or unique_values_count <= 2:
            return {
                "sensor_name": sensor_name,
                "is_sufficient": False,
                "total_records": total_count,
                "valid_records": valid_count,
                "missing_records": missing_count,
                "variance": round(variance, 6),
                "reason": "Sensor signal exhibits near-zero variance or flatlined output.",
            }

        if most_frequent_pct > 0.95:
            top_val = valid_s.value_counts().index[0]
            return {
                "sensor_name": sensor_name,
                "is_sufficient": False,
                "total_records": total_count,
                "valid_records": valid_count,
                "missing_records": missing_count,
                "variance": round(variance, 4),
                "reason": (
                    f"Sensor saturated: {most_frequent_pct*100:.1f}% of recordings are pegged at "
                    f"constant value ({top_val}). Unsuitable for regression forecasting."
                ),
            }

        return {
            "sensor_name": sensor_name,
            "is_sufficient": True,
            "total_records": total_count,
            "valid_records": valid_count,
            "missing_records": missing_count,
            "variance": round(variance, 4),
            "reason": f"Sufficient variance ({variance:.4f}) and sample size ({valid_count} records).",
        }

    @staticmethod
    def prepare_dataset(
        df: pd.DataFrame,
        sensor_column: str,
        timestamp_col: str = "timestamp",
        max_fill_gap: int = 5,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Extract and prepare a clean, chronologically sorted univariate/multivariate sensor dataset.
        Returns (clean_df, quality_audit).
        """
        if df.empty or sensor_column not in df.columns:
            return pd.DataFrame(), {"success": False, "error": f"Column '{sensor_column}' not found in DataFrame."}

        # Select timestamp and target column
        sub_df = df[[timestamp_col, sensor_column]].copy()

        # Ensure datetime format
        if not pd.api.types.is_datetime64_any_dtype(sub_df[timestamp_col]):
            sub_df[timestamp_col] = pd.to_datetime(sub_df[timestamp_col], errors="coerce", utc=True)

        sub_df = sub_df.dropna(subset=[timestamp_col])
        sub_df = sub_df.sort_values(timestamp_col).reset_index(drop=True)

        # Deduplicate timestamps by averaging duplicates
        if sub_df[timestamp_col].duplicated().any():
            sub_df = sub_df.groupby(timestamp_col)[sensor_column].mean().reset_index()

        # Assess sufficiency prior to extensive imputation
        sufficiency = TimeSeriesDataPreparer.assess_sensor_data_sufficiency(sub_df[sensor_column], sensor_column)
        if not sufficiency["is_sufficient"]:
            return sub_df, {
                "success": False,
                "sufficiency": sufficiency,
                "message": sufficiency["reason"],
            }

        # Impute small gaps using forward fill (causal, no future lookahead)
        initial_missing = int(sub_df[sensor_column].isna().sum())
        sub_df[sensor_column] = sub_df[sensor_column].ffill(limit=max_fill_gap).bfill(limit=max_fill_gap)

        # Drop any remaining unfillable NaNs
        final_df = sub_df.dropna(subset=[sensor_column]).reset_index(drop=True)

        audit = {
            "success": True,
            "sensor_column": sensor_column,
            "initial_rows": len(df),
            "clean_rows": len(final_df),
            "initial_missing": initial_missing,
            "start_time": str(final_df[timestamp_col].min()),
            "end_time": str(final_df[timestamp_col].max()),
            "sufficiency": sufficiency,
        }

        return final_df, audit

    @staticmethod
    def chronological_split(
        df: pd.DataFrame,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Strict chronological train-validation-test split preventing data leakage.
        Guarantees that train < validation < test in time.
        """
        n = len(df)
        if n == 0:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        # Normalize ratios if they don't sum to 1
        total_r = train_ratio + val_ratio + test_ratio
        r_tr = train_ratio / total_r
        r_val = val_ratio / total_r

        train_end = int(n * r_tr)
        val_end = int(n * (r_tr + r_val))

        train_df = df.iloc[:train_end].copy().reset_index(drop=True)
        val_df = df.iloc[train_end:val_end].copy().reset_index(drop=True)
        test_df = df.iloc[val_end:].copy().reset_index(drop=True)

        return train_df, val_df, test_df
