"""
Unit tests for AEROsense Anomaly Service and Database Integration
"""

import unittest
import tempfile
import os
import pandas as pd
import numpy as np

from backend.database.db_connection import DatabaseConnectionManager
from backend.database.db_initializer import initialize_database
from backend.services.anomaly_service import AnomalyService
from backend.intelligence.anomaly_detector import AnomalyDetector


class TestAnomalyService(unittest.TestCase):

    def setUp(self):
        # Create an isolated temporary SQLite database for service testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_anomalies.db")
        initialize_database(self.db_path, seed_metadata=True)

        self.db_manager = DatabaseConnectionManager(db_path=self.db_path)
        self.service = AnomalyService(db_manager=self.db_manager)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def _generate_sample_sensor_df(self) -> pd.DataFrame:
        np.random.seed(42)
        n = 100
        dates = pd.date_range("2026-10-18 00:00:00", periods=n, freq="min", tz="UTC")
        temp = np.random.normal(24.0, 0.5, n)
        temp[10] = 35.0  # Z-score outlier
        temp[20] = 5.0   # Low outlier

        smoke = np.random.normal(250.0, 5.0, n)
        smoke[40] = 350.0 # High outlier

        return pd.DataFrame({
            "timestamp": dates,
            "temperature": temp,
            "humidity": np.random.normal(50.0, 2.0, n),
            "smoke": smoke,
            "carbon_monoxide": np.random.normal(300.0, 10.0, n),
            "ammonia": np.random.normal(200.0, 5.0, n),
            "nitrogen_oxides": np.random.normal(150.0, 5.0, n),
            "pm25": [560.9] * n,
            "source": ["test_sample"] * n,
        })

    def test_pipeline_execution_and_persistence(self):
        df = self._generate_sample_sensor_df()
        detected = self.service.run_detection_pipeline(df=df, persist=True)

        self.assertGreater(len(detected), 0)
        total_in_db = self.service.repository.get_anomaly_count()
        self.assertGreater(total_in_db, 0)

    def test_duplicate_prevention_on_rerun(self):
        df = self._generate_sample_sensor_df()

        # First run
        self.service.run_detection_pipeline(df=df, persist=True)
        count_first_run = self.service.repository.get_anomaly_count()

        # Second run with exact same data
        self.service.run_detection_pipeline(df=df, persist=True)
        count_second_run = self.service.repository.get_anomaly_count()

        # The count must NOT increase due to duplicate prevention
        self.assertEqual(count_first_run, count_second_run)

    def test_anomaly_summary_metrics(self):
        df = self._generate_sample_sensor_df()
        self.service.run_detection_pipeline(df=df, persist=True)

        summary = self.service.get_anomaly_summary()
        self.assertIn("total_anomalies", summary)
        self.assertIn("by_sensor", summary)
        self.assertIn("by_method", summary)
        self.assertIn("by_severity", summary)
        self.assertGreater(summary["total_anomalies"], 0)

    def test_anomalies_dataframe_formatting(self):
        df = self._generate_sample_sensor_df()
        self.service.run_detection_pipeline(df=df, persist=True)

        anom_df = self.service.get_anomalies_dataframe(limit=50)
        self.assertFalse(anom_df.empty)
        required_cols = {"timestamp", "sensor", "field", "value", "unit", "severity", "method", "reason"}
        self.assertTrue(required_cols.issubset(set(anom_df.columns)))


if __name__ == "__main__":
    unittest.main()
