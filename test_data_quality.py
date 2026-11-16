"""
Unit Tests for Data Quality Analyzer
Tests calculation of total/valid/invalid records, completeness percentage,
missing values per sensor, and temporal limits.
"""

import unittest
import pandas as pd
import numpy as np

from backend.processing.data_quality import DataQualityAnalyzer, DataQualityReport


class TestDataQualityAnalyzer(unittest.TestCase):

    def test_complete_dataset_quality_score(self):
        """Test dataset with 100% valid readings scores EXCELLENT health."""
        df = pd.DataFrame({
            "timestamp": pd.date_range("2026-01-01", periods=10, freq="min", tz="UTC"),
            "temperature": [22.0] * 10,
            "humidity": [45.0] * 10,
            "smoke": [100.0] * 10,
            "carbon_monoxide": [2.0] * 10,
            "ammonia": [1.0] * 10,
            "nitrogen_oxides": [0.02] * 10,
            "pm25": [15.0] * 10,
        })

        report = DataQualityAnalyzer.analyze(df)

        self.assertEqual(report.total_records, 10)
        self.assertEqual(report.valid_records, 10)
        self.assertEqual(report.invalid_records, 0)
        self.assertEqual(report.overall_completeness_pct, 100.0)
        self.assertEqual(report.health_grade, "EXCELLENT")

    def test_missing_values_per_sensor_calculation(self):
        """Test calculation of missing values per sensor."""
        df = pd.DataFrame({
            "timestamp": pd.date_range("2026-01-01", periods=4, freq="min", tz="UTC"),
            "temperature": [22.0, np.nan, 23.0, np.nan],  # 2 missing (50%)
            "humidity": [45.0, 46.0, 47.0, np.nan],       # 1 missing (25%)
            "pm25": [15.0, 16.0, 17.0, 18.0],             # 0 missing (100% complete)
        })

        report = DataQualityAnalyzer.analyze(df, sensor_columns=["temperature", "humidity", "pm25"])

        self.assertEqual(report.missing_values_per_sensor["temperature"], 2)
        self.assertEqual(report.missing_pct_per_sensor["temperature"], 50.0)
        self.assertEqual(report.sensor_completeness["temperature"], 50.0)
        self.assertEqual(report.missing_values_per_sensor["humidity"], 1)
        self.assertEqual(report.missing_values_per_sensor["pm25"], 0)

    def test_empty_dataset_quality(self):
        """Test empty DataFrame returns safe zeroed metrics."""
        empty_df = pd.DataFrame()
        report = DataQualityAnalyzer.analyze(empty_df)

        self.assertEqual(report.total_records, 0)
        self.assertEqual(report.valid_records, 0)
        self.assertEqual(report.overall_completeness_pct, 0.0)
        self.assertEqual(report.health_grade, "POOR")


if __name__ == "__main__":
    unittest.main()
