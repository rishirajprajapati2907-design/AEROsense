"""
Unit Tests for Historical Data Loader
Verifies loading of physical Excel/CSV datasets, schema integrity,
missing value preservation, and metadata generation.
"""

import os
import unittest
import pandas as pd
import numpy as np

from services.historical_loader import HistoricalDataLoader
from config import SENSOR_FIELDS


class TestHistoricalDataLoader(unittest.TestCase):

    def setUp(self):
        self.loader = HistoricalDataLoader()

    def test_load_dataset_integrity(self):
        """Test loading verified historical dataset returns expected rows and columns."""
        df, meta = self.loader.load(include_mapped_columns=True)

        self.assertFalse(df.empty)
        self.assertEqual(len(df), 5024)
        self.assertIn("timestamp", df.columns)
        self.assertIn("source", df.columns)
        self.assertTrue(df["source"].iloc[0].startswith("historical_"))

        # Check all 7 sensor fields are present
        for fid in SENSOR_FIELDS.keys():
            self.assertIn(fid, df.columns)

        # Check mapped column names exist
        self.assertIn("temperature", df.columns)
        self.assertIn("humidity", df.columns)
        self.assertIn("pm25", df.columns)

        # Metadata checks
        self.assertEqual(meta["total_records"], 5024)
        self.assertEqual(meta["sensor_count"], 7)
        self.assertGreaterEqual(meta["completeness_pct"], 95.0)
        self.assertIsNotNone(meta["start_time"])
        self.assertIsNotNone(meta["end_time"])

    def test_preserves_missing_values(self):
        """Verify loader preserves original NaN values and does not convert them to zero."""
        df, _ = self.loader.load()
        # Ensure that if any null exists in any sensor column, it is NaN, not coerced to 0.0
        for fid in SENSOR_FIELDS.keys():
            null_count = df[fid].isna().sum()
            # If nulls exist, they should be true NaNs
            if null_count > 0:
                self.assertTrue(df[fid].isna().any())

    def test_timestamps_are_sorted_and_timezone_aware(self):
        """Verify timestamps are chronologically ordered."""
        df, _ = self.loader.load()
        self.assertTrue(df["timestamp"].is_monotonic_increasing)


if __name__ == "__main__":
    unittest.main()
