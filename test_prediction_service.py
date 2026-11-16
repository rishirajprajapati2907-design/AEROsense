"""
Unit tests for Prediction Service and SQLite Prediction Database Integration
"""

import unittest
import tempfile
import shutil
import os
import pandas as pd
import numpy as np

from backend.database.db_connection import DatabaseConnectionManager
from backend.database.db_initializer import initialize_database
from backend.services.prediction_service import PredictionService


class TestPredictionService(unittest.TestCase):

    def setUp(self):
        # Create an isolated temporary SQLite database and model directory
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_predictions.db")
        self.models_dir = os.path.join(self.temp_dir, "models")
        initialize_database(self.db_path, seed_metadata=True)

        self.db_manager = DatabaseConnectionManager(db_path=self.db_path)
        self.service = PredictionService(db_manager=self.db_manager, models_dir=self.models_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _generate_sample_sensor_df(self) -> pd.DataFrame:
        np.random.seed(42)
        n = 150
        dates = pd.date_range("2026-10-18 00:00:00", periods=n, freq="min", tz="UTC")
        return pd.DataFrame({
            "timestamp": dates,
            "temperature": 24.0 + np.sin(np.linspace(0, 6 * np.pi, n)) * 2.5 + np.random.normal(0, 0.1, n),
            "humidity": 55.0 - np.sin(np.linspace(0, 6 * np.pi, n)) * 10.0 + np.random.normal(0, 0.2, n),
            "pm25": [560.9] * n,  # Saturated sensor
            "source": ["historical_excel"] * n,
        })

    def test_train_and_evaluate_sensor_models(self):
        df = self._generate_sample_sensor_df()
        eval_res = self.service.train_and_evaluate_sensor_models("temperature", df=df)

        self.assertTrue(eval_res["success"])
        self.assertTrue(eval_res["is_sufficient"])
        self.assertIn("LinearRegression", eval_res["model_evaluations"])
        self.assertIn("RandomForest", eval_res["model_evaluations"])
        self.assertIn("ARIMA", eval_res["model_evaluations"])
        self.assertIsNotNone(eval_res["best_model"])

    def test_saturated_sensor_handled_without_fake_model(self):
        df = self._generate_sample_sensor_df()
        eval_res = self.service.train_and_evaluate_sensor_models("pm25", df=df)

        self.assertFalse(eval_res["success"])
        self.assertFalse(eval_res["is_sufficient"])
        reason_lower = eval_res["reason"].lower()
        self.assertTrue("saturated" in reason_lower or "variance" in reason_lower or "flatlined" in reason_lower)

    def test_forecast_generation_and_persistence(self):
        df = self._generate_sample_sensor_df()
        # Seed sensor repo with data
        self.service.sensor_repo.bulk_insert_readings(df, source="historical_excel")

        forecast = self.service.generate_forecast(
            sensor_name="temperature",
            horizon="15m",
            persist=True,
        )

        self.assertTrue(forecast["success"])
        self.assertEqual(len(forecast["predictions"]), 15)

        # Verify predictions persisted into SQLite
        count_in_db = self.service.pred_repo.get_prediction_count(sensor_name="temperature")
        self.assertEqual(count_in_db, 15)

    def test_prediction_duplicate_prevention(self):
        df = self._generate_sample_sensor_df()
        self.service.sensor_repo.bulk_insert_readings(df, source="historical_excel")

        # First forecast run
        self.service.generate_forecast("temperature", horizon="15m", persist=True)
        count_1 = self.service.pred_repo.get_prediction_count(sensor_name="temperature")

        # Second forecast run for identical horizon
        self.service.generate_forecast("temperature", horizon="15m", persist=True)
        count_2 = self.service.pred_repo.get_prediction_count(sensor_name="temperature")

        # Should not duplicate existing predictions
        self.assertEqual(count_1, count_2)


if __name__ == "__main__":
    unittest.main()
