"""
Unit tests for AEROsense Descriptive Analytics Module.
Verifies sample moments, percentiles, missingness audits, and edge-case handling.
"""

import unittest
import numpy as np
import pandas as pd

from backend.analytics.descriptive_analytics import (
    calculate_sensor_descriptives,
    calculate_dataset_descriptives,
    DescriptiveStats,
)


class TestDescriptiveAnalytics(unittest.TestCase):
    """Test suite verifying mathematical precision and NaN handling in descriptive analytics."""

    def test_01_known_dataset_moments_and_percentiles(self):
        """Verify calculations against a hand-crafted known sample [10, 20, 30, 40, 50]."""
        data = [10.0, 20.0, 30.0, 40.0, 50.0]
        stats = calculate_sensor_descriptives(data, sensor_name="test_sensor")

        self.assertEqual(stats.total_records, 5)
        self.assertEqual(stats.valid_count, 5)
        self.assertEqual(stats.missing_count, 0)
        self.assertEqual(stats.missing_percentage, 0.0)
        self.assertEqual(stats.mean, 30.0)
        self.assertEqual(stats.median, 30.0)
        self.assertEqual(stats.min, 10.0)
        self.assertEqual(stats.max, 50.0)
        self.assertEqual(stats.range, 40.0)
        self.assertAlmostEqual(stats.std, 15.81, places=2)
        self.assertAlmostEqual(stats.variance, 250.0, places=1)
        self.assertEqual(stats.p50, 30.0)
        self.assertLess(stats.p05, stats.p25)
        self.assertLess(stats.p75, stats.p95)

    def test_02_missing_and_nan_value_handling(self):
        """Verify that NaNs are excluded from statistical moments but properly tallied in missing counts."""
        data = [10.0, np.nan, 30.0, np.nan, 50.0]
        stats = calculate_sensor_descriptives(data, sensor_name="test_sensor")

        self.assertEqual(stats.total_records, 5)
        self.assertEqual(stats.valid_count, 3)
        self.assertEqual(stats.missing_count, 2)
        self.assertEqual(stats.missing_percentage, 40.0)
        self.assertEqual(stats.mean, 30.0)
        self.assertEqual(stats.median, 30.0)

    def test_03_empty_and_all_nan_handling(self):
        """Verify graceful handling of completely empty and all-NaN arrays."""
        empty_stats = calculate_sensor_descriptives([], sensor_name="empty")
        self.assertEqual(empty_stats.valid_count, 0)
        self.assertIsNone(empty_stats.mean)

        nan_stats = calculate_sensor_descriptives([np.nan, np.nan], sensor_name="all_nan")
        self.assertEqual(nan_stats.valid_count, 0)
        self.assertEqual(nan_stats.missing_count, 2)
        self.assertEqual(nan_stats.missing_percentage, 100.0)
        self.assertIsNone(nan_stats.mean)

    def test_04_dataset_multichannel_computation(self):
        """Verify multi-column DataFrame analysis."""
        df = pd.DataFrame({
            "temp": [22.0, 23.0, 24.0, 25.0],
            "humidity": [50.0, 52.0, 54.0, 56.0],
            "unrelated": ["a", "b", "c", "d"],
        })
        results = calculate_dataset_descriptives(df, sensor_columns=["temp", "humidity"])
        self.assertIn("temp", results)
        self.assertIn("humidity", results)
        self.assertNotIn("unrelated", results)
        self.assertEqual(results["temp"].mean, 23.5)
        self.assertEqual(results["humidity"].mean, 53.0)


if __name__ == "__main__":
    unittest.main()
