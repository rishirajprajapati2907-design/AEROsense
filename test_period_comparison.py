"""
Unit tests for AEROsense Period Comparison Module.
Verifies period deltas, percentage changes, variance shifts, and sample-size gating.
"""

import unittest
from datetime import datetime, timezone
import pandas as pd

from backend.analytics.period_comparison import (
    compare_periods,
    PeriodComparisonResult,
)


class TestPeriodComparison(unittest.TestCase):
    """Test suite verifying multi-period comparative evaluations."""

    def test_01_period_shift_and_deltas(self):
        """Verify metric deltas and percentage changes across two known windows."""
        # Previous window: mean = 20.0
        df_prev = pd.DataFrame({
            "timestamp": pd.date_range("2026-10-01", periods=12, freq="1h", tz="UTC"),
            "temperature": [20.0] * 12,
            "humidity": [50.0] * 12,
        })
        # Current window: temp mean = 25.0 (+25%), humidity mean = 40.0 (-20%)
        df_curr = pd.DataFrame({
            "timestamp": pd.date_range("2026-10-02", periods=12, freq="1h", tz="UTC"),
            "temperature": [25.0] * 12,
            "humidity": [40.0] * 12,
        })

        res = compare_periods(df_curr, df_prev, sensor_columns=["temperature", "humidity"])

        self.assertEqual(res.status, "SUCCESS")
        self.assertIn("temperature", res.sensor_comparisons)
        self.assertIn("humidity", res.sensor_comparisons)

        temp_comp = res.sensor_comparisons["temperature"]
        self.assertEqual(temp_comp["current_mean"], 25.0)
        self.assertEqual(temp_comp["previous_mean"], 20.0)
        self.assertEqual(temp_comp["absolute_delta"], 5.0)
        self.assertEqual(temp_comp["percent_change"], 25.0)
        self.assertEqual(temp_comp["direction"], "INCREASED")

        hum_comp = res.sensor_comparisons["humidity"]
        self.assertEqual(hum_comp["percent_change"], -20.0)
        self.assertEqual(hum_comp["direction"], "DECREASED")

    def test_02_insufficient_samples_gating(self):
        """Verify that comparisons with fewer than 10 samples are gated as INSUFFICIENT_DATA."""
        df_small = pd.DataFrame({
            "timestamp": pd.date_range("2026-10-01", periods=4, freq="1h", tz="UTC"),
            "temperature": [20.0, 21.0, 22.0, 23.0],
        })
        df_ok = pd.DataFrame({
            "timestamp": pd.date_range("2026-10-02", periods=15, freq="1h", tz="UTC"),
            "temperature": [20.0] * 15,
        })

        res = compare_periods(df_small, df_ok, min_samples_per_period=10)
        self.assertEqual(res.status, "INSUFFICIENT_DATA")
        self.assertIn("Insufficient observation count", res.explanation)


if __name__ == "__main__":
    unittest.main()
