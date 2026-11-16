"""
Unit Tests for Environmental Audit PDF Generator (ReportLab)
Verifies PDF generation, binary header compliance, multi-sensor sections, and empty dataframe handling.
"""

import io
import unittest
import pandas as pd
import numpy as np

from backend.reporting.pdf_generator import EnvironmentalAuditPdfGenerator


class TestPdfGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = EnvironmentalAuditPdfGenerator()
        # Create realistic sample dataframe
        dates = pd.date_range("2026-06-01 00:00", periods=50, freq="15min")
        self.sample_df = pd.DataFrame({
            "timestamp": [d.strftime("%Y-%m-%d %H:%M:%S") for d in dates],
            "temperature": np.linspace(22.0, 26.5, 50),
            "humidity": np.linspace(45.0, 58.0, 50),
            "smoke": np.linspace(100.0, 150.0, 50),
            "carbon_monoxide": np.linspace(1.5, 4.0, 50),
            "ammonia": np.linspace(0.8, 2.2, 50),
            "nitrogen_oxides": np.linspace(0.01, 0.05, 50),
            "pm25": np.linspace(12.0, 35.0, 50),
            "source": "historical_test",
        })

    def test_pdf_generation_magic_bytes(self):
        """Verify generated PDF starts with standard PDF binary header."""
        pdf_bytes = self.generator.generate_report(self.sample_df)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

    def test_pdf_generation_with_anomalies_and_predictions(self):
        """Verify report generation when anomalies and predictions are present."""
        sample_anomalies = [
            {"sensor_name": "carbon_monoxide", "timestamp": "2026-06-01 02:30:00", "detected_value": 4.5, "method": "IQR", "severity": "CRITICAL"},
            {"sensor_name": "temperature", "timestamp": "2026-06-01 04:15:00", "detected_value": 31.2, "method": "Z-Score", "severity": "WARNING"},
        ]
        sample_preds = [
            {"sensor_name": "temperature", "prediction_timestamp": "2026-06-01 13:00:00", "predicted_value": 24.8, "model_name": "Random Forest", "confidence_lower": 23.5, "confidence_upper": 26.1},
        ]

        pdf_bytes = self.generator.generate_report(
            df=self.sample_df,
            anomalies=sample_anomalies,
            predictions=sample_preds,
            date_range_label="Test Period June 2026",
        )
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
        self.assertTrue(len(pdf_bytes) > 2000)

    def test_pdf_generation_empty_dataframe(self):
        """Verify report generator handles an empty dataframe without crashing."""
        empty_df = pd.DataFrame(columns=["timestamp", "temperature", "humidity"])
        pdf_bytes = self.generator.generate_report(empty_df)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
        self.assertTrue(len(pdf_bytes) > 500)


if __name__ == "__main__":
    unittest.main()
