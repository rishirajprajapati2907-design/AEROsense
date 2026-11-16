"""
Unit tests for Isolation Forest Multivariable Anomaly Detector
"""

import unittest
import pandas as pd
import numpy as np

from backend.intelligence.isolation_forest import IsolationForestDetector
from backend.intelligence.anomaly_classifier import AnomalyCategory, AnomalySeverity


class TestIsolationForestDetector(unittest.TestCase):

    def setUp(self):
        self.detector = IsolationForestDetector(
            contamination=0.03,
            n_estimators=50,
            random_state=42,
            min_samples=20,
        )

    def test_detects_multivariate_outliers(self):
        # 100 observations of correlated temperature and humidity
        np.random.seed(42)
        temp = np.random.normal(25.0, 1.0, 100)
        humidity = 50.0 - (temp - 25.0) * 2.0 + np.random.normal(0, 0.5, 100)
        smoke = np.random.normal(250.0, 5.0, 100)

        # Inject 2 multivariate anomalies: high smoke + high temperature
        temp[15] = 38.0
        smoke[15] = 450.0

        temp[85] = 37.0
        humidity[85] = 85.0  # high temp AND high humidity is abnormal in this joint distribution

        df = pd.DataFrame({
            "timestamp": pd.date_range("2026-10-18", periods=100, freq="min"),
            "temperature": temp,
            "humidity": humidity,
            "smoke": smoke,
        })

        anomalies = self.detector.detect_multivariate(
            df,
            sensor_columns=["temperature", "humidity", "smoke"],
        )

        self.assertGreater(len(anomalies), 0)
        flagged_indices = [a.row_index for a in anomalies]
        # At least one of the injected anomalies should be identified
        self.assertTrue(15 in flagged_indices or 85 in flagged_indices)

        for anom in anomalies:
            self.assertEqual(anom.category, AnomalyCategory.MULTIVARIABLE_PATTERN)
            self.assertIn("Leading contributor", anom.explanation)

    def test_missing_values_handled_gracefully(self):
        # DataFrame containing sporadic NaN values
        np.random.seed(42)
        df = pd.DataFrame({
            "timestamp": pd.date_range("2026-10-18", periods=50, freq="min"),
            "temperature": [25.0] * 48 + [None, 45.0],
            "humidity": [50.0] * 25 + [None] * 5 + [50.0] * 20,
            "smoke": [250.0] * 50,
        })

        anomalies = self.detector.detect_multivariate(
            df,
            sensor_columns=["temperature", "humidity", "smoke"],
        )
        self.assertIsInstance(anomalies, list)

    def test_deterministic_reproducibility(self):
        np.random.seed(42)
        df = pd.DataFrame({
            "temperature": np.random.normal(25.0, 1.0, 60),
            "humidity": np.random.normal(50.0, 2.0, 60),
        })

        d1 = IsolationForestDetector(contamination=0.05, random_state=42)
        d2 = IsolationForestDetector(contamination=0.05, random_state=42)

        res1 = [a.row_index for a in d1.detect_multivariate(df, ["temperature", "humidity"])]
        res2 = [a.row_index for a in d2.detect_multivariate(df, ["temperature", "humidity"])]

        self.assertEqual(res1, res2)


if __name__ == "__main__":
    unittest.main()
