"""
Unit Tests for CSV Data Exporter
Verifies CSV byte conversions, date filtering, column subsets, anomaly export, and summary metrics.
"""

import unittest
import pandas as pd
import numpy as np

from backend.reporting.csv_exporter import CsvDataExporter


class TestCsvExporter(unittest.TestCase):

    def setUp(self):
        self.exporter = CsvDataExporter()
        dates = pd.date_range("2026-06-01 00:00", periods=10, freq="1h")
        self.sample_df = pd.DataFrame({
            "timestamp": [d.strftime("%Y-%m-%d %H:%M:%S") for d in dates],
            "temperature": [20.0 + i * 0.5 for i in range(10)],
            "humidity": [50.0 - i * 0.5 for i in range(10)],
            "smoke": [100.0] * 10,
            "carbon_monoxide": [1.5] * 10,
            "ammonia": [0.8] * 10,
            "nitrogen_oxides": [0.02] * 10,
            "pm25": [15.0] * 10,
            "source": "csv_test",
        })

    def test_export_readings_csv_full(self):
        """Verify full CSV export generates valid CSV bytes."""
        csv_bytes = self.exporter.export_readings_csv(self.sample_df)
        self.assertIsInstance(csv_bytes, bytes)
        content = csv_bytes.decode("utf-8")
        lines = content.strip().split("\n")
        self.assertEqual(len(lines), 11)  # 1 header + 10 rows
        self.assertIn("temperature", lines[0])

    def test_export_readings_csv_date_filter(self):
        """Verify date filtering limits rows correctly."""
        csv_bytes = self.exporter.export_readings_csv(
            self.sample_df,
            start_date="2026-06-01 03:00:00",
            end_date="2026-06-01 06:00:00",
        )
        content = csv_bytes.decode("utf-8")
        lines = content.strip().split("\n")
        self.assertEqual(len(lines), 5)  # 1 header + 4 rows (03:00, 04:00, 05:00, 06:00)

    def test_export_readings_csv_sensor_subset(self):
        """Verify column filtering returns only requested sensors."""
        csv_bytes = self.exporter.export_readings_csv(
            self.sample_df,
            sensors=["temperature", "humidity"],
        )
        content = csv_bytes.decode("utf-8")
        lines = content.strip().split("\n")
        header = lines[0].split(",")
        self.assertIn("timestamp", header)
        self.assertIn("temperature", header)
        self.assertIn("humidity", header)
        self.assertNotIn("smoke", header)

    def test_export_anomalies_and_summary_csv(self):
        """Verify anomaly logs and descriptive summary CSV generation."""
        anomalies = [{"id": 1, "sensor_name": "temperature", "detected_value": 35.0, "severity": "CRITICAL"}]
        anom_csv = self.exporter.export_anomalies_csv(anomalies)
        self.assertIn(b"temperature", anom_csv)

        summary_csv = self.exporter.export_summary_csv(self.sample_df)
        self.assertIn(b"mean", summary_csv)


if __name__ == "__main__":
    unittest.main()
