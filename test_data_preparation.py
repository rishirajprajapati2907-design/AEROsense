"""
Unit tests for Time-Series Data Preparation and Chronological Splitting
"""

import unittest
from datetime import datetime, timezone
import pandas as pd
import numpy as np

from backend.intelligence.prediction.data_preparation import TimeSeriesDataPreparer


class TestTimeSeriesDataPreparation(unittest.TestCase):

    def setUp(self):
        # Generate sample series with timestamps
        n = 120
        self.timestamps = pd.date_range("2026-10-18 00:00:00", periods=n, freq="min", tz="UTC")
        self.df_normal = pd.DataFrame({
            "timestamp": self.timestamps,
            "temperature": 25.0 + np.sin(np.linspace(0, 4 * np.pi, n)) * 3.0,
        })

    def test_chronological_sorting_and_deduplication(self):
        # Scramble timestamps and introduce duplicates
        scrambled = self.df_normal.sample(frac=1.0, random_state=42).reset_index(drop=True)
        # Duplicate first timestamp
        dup_row = scrambled.iloc[0:1].copy()
        scrambled = pd.concat([scrambled, dup_row], ignore_index=True)

        clean_df, audit = TimeSeriesDataPreparer.prepare_dataset(scrambled, "temperature")

        self.assertTrue(audit["success"])
        self.assertEqual(len(clean_df), len(self.df_normal))
        # Verify strictly chronological
        self.assertTrue(clean_df["timestamp"].is_monotonic_increasing)

    def test_sensor_data_sufficiency_assessment(self):
        # 1. Normal sufficient data
        res_normal = TimeSeriesDataPreparer.assess_sensor_data_sufficiency(
            self.df_normal["temperature"], "temperature"
        )
        self.assertTrue(res_normal["is_sufficient"])

        # 2. Insufficient sample size (< 100)
        short_series = pd.Series([25.0] * 30)
        res_short = TimeSeriesDataPreparer.assess_sensor_data_sufficiency(short_series, "short")
        self.assertFalse(res_short["is_sufficient"])
        self.assertIn("Insufficient sample size", res_short["reason"])

        # 3. Flatlined / zero variance
        flat_series = pd.Series([25.0] * 150)
        res_flat = TimeSeriesDataPreparer.assess_sensor_data_sufficiency(flat_series, "flat")
        self.assertFalse(res_flat["is_sufficient"])
        self.assertIn("near-zero variance", res_flat["reason"])

        # 4. Saturated sensor (like PM2.5 pegged at 560.9)
        saturated = [560.9] * 145 + [500.0, 480.0, 520.0, 510.0, 490.0]  # >95% constant
        res_sat = TimeSeriesDataPreparer.assess_sensor_data_sufficiency(pd.Series(saturated), "pm25")
        self.assertFalse(res_sat["is_sufficient"])
        self.assertIn("Sensor saturated", res_sat["reason"])

    def test_chronological_split_prevents_data_leakage(self):
        train_df, val_df, test_df = TimeSeriesDataPreparer.chronological_split(
            self.df_normal, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15
        )

        self.assertGreater(len(train_df), 0)
        self.assertGreater(len(val_df), 0)
        self.assertGreater(len(test_df), 0)
        self.assertEqual(len(train_df) + len(val_df) + len(test_df), len(self.df_normal))

        # Strict chronological integrity: train max < val min <= val max < test min
        self.assertLess(train_df["timestamp"].max(), val_df["timestamp"].min())
        self.assertLess(val_df["timestamp"].max(), test_df["timestamp"].min())


if __name__ == "__main__":
    unittest.main()
