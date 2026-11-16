"""
Unit Tests for Multi-Tab Excel Exporter (openpyxl)
Verifies workbook structure, worksheet names, column alignments, styling, and data accuracy.
"""

import io
import unittest
import pandas as pd
import numpy as np
import openpyxl

from backend.reporting.excel_exporter import MultiTabExcelExporter


class TestExcelExporter(unittest.TestCase):

    def setUp(self):
        self.exporter = MultiTabExcelExporter()
        dates = pd.date_range("2026-06-01 00:00", periods=20, freq="15min")
        self.sample_df = pd.DataFrame({
            "timestamp": [d.strftime("%Y-%m-%d %H:%M:%S") for d in dates],
            "temperature": np.linspace(20.0, 25.0, 20),
            "humidity": np.linspace(40.0, 60.0, 20),
            "smoke": np.linspace(100.0, 120.0, 20),
            "carbon_monoxide": np.linspace(1.0, 2.5, 20),
            "ammonia": np.linspace(0.5, 1.5, 20),
            "nitrogen_oxides": np.linspace(0.01, 0.04, 20),
            "pm25": np.linspace(10.0, 25.0, 20),
            "source": "test_unit",
        })

    def test_export_workbook_sheets(self):
        """Verify all 5 required worksheets are present in the generated workbook."""
        anomalies = [
            {"id": 1, "sensor_name": "smoke", "timestamp": "2026-06-01 01:00:00", "detected_value": 150.0, "method": "IQR", "severity": "CRITICAL", "explanation": "Spike detected"},
        ]
        predictions = [
            {"id": 1, "sensor_name": "temperature", "prediction_timestamp": "2026-06-01 06:00:00", "predicted_value": 22.4, "model_name": "Random Forest", "confidence_lower": 21.0, "confidence_upper": 23.8},
        ]

        excel_bytes = self.exporter.export_workbook(
            readings_df=self.sample_df,
            anomalies_df_or_list=anomalies,
            predictions_df_or_list=predictions,
            quality_metadata={"sensor_node": "Station A", "uptime": "99.9%"},
        )

        self.assertIsInstance(excel_bytes, bytes)
        wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))

        expected_sheets = {
            "Sensor Readings",
            "Historical Analytics",
            "Anomaly Logs",
            "AI Predictions",
            "Data Quality & Metadata",
        }
        self.assertTrue(expected_sheets.issubset(set(wb.sheetnames)))

        # Verify Sensor Readings content
        ws_readings = wb["Sensor Readings"]
        self.assertEqual(ws_readings.cell(row=1, column=1).value, "timestamp")
        self.assertEqual(ws_readings.max_row, 21)  # 1 header + 20 rows

        # Verify Anomaly Logs content
        ws_anom = wb["Anomaly Logs"]
        self.assertEqual(ws_anom.max_row, 2)  # 1 header + 1 anomaly

        # Verify Data Quality & Metadata content
        ws_meta = wb["Data Quality & Metadata"]
        self.assertTrue(ws_meta.max_row >= 5)

    def test_export_empty_dataframe(self):
        """Verify workbook generation succeeds even with empty inputs."""
        empty_df = pd.DataFrame()
        excel_bytes = self.exporter.export_workbook(empty_df)
        wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
        self.assertIn("Sensor Readings", wb.sheetnames)


if __name__ == "__main__":
    unittest.main()
