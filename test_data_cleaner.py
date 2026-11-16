"""
Unit Tests for Data Cleaner Engine
Tests missing value handling, duplicate detection, empty row removal,
and verification that raw datasets are preserved without zero-filling.
"""

import unittest
import pandas as pd
import numpy as np

from backend.processing.data_cleaner import DataCleaner, CleaningReport


class TestDataCleaner(unittest.TestCase):

    def test_missing_values_preserved_never_zeroed(self):
        """Verify missing values remain NaN and are NEVER silently replaced with zero."""
        df = pd.DataFrame({
            "timestamp": pd.date_range("2026-01-01", periods=4, freq="min", tz="UTC"),
            "field1": [21.5, None, "NaN", "--"],
            "field2": [45.0, 50.0, None, np.nan],
        })

        cleaned, raw, report = DataCleaner.clean(df, sensor_columns=["field1", "field2"], drop_completely_empty=False)

        # Check raw is preserved untouched
        self.assertEqual(raw["field1"].iloc[3], "--")

        # Check cleaned has NaNs, NOT 0.0
        self.assertTrue(np.isnan(cleaned["field1"].iloc[1]))
        self.assertTrue(np.isnan(cleaned["field1"].iloc[2]))
        self.assertTrue(np.isnan(cleaned["field1"].iloc[3]))
        self.assertFalse((cleaned["field1"] == 0.0).any())

        # Check report counts
        self.assertEqual(report.missing_values_per_sensor["field1"], 3)
        self.assertEqual(report.missing_values_per_sensor["field2"], 2)

    def test_completely_empty_rows_dropped(self):
        """Test rows where all sensor values are missing are dropped if drop_completely_empty is True."""
        df = pd.DataFrame({
            "timestamp": pd.date_range("2026-01-01", periods=3, freq="min", tz="UTC"),
            "field1": [22.0, None, 24.0],
            "field2": [45.0, None, 48.0],
            "field3": [100.0, None, 110.0],
        })

        cleaned, raw, report = DataCleaner.clean(df, sensor_columns=["field1", "field2", "field3"], drop_completely_empty=True)

        self.assertEqual(len(raw), 3)
        self.assertEqual(len(cleaned), 2)
        self.assertEqual(report.dropped_empty_rows, 1)

    def test_duplicate_rows_detected(self):
        """Test detection and handling of duplicate records."""
        df = pd.DataFrame({
            "timestamp": [
                pd.Timestamp("2026-01-01 10:00:00", tz="UTC"),
                pd.Timestamp("2026-01-01 10:00:00", tz="UTC"),
                pd.Timestamp("2026-01-01 10:01:00", tz="UTC"),
            ],
            "field1": [22.0, 22.0, 23.0],
            "field2": [45.0, 45.0, 46.0],
        })

        cleaned, _, report = DataCleaner.clean(
            df,
            sensor_columns=["field1", "field2"],
            drop_duplicate_rows=True,
            subset_for_duplicates=["timestamp"],
        )

        self.assertEqual(len(cleaned), 2)
        self.assertEqual(report.dropped_duplicate_rows, 1)

    def test_empty_dataframe_handled_safely(self):
        """Test empty input DataFrame returns clean report without exceptions."""
        empty_df = pd.DataFrame()
        cleaned, raw, report = DataCleaner.clean(empty_df)
        self.assertTrue(cleaned.empty)
        self.assertEqual(report.raw_record_count, 0)
        self.assertEqual(report.cleaned_record_count, 0)


if __name__ == "__main__":
    unittest.main()
