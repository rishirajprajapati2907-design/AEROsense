"""
AEROsense Time-Series Feature Engineering Module
Generates lag features, rolling statistics, cyclical diurnal encodings, and trend indicators
with strict causal alignment to prevent data leakage.
"""

from typing import List, Optional, Tuple, Dict, Any
import numpy as np
import pandas as pd


class TimeSeriesFeatureEngineer:
    """Extracts leak-free causal time-series features for regression models."""

    DEFAULT_LAGS = [1, 2, 3, 5, 10, 15]
    DEFAULT_ROLLING = [3, 6, 12]

    @staticmethod
    def extract_time_features(df: pd.DataFrame, timestamp_col: str = "timestamp") -> pd.DataFrame:
        """
        Extract cyclical and calendar temporal features.
        Uses sine and cosine encodings to preserve 23:00 -> 00:00 continuity.
        """
        out = pd.DataFrame(index=df.index)
        ts = pd.to_datetime(df[timestamp_col], utc=True)

        hour = ts.dt.hour
        day_of_week = ts.dt.dayofweek

        out["hour"] = hour
        out["day_of_week"] = day_of_week
        out["is_weekend"] = (day_of_week >= 5).astype(int)

        # Cyclical diurnal encoding (period = 24 hours)
        out["sin_hour"] = np.sin(2 * np.pi * hour / 24.0)
        out["cos_hour"] = np.cos(2 * np.pi * hour / 24.0)

        # Cyclical weekly encoding (period = 7 days)
        out["sin_day"] = np.sin(2 * np.pi * day_of_week / 7.0)
        out["cos_day"] = np.cos(2 * np.pi * day_of_week / 7.0)

        return out

    @staticmethod
    def build_features_and_target(
        df: pd.DataFrame,
        target_col: str,
        timestamp_col: str = "timestamp",
        lags: Optional[List[int]] = None,
        rolling_windows: Optional[List[int]] = None,
        forecast_horizon: int = 1,
        exogenous_cols: Optional[List[str]] = None,
    ) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
        """
        Construct feature matrix X and target vector y for multi-step or single-step forecasting.
        
        Causal Alignment Guarantee:
        - X at row t contains values at and prior to index t (lags t-1, t-2, etc.).
        - y at row t is the target sensor value at index (t + forecast_horizon).
        - No future information is leaked into X.
        
        Returns:
            X: DataFrame of feature vectors
            y: Series of future target values
            feature_names: List of column names in X
        """
        if df.empty or target_col not in df.columns:
            return pd.DataFrame(), pd.Series(), []

        lags = lags or TimeSeriesFeatureEngineer.DEFAULT_LAGS
        rolling_windows = rolling_windows or TimeSeriesFeatureEngineer.DEFAULT_ROLLING
        df_work = df.copy()

        feature_dfs = []

        # 1. Temporal calendar features
        time_feats = TimeSeriesFeatureEngineer.extract_time_features(df_work, timestamp_col=timestamp_col)
        feature_dfs.append(time_feats)

        # 2. Autoregressive Lag Features
        lag_df = pd.DataFrame(index=df_work.index)
        for lag in lags:
            lag_df[f"{target_col}_lag_{lag}"] = df_work[target_col].shift(lag)
        feature_dfs.append(lag_df)

        # 3. Rolling window statistics (computed strictly over past values)
        # We shift by 1 first so rolling window at index t does not include the unobserved future
        shifted_series = df_work[target_col].shift(1)
        roll_df = pd.DataFrame(index=df_work.index)
        for w in rolling_windows:
            roll_df[f"{target_col}_roll_mean_{w}"] = shifted_series.rolling(window=w, min_periods=1).mean()
            roll_df[f"{target_col}_roll_std_{w}"] = shifted_series.rolling(window=w, min_periods=2).std().fillna(0.0)
        feature_dfs.append(roll_df)

        # 4. Short-term trend momentum (difference between lag 1 and lag 2)
        trend_df = pd.DataFrame(index=df_work.index)
        trend_df[f"{target_col}_momentum_1_2"] = df_work[target_col].shift(1) - df_work[target_col].shift(2)
        trend_df[f"{target_col}_momentum_1_5"] = df_work[target_col].shift(1) - df_work[target_col].shift(5)
        feature_dfs.append(trend_df)

        # 5. Exogenous sensor features (if available)
        if exogenous_cols:
            exo_df = pd.DataFrame(index=df_work.index)
            for ex in exogenous_cols:
                if ex in df_work.columns and ex != target_col:
                    exo_df[f"{ex}_lag_1"] = df_work[ex].shift(1)
            feature_dfs.append(exo_df)

        # Combine all features
        X_all = pd.concat(feature_dfs, axis=1)

        # Build Future Target: target shifted backwards by forecast_horizon
        # y[t] = target[t + forecast_horizon]
        y_all = df_work[target_col].shift(-forecast_horizon)

        # Drop rows with NaNs caused by lags (head) and future target shift (tail)
        valid_mask = X_all.notna().all(axis=1) & y_all.notna()

        X_clean = X_all[valid_mask].copy().reset_index(drop=True)
        y_clean = y_all[valid_mask].copy().reset_index(drop=True)

        return X_clean, y_clean, list(X_clean.columns)
