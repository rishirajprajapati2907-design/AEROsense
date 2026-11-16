"""
Unit Tests for Outlier Detection Engine
Tests IQR, Z-score, and rolling average outlier detection.
Verifies that unusual readings are flagged with indicator columns without being deleted.
"""

import unittest
from datetime import datetime, timezone
import pandas as pd
import numpy as np

from backend.processing.outlier_detector import OutlierDetector, OutlierEvent


class TestOutlierDetector(unittest.TestCase):

    def setUp(self):
        self.detector = OutlierDetector(
            z_threshold=3.0,
            z_critical_threshold=4.0,
            iqr_multiplier=1.5,
            rolling_window=10,
            rolling_std_multiplier=3.0,
        )

    def test_zscore_outlier_detection(self):
        """Test statistical Z-score detects high spike (>3 sigma)."""
        # 50 normal points around 20.0, 1 extreme outlier at 100.0
        np.random.seed(42)
        values = list(np.random.normal(loc=20.0, scale=1.0, size=50))
        values.append(100.0)  # Extreme outlier

        df = pd.DataFrame({
            "timestamp": pd.date_range("2026-01-01", periods=len(values), freq="min", tz="UTC"),
            "temperature": values,
        })

        flagged_df, events = self.detector.identify_outliers(df, sensor_columns=["temperature"], methods=["Z_SCORE"])

        # Check that rows were NOT deleted
        self.assertEqual(len(flagged_df), 51)
        # Check outlier flag column exists
        self.assertIn("is_outlier", flagged_df.columns)
        self.assertIn("outlier_z_temperature", flagged_df.columns)
        self.assertTrue(flagged_df["outlier_z_temperature"].iloc[-1])

        # Check recorded event details
        self.assertGreaterEqual(len(events), 1)
        spike_event = events[0]
        self.assertEqual(spike_event.sensor, "temperature")
        self.assertEqual(spike_event.method, "Z_SCORE")
        self.assertEqual(spike_event.value, 100.0)
        self.assertGreater(spike_event.score, 3.0)

    def test_iqr_outlier_detection(self):
        """Test IQR identifies values outside 1.5 * IQR."""
        np.random.seed(42)
        values = list(np.random.normal(loc=50.0, scale=2.0, size=40))
        values.append(200.0)  # IQR spike

        df = pd.DataFrame({
            "timestamp": pd.date_range("2026-01-01", periods=len(values), freq="min", tz="UTC"),
            "smoke": values,
        })

        flagged_df, events = self.detector.identify_outliers(df, sensor_columns=["smoke"], methods=["IQR"])

        self.assertEqual(len(flagged_df), 41)
        self.assertTrue(flagged_df["outlier_iqr_smoke"].iloc[-1])
        iqr_events = [e for e in events if e.method == "IQR"]
        self.assertGreaterEqual(len(iqr_events), 1)
        self.assertEqual(iqr_events[0].sensor, "smoke")

    def test_rolling_average_outlier_detection(self):
        """Test local sudden jump detection using rolling window deviation."""
        # Plateau of 10.0, sudden single spike to 50.0, back to 10.0
        values = [10.0] * 20 + [50.0] + [10.0] * 20
        df = pd.DataFrame({
            "timestamp": pd.date_range("2026-01-01", periods=len(values), freq="min", tz="UTC"),
            "pm25": values,
        })

        flagged_df, events = self.detector.identify_outliers(df, sensor_columns=["pm25"], methods=["ROLLING_AVG"])

        self.assertEqual(len(flagged_df), 41)
        self.assertTrue(flagged_df["outlier_rolling_pm25"].iloc[20])
        self.assertGreaterEqual(len(events), 1)

    def test_readings_are_flagged_not_deleted(self):
        """Ensure original records are preserved with all columns intact."""
        df = pd.DataFrame({
            "timestamp": pd.date_range("2026-01-01", periods=25, freq="min", tz="UTC"),
            "temperature": [20.0] * 24 + [99.0],
            "raw_reading_id": list(range(25)),
        })

        flagged_df, _ = self.detector.identify_outliers(df, sensor_columns=["temperature"])

        self.assertEqual(len(flagged_df), 25)
        self.assertEqual(flagged_df["raw_reading_id"].tolist(), list(range(25)))
        self.assertTrue(flagged_df["is_outlier"].iloc[-1])
        self.assertFalse(flagged_df["is_outlier"].iloc[0])


if __name__ == "__main__":
    unittest.main()
