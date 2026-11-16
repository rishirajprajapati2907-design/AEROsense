"""
Unit tests for IQR Anomaly Detector
"""

import unittest
import pandas as pd
import numpy as np

from backend.intelligence.iqr_detector import IQRDetector
from backend.intelligence.anomaly_classifier import AnomalyCategory, AnomalySeverity


class TestIQRDetector(unittest.TestCase):

    def setUp(self):
        self.detector = IQRDetector(multiplier=1.5, extreme_multiplier=3.0)

    def test_detects_tukey_fence_outliers(self):
        # Distribution with q1=40, q3=60, iqr=20. Upper fence = 90, Lower fence = 10
        data = [40.0] * 25 + [50.0] * 50 + [60.0] * 25
        data.append(150.0)  # High outlier (>90)
        data.append(5.0)    # Low outlier (<10)

        s = pd.Series(data)
        anomalies = self.detector.detect_series(s, "smoke")

        self.assertGreaterEqual(len(anomalies), 2)
        categories = [a.category for a in anomalies]
        self.assertIn(AnomalyCategory.UNUSUAL_HIGH, categories)
        self.assertIn(AnomalyCategory.UNUSUAL_LOW, categories)

    def test_extreme_multiplier_assigns_critical_severity(self):
        # q1=12, q3=18, iqr=6. Upper fence = 27, Extreme fence = 36.
        data = [10.0, 12.0, 15.0, 18.0, 20.0] * 10
        data.append(30.0)   # Warning (between 27 and 36)
        data.append(100.0)  # Critical (> 36)

        s = pd.Series(data)
        anomalies = self.detector.detect_series(s, "carbon_monoxide")

        warning_anom = [a for a in anomalies if a.detected_value == 30.0]
        critical_anom = [a for a in anomalies if a.detected_value == 100.0]

        self.assertEqual(len(warning_anom), 1)
        self.assertEqual(warning_anom[0].severity, AnomalySeverity.WARNING)

        self.assertEqual(len(critical_anom), 1)
        self.assertEqual(critical_anom[0].severity, AnomalySeverity.CRITICAL)

    def test_near_zero_iqr_handling(self):
        # Completely constant data (std = 0)
        s = pd.Series([560.9] * 50)
        anomalies = self.detector.detect_series(s, "pm25")
        self.assertEqual(len(anomalies), 0)

    def test_dataframe_multi_sensor_detection(self):
        df = pd.DataFrame({
            "timestamp": pd.date_range("2026-10-18", periods=41, freq="min"),
            "temperature": [20.0] * 10 + [25.0] * 20 + [30.0] * 10 + [65.0],
            "humidity": [40.0] * 10 + [50.0] * 20 + [60.0] * 10 + [5.0],
        })
        anomalies = self.detector.detect_dataframe(df, ["temperature", "humidity"])
        sensors_flagged = set(a.sensor_name for a in anomalies)
        self.assertIn("temperature", sensors_flagged)
        self.assertIn("humidity", sensors_flagged)


if __name__ == "__main__":
    unittest.main()
