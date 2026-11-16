"""
Unit Tests for Unified Data Service
Verifies mode switching between Historical and Live sources,
source metadata attachment, and offline ESP32 node fallback behavior.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
import pandas as pd

from services.data_service import UnifiedDataService
from thingspeak_client import TelemetryEntry, ChannelStatus


class TestUnifiedDataService(unittest.TestCase):

    def setUp(self):
        self.service = UnifiedDataService()

    def test_historical_mode_returns_archive_and_metadata(self):
        """Test Historical mode loads verified dataset and attaches DataSourceInfo."""
        latest_entry, df_active, status, info = self.service.get_state(is_live_mode=False)

        self.assertIsNotNone(latest_entry)
        self.assertEqual(len(df_active), 5024)
        self.assertEqual(status.state, "HISTORICAL")
        self.assertEqual(info.mode, "HISTORICAL")
        self.assertFalse(info.is_live)
        self.assertFalse(info.is_stale)
        self.assertFalse(info.is_offline)
        self.assertIn("historical", info.source_type)
        self.assertEqual(info.record_count, 5024)

    @patch("thingspeak_client.ThingSpeakClient.fetch_latest")
    @patch("thingspeak_client.ThingSpeakClient.fetch_historical")
    def test_live_mode_with_active_sensor(self, mock_hist, mock_latest):
        """Test Live mode correctly returns ThingSpeak telemetry when sensor is active."""
        now_dt = datetime.now(timezone.utc)
        mock_entry = TelemetryEntry(
            entry_id=5001,
            timestamp=now_dt,
            values={"field1": 23.5, "field2": 46.0, "field3": 95.0, "field4": 2.1, "field5": 1.1, "field6": 0.02, "field7": 14.0},
            raw_values={},
            is_stale=False,
            is_demo=False,
            source="thingspeak_live",
        )
        mock_status = ChannelStatus(
            state="LIVE",
            status_label="LIVE",
            status_color="#10B981",
            api_connected=True,
            sensor_active=True,
            last_entry_time=now_dt,
            seconds_since_last=5.0,
            time_elapsed_display="5s ago",
        )
        mock_latest.return_value = (mock_entry, mock_status)
        mock_hist.return_value = ([mock_entry] * 10, {}, mock_status)

        latest, df_active, status, info = self.service.get_state(is_live_mode=True)

        self.assertIsNotNone(latest)
        self.assertEqual(latest.entry_id, 5001)
        self.assertEqual(status.state, "LIVE")
        self.assertEqual(info.mode, "LIVE")
        self.assertTrue(info.is_live)
        self.assertFalse(info.is_stale)
        self.assertFalse(info.is_offline)

    @patch("thingspeak_client.ThingSpeakClient.fetch_latest")
    @patch("thingspeak_client.ThingSpeakClient.fetch_historical")
    def test_live_mode_offline_esp32_preserves_reading_and_analytics(self, mock_hist, mock_latest):
        """
        When ESP32 is offline:
        1. Last available reading is preserved.
        2. State is clearly marked OFFLINE or STALE.
        3. Never generates artificial/fake readings.
        4. Historical analytics stay operational.
        """
        stale_dt = datetime.now(timezone.utc) - timedelta(hours=2)
        mock_entry = TelemetryEntry(
            entry_id=4500,
            timestamp=stale_dt,
            values={"field1": 21.0, "field2": 52.0, "field3": 110.0, "field4": 3.0, "field5": 1.5, "field6": 0.03, "field7": 16.0},
            raw_values={},
            is_stale=True,
            is_demo=False,
            source="thingspeak_live",
        )
        mock_status = ChannelStatus(
            state="OFFLINE",
            status_label="OFFLINE",
            status_color="#EF4444",
            api_connected=True,
            sensor_active=False,
            last_entry_time=stale_dt,
            seconds_since_last=7200.0,
            time_elapsed_display="2h ago",
            error_message="Sensor offline for 2 hours.",
        )
        mock_latest.return_value = (mock_entry, mock_status)
        # Few entries returned by live query (<5)
        mock_hist.return_value = ([mock_entry], {}, mock_status)

        latest, df_active, status, info = self.service.get_state(is_live_mode=True)

        self.assertIsNotNone(latest)
        self.assertEqual(latest.entry_id, 4500)
        self.assertFalse(latest.is_demo)  # Must never be artificial/demo
        self.assertEqual(status.state, "OFFLINE")
        self.assertTrue(info.is_offline)
        # Analytics stay operational using full historical dataset as reference
        self.assertEqual(len(df_active), 5024)


if __name__ == "__main__":
    unittest.main()
