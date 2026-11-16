"""
Unit tests for Rate of Change Anomaly Detector
"""

import unittest
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from backend.intelligence.rate_of_change import RateOfChangeDetector
from backend.intelligence.anomaly_classifier import AnomalyCategory, AnomalySeverity


class TestRateOfChangeDetector(unittest.TestCase):

    def setUp(self):
        self.detector = RateOfChangeDetector(
            default_rate_threshold=10.0,
            sensor_rate_thresholds={"temperature": 0.5, "smoke": 15.0},
        )

    def test_detects_sudden_step_discontinuity(self):
        # 10 readings spaced 2 seconds apart; index 5 jumps from 24.0 to 30.0 (Δ=6.0 in 2s => rate=3.0 > 0.5)
        times = [datetime(2026, 10, 18, 12, 0, 0) + timedelta(seconds=i * 2) for i in range(10)]
        values = [24.0, 24.1, 24.0, 24.2, 24.1, 30.0, 30.1, 30.0, 30.2, 30.1]

        s = pd.Series(values)
        ts = pd.Series(times)

        anomalies = self.detector.detect_series(s, "temperature", timestamps=ts)

        self.assertGreater(len(anomalies), 0)
        self.assertEqual(anomalies[0].category, AnomalyCategory.SUDDEN_VARIATION)
        self.assertEqual(anomalies[0].row_index, 5)
        self.assertEqual(anomalies[0].detected_value, 30.0)

    def test_gradual_normal_variation_not_flagged(self):
        # Temperature rises 0.1°C every 10 seconds (rate = 0.01/s << 0.5)
        times = [datetime(2026, 10, 18, 12, 0, 0) + timedelta(seconds=i * 10) for i in range(20)]
        values = [20.0 + i * 0.1 for i in range(20)]

        s = pd.Series(values)
        ts = pd.Series(times)

        anomalies = self.detector.detect_series(s, "temperature", timestamps=ts)
        self.assertEqual(len(anomalies), 0)

    def test_skips_offline_downtime_gap(self):
        # Jump occurs after a 2-day downtime (48 hours = 172800s > max_time_diff_sec)
        t1 = datetime(2026, 10, 18, 12, 0, 0)
        t2 = datetime(2026, 10, 20, 12, 0, 0)

        s = pd.Series([20.0, 35.0])
        ts = pd.Series([t1, t2])

        anomalies = self.detector.detect_series(s, "temperature", timestamps=ts)
        self.assertEqual(len(anomalies), 0)


if __name__ == "__main__":
    unittest.main()
