"""
Unit tests for Time-Series Feature Engineering and Data Leakage Prevention
"""

import unittest
import pandas as pd
import numpy as np

from backend.intelligence.prediction.feature_engineering import TimeSeriesFeatureEngineer


class TestTimeSeriesFeatureEngineering(unittest.TestCase):

    def setUp(self):
        n = 50
        dates = pd.date_range("2026-10-18 10:00:00", periods=n, freq="min", tz="UTC")
        self.df = pd.DataFrame({
            "timestamp": dates,
            "temperature": [20.0 + i * 0.5 for i in range(n)],
            "humidity": [50.0 - i * 0.2 for i in range(n)],
        })

    def test_time_features_cyclical_bounds(self):
        time_feats = TimeSeriesFeatureEngineer.extract_time_features(self.df)
        self.assertIn("sin_hour", time_feats.columns)
        self.assertIn("cos_hour", time_feats.columns)
        # Sin and cos must strictly remain between -1 and 1
        self.assertTrue((time_feats["sin_hour"] >= -1.0).all() and (time_feats["sin_hour"] <= 1.0).all())
        self.assertTrue((time_feats["cos_hour"] >= -1.0).all() and (time_feats["cos_hour"] <= 1.0).all())

    def test_lag_and_rolling_feature_generation(self):
        X, y, feats = TimeSeriesFeatureEngineer.build_features_and_target(
            self.df, target_col="temperature", forecast_horizon=1
        )

        self.assertFalse(X.empty)
        self.assertFalse(y.empty)
        self.assertEqual(len(X), len(y))

        # Check expected feature columns
        self.assertIn("temperature_lag_1", X.columns)
        self.assertIn("temperature_roll_mean_3", X.columns)
        self.assertIn("temperature_momentum_1_2", X.columns)

    def test_prevent_future_data_leakage(self):
        """
        Verify that mutating a future row in the raw data DOES NOT change the
        feature vector for an earlier point in time.
        """
        df_copy1 = self.df.copy()
        df_copy2 = self.df.copy()

        # Modify values at index 40
        df_copy2.loc[40, "temperature"] = 999.0

        X1, _, _ = TimeSeriesFeatureEngineer.build_features_and_target(df_copy1, "temperature", forecast_horizon=1)
        X2, _, _ = TimeSeriesFeatureEngineer.build_features_and_target(df_copy2, "temperature", forecast_horizon=1)

        # For index 10 (which is well before index 40), all features must be IDENTICAL
        row1_idx10 = X1.iloc[10].to_dict()
        row2_idx10 = X2.iloc[10].to_dict()

        for k in row1_idx10:
            self.assertAlmostEqual(row1_idx10[k], row2_idx10[k], places=5, msg=f"Leakage detected in feature {k}!")


if __name__ == "__main__":
    unittest.main()
