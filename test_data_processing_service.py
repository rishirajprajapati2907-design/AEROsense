"""
Integration Tests for Data Processing Service
Tests the end-to-end pipeline on physical historical datasets and mocked live ThingSpeak feeds.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
import pandas as pd

from backend.services.data_processing_service import DataProcessingService, ProcessedDatasetResult
from backend.processing.data_transformer import STANDARDIZED_COLUMNS
from thingspeak_client import TelemetryEntry, ChannelStatus


class TestDataProcessingService(unittest.TestCase):

    def setUp(self):
        self.service = DataProcessingService()

    def test_process_historical_archive(self):
        """Test processing the verified 5,024-row historical dataset through the complete pipeline."""
        result = self.service.process_historical_archive()

        self.assertIsInstance(result, ProcessedDatasetResult)
        self.assertEqual(result.record_count, 5024)
        self.assertEqual(len(result.raw_data), 5024)
        self.assertEqual(len(result.standardized_data), 5024)
        self.assertEqual(len(result.flagged_data), 5024)

        # Check all standardized columns are populated
        for col in STANDARDIZED_COLUMNS:
            self.assertIn(col, result.standardized_data.columns)

        # Check dual field1-7 columns are preserved for frontend backwards compatibility
        for i in range(1, 8):
            self.assertIn(f"field{i}", result.standardized_data.columns)

        # Quality metrics
        self.assertGreaterEqual(result.quality_report.overall_completeness_pct, 95.0)
        self.assertEqual(result.quality_report.health_grade, "EXCELLENT")

        # Validation report
        self.assertTrue(result.validation_report.is_valid)

        # Outlier detection occurred without deleting data
        self.assertIn("is_outlier", result.flagged_data.columns)
        self.assertGreater(len(result.outlier_events), 0)

    @patch("thingspeak_client.ThingSpeakClient.fetch_historical")
    def test_process_thingspeak_stream(self, mock_fetch):
        """Test processing mocked ThingSpeak live telemetry feeds."""
        now = datetime.now(timezone.utc)
        entries = [
            TelemetryEntry(
                entry_id=101 + i,
                timestamp=now - timedelta(minutes=10 - i),
                values={
                    "field1": 22.0 + i * 0.1,
                    "field2": 45.0 + i * 0.2,
                    "field3": 90.0,
                    "field4": 2.0,
                    "field5": 1.0,
                    "field6": 0.02,
                    "field7": 12.0,
                },
                raw_values={},
                is_stale=False,
                is_demo=False,
            )
            for i in range(10)
        ]
        status = ChannelStatus(
            state="LIVE",
            status_label="LIVE",
            status_color="#10B981",
            api_connected=True,
            sensor_active=True,
            last_entry_time=now,
        )
        mock_fetch.return_value = (entries, {}, status)

        result, channel_status = self.service.process_thingspeak_stream(results=10)

        self.assertEqual(channel_status.state, "LIVE")
        self.assertEqual(result.record_count, 10)
        self.assertTrue(result.is_live)
        self.assertIn("temperature", result.standardized_data.columns)
        self.assertIn("pm25", result.standardized_data.columns)
        self.assertEqual(result.quality_report.overall_completeness_pct, 100.0)

    def test_process_empty_dataframe(self):
        """Test pipeline gracefully handles empty DataFrame input."""
        empty_df = pd.DataFrame()
        result = self.service.process_dataframe(empty_df, source_name="empty_test")

        self.assertEqual(result.record_count, 0)
        self.assertTrue(result.standardized_data.empty)
        self.assertEqual(result.quality_report.total_records, 0)


if __name__ == "__main__":
    unittest.main()
