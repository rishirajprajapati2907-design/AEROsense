"""
Unit tests for Linear Regression, Random Forest, ARIMA Training and Model Management
"""

import unittest
import tempfile
import shutil
import pandas as pd
import numpy as np

from backend.intelligence.prediction.feature_engineering import TimeSeriesFeatureEngineer
from backend.intelligence.prediction.linear_regression_model import LinearRegressionForecaster
from backend.intelligence.prediction.random_forest_model import RandomForestForecaster
from backend.intelligence.prediction.arima_model import ARIMAForecaster
from backend.intelligence.prediction.model_manager import ModelManager


class TestModelTrainingAndManagement(unittest.TestCase):

    def setUp(self):
        np.random.seed(42)
        n = 80
        dates = pd.date_range("2026-10-18", periods=n, freq="min", tz="UTC")
        self.df = pd.DataFrame({
            "timestamp": dates,
            "temperature": 24.0 + np.sin(np.linspace(0, 4 * np.pi, n)) * 2.0 + np.random.normal(0, 0.1, n),
        })

        self.X, self.y, self.feat_names = TimeSeriesFeatureEngineer.build_features_and_target(
            self.df, target_col="temperature", forecast_horizon=1
        )

        self.temp_dir = tempfile.mkdtemp()
        self.manager = ModelManager(models_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_linear_regression_training_and_coefficients(self):
        model = LinearRegressionForecaster()
        model.fit(self.X, self.y, target_name="temperature")
        self.assertTrue(model.is_fitted)

        preds = model.predict(self.X)
        self.assertEqual(len(preds), len(self.y))
        coefs = model.get_coefficients()
        self.assertGreater(len(coefs), 0)

    def test_random_forest_training_and_importances(self):
        model = RandomForestForecaster(n_estimators=20, max_depth=5, random_state=42)
        model.fit(self.X, self.y, target_name="temperature")
        self.assertTrue(model.is_fitted)

        preds = model.predict(self.X)
        self.assertEqual(len(preds), len(self.y))
        importances = model.get_feature_importances()
        self.assertGreater(len(importances), 0)
        # Sum of importances should approximately equal 1.0
        self.assertAlmostEqual(sum(importances.values()), 1.0, places=3)

    def test_arima_forecasting_with_confidence_bounds(self):
        model = ARIMAForecaster(order=(1, 1, 0))
        model.fit(self.df["temperature"], target_name="temperature")
        self.assertTrue(model.is_fitted)

        preds, lower, upper = model.forecast(steps=10)
        self.assertEqual(len(preds), 10)
        self.assertEqual(len(lower), 10)
        self.assertEqual(len(upper), 10)
        # Verify upper bound > prediction > lower bound
        self.assertTrue((upper >= preds).all())
        self.assertTrue((preds >= lower).all())

    def test_model_manager_save_and_load(self):
        rf_model = RandomForestForecaster(n_estimators=10, max_depth=3, random_state=42)
        rf_model.fit(self.X, self.y, target_name="temperature")

        # Save model
        saved_path = self.manager.save_model(
            model_artifact=rf_model,
            sensor_name="temperature",
            model_type="RandomForest",
            version="v1.0",
            evaluation_metrics={"rmse": 0.42, "r2": 0.95},
            sample_count=len(self.X),
        )
        self.assertTrue(self.manager.is_model_available("temperature", "RandomForest", "v1.0"))

        # Load model and verify predictions match
        loaded_model = self.manager.load_model("temperature", "RandomForest", "v1.0")
        self.assertIsNotNone(loaded_model)
        original_preds = rf_model.predict(self.X)
        loaded_preds = loaded_model.predict(self.X)
        np.testing.assert_array_almost_equal(original_preds, loaded_preds)

        # Verify metadata
        meta = self.manager.load_metadata("temperature", "RandomForest", "v1.0")
        self.assertEqual(meta["sensor_name"], "temperature")
        self.assertEqual(meta["metrics"]["rmse"], 0.42)


if __name__ == "__main__":
    unittest.main()
