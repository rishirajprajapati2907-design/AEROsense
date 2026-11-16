"""
Unit tests for Future Forecasting and Explanation Generation
"""

import unittest
from datetime import datetime
import pandas as pd
import numpy as np

from backend.intelligence.prediction.forecasting import Forecaster
from backend.intelligence.prediction.feature_engineering import TimeSeriesFeatureEngineer
from backend.intelligence.prediction.linear_regression_model import LinearRegressionForecaster


class TestForecasting(unittest.TestCase):

    def setUp(self):
        n = 60
        dates = pd.date_range("2026-10-18 12:00:00", periods=n, freq="min", tz="UTC")
        self.df = pd.DataFrame({
            "timestamp": dates,
            "temperature": [22.0 + np.sin(i * 0.1) * 2.0 for i in range(n)],
        })

        X, y, _ = TimeSeriesFeatureEngineer.build_features_and_target(self.df, "temperature")
        self.model = LinearRegressionForecaster()
        self.model.fit(X, y, target_name="temperature")

    def test_generate_future_timestamps(self):
        base_t = datetime(2026, 10, 18, 12, 0, 0)
        future_ts = Forecaster.generate_future_timestamps(base_t, steps=5, step_interval_seconds=60)

        self.assertEqual(len(future_ts), 5)
        self.assertEqual(future_ts[0], datetime(2026, 10, 18, 12, 1, 0))
        self.assertEqual(future_ts[-1], datetime(2026, 10, 18, 12, 5, 0))

    def test_recursive_forecast_generation_and_confidence_envelope(self):
        res = Forecaster.forecast_recursive(
            model_wrapper=self.model,
            recent_df=self.df,
            target_col="temperature",
            steps=10,
            val_rmse=0.25,
            step_interval_seconds=60,
        )

        self.assertTrue(res["success"])
        self.assertEqual(len(res["predictions"]), 10)
        self.assertEqual(len(res["confidence_lower"]), 10)
        self.assertEqual(len(res["confidence_upper"]), 10)

        # Upper bound must always exceed prediction, which exceeds lower bound
        for p, l, u in zip(res["predictions"], res["confidence_lower"], res["confidence_upper"]):
            self.assertGreaterEqual(u, p)
            self.assertGreaterEqual(p, l)

    def test_forecast_explanation_is_factual_and_non_clinical(self):
        exp = Forecaster.explain_forecast(
            sensor_name="temperature",
            initial_val=24.0,
            final_val=26.5,
            horizon_steps=30,
            step_interval_seconds=60,
            uncertainty_width=1.2,
        )

        self.assertIn("Temperature is projected to increase", exp)
        self.assertIn("30 minutes", exp)
        self.assertIn("confidence band", exp)
        # Verify no medical jargon
        self.assertNotIn("patient", exp.lower())
        self.assertNotIn("clinical", exp.lower())


if __name__ == "__main__":
    unittest.main()
