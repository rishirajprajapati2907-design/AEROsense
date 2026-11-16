"""
Unit tests for Rolling Window Anomaly Detector
"""

import unittest
import pandas as pd
import numpy as np

from backend.intelligence.rolling_detector import RollingWindowDetector
from backend.intelligence.anomaly_classifier import AnomalyCategory, AnomalySeverity


class TestRollingWindowDetector(unittest.TestCase):

    def setUp(self):
        self.detector = RollingWindowDetector(window_size=15, std_multiplier=3.0, critical_multiplier=4.0)

    def test_detects_sudden_spike_against_moving_baseline(self):
        # Gradual upward trend from 20 to 30 over 60 points with minor noise
        np.random.seed(42)
        trend = np.linspace(20, 30, 60) + np.random.normal(0, 0.2, 60)
        # Inject sudden spike at index 40
        trend[40] = 38.0  # +8 above local trend of ~26.7

        s = pd.Series(trend)
        anomalies = self.detector.detect_series(s, "temperature")

        self.assertGreater(len(anomalies), 0)
        flagged_indices = [a.row_index for a in anomalies]
        self.assertIn(40, flagged_indices)

        spike = next(a for a in anomalies if a.row_index == 40)
        self.assertEqual(spike.category, AnomalyCategory.UNUSUAL_HIGH)
        self.assertIn(spike.severity, [AnomalySeverity.WARNING, AnomalySeverity.CRITICAL])

    def test_insufficient_samples_window_warmup(self):
        # Fewer than min_periods (5) should yield no anomalies
        s = pd.Series([20.0, 20.1, 20.2])
        anomalies = self.detector.detect_series(s, "humidity")
        self.assertEqual(len(anomalies), 0)

    def test_dataframe_scanning(self):
        df = pd.DataFrame({
            "timestamp": pd.date_range("2026-10-18", periods=40, freq="min"),
            "smoke": [250.0] * 35 + [350.0] + [250.0] * 4,
        })
        anomalies = self.detector.detect_dataframe(df, ["smoke"])
        self.assertGreater(len(anomalies), 0)
        self.assertEqual(anomalies[0].sensor_name, "smoke")


if __name__ == "__main__":
    unittest.main()
