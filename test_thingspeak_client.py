"""
Unit Tests for ThingSpeak Client
Tests REST API queries, error handling, rate limiting, timestamp parsing,
staleness detection, and DataFrame conversions using mocked responses.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
import pandas as pd
import requests

from thingspeak_client import ThingSpeakClient, TelemetryEntry, ChannelStatus


class TestThingSpeakClient(unittest.TestCase):

    def setUp(self):
        self.client = ThingSpeakClient(channel_id=3540991, read_api_key="TEST_API_KEY_123")

    @patch("requests.Session.get")
    def test_fetch_latest_success(self, mock_get):
        """Test successful fetch of the most recent channel entry."""
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "created_at": now_iso,
            "entry_id": 4096,
            "field1": "24.5",
            "field2": "48.2",
            "field3": "120.0",
            "field4": "2.8",
            "field5": "1.4",
            "field6": "0.025",
            "field7": "15.0",
        }
        mock_get.return_value = mock_resp

        entry, status = self.client.fetch_latest()

        self.assertIsNotNone(entry)
        self.assertEqual(entry.entry_id, 4096)
        self.assertEqual(entry.values["field1"], 24.5)
        self.assertEqual(entry.values["field2"], 48.2)
        self.assertEqual(entry.values["field7"], 15.0)
        self.assertEqual(status.state, "LIVE")
        self.assertTrue(status.api_connected)
        self.assertTrue(status.sensor_active)
        self.assertFalse(entry.is_stale)
        self.assertFalse(entry.is_demo)

    @patch("requests.Session.get")
    def test_fetch_latest_stale_detection(self, mock_get):
        """Test that readings older than 5 minutes (300s) are marked STALE."""
        stale_time = (datetime.now(timezone.utc) - timedelta(minutes=8)).strftime("%Y-%m-%dT%H:%M:%SZ")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "created_at": stale_time,
            "entry_id": 4095,
            "field1": "22.0",
            "field2": "50.0",
            "field3": "110.0",
            "field4": "2.0",
            "field5": "1.0",
            "field6": "0.020",
            "field7": "12.0",
        }
        mock_get.return_value = mock_resp

        entry, status = self.client.fetch_latest()

        self.assertIsNotNone(entry)
        self.assertTrue(entry.is_stale)
        self.assertEqual(status.state, "STALE")
        self.assertTrue(status.api_connected)
        self.assertFalse(status.sensor_active)

    @patch("requests.Session.get")
    def test_fetch_latest_offline_detection(self, mock_get):
        """Test that readings older than 15 minutes (900s) are marked OFFLINE."""
        offline_time = (datetime.now(timezone.utc) - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "created_at": offline_time,
            "entry_id": 4000,
            "field1": "21.5",
            "field2": "49.0",
        }
        mock_get.return_value = mock_resp

        entry, status = self.client.fetch_latest()

        self.assertIsNotNone(entry)
        self.assertEqual(status.state, "OFFLINE")
        self.assertTrue(status.api_connected)
        self.assertFalse(status.sensor_active)

    @patch("requests.Session.get")
    def test_fetch_latest_auth_failure(self, mock_get):
        """Test handling of ThingSpeak authentication reject (-1 / 401)."""
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_resp.text = "-1"
        mock_get.return_value = mock_resp

        entry, status = self.client.fetch_latest()

        self.assertIsNone(entry)
        self.assertEqual(status.state, "OFFLINE")
        self.assertFalse(status.api_connected)
        self.assertIn("rejected", status.error_message.lower())

    @patch("requests.Session.get")
    def test_fetch_latest_rate_limit(self, mock_get):
        """Test handling of HTTP 429 rate limit exceeded."""
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_get.return_value = mock_resp

        entry, status = self.client.fetch_latest()

        self.assertIsNone(entry)
        self.assertEqual(status.state, "STALE")
        self.assertIn("rate limit", status.error_message.lower())

    @patch("requests.Session.get")
    def test_fetch_latest_timeout(self, mock_get):
        """Test timeout handling does not crash the client."""
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

        entry, status = self.client.fetch_latest()

        self.assertIsNone(entry)
        self.assertEqual(status.state, "OFFLINE")
        self.assertFalse(status.api_connected)
        self.assertIn("timed out", status.error_message.lower())

    @patch("requests.Session.get")
    def test_fetch_historical_to_dataframe(self, mock_get):
        """Test fetching historical feeds and converting to DataFrame with mapped fields."""
        now_dt = datetime.now(timezone.utc)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "channel": {"id": 3540991, "name": "AEROsense Air Quality"},
            "feeds": [
                {
                    "created_at": (now_dt - timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "entry_id": 1,
                    "field1": "23.1",
                    "field2": "45.0",
                    "field3": "85.0",
                    "field4": "1.5",
                    "field5": "0.8",
                    "field6": "0.015",
                    "field7": "10.2",
                },
                {
                    "created_at": (now_dt - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "entry_id": 2,
                    "field1": "23.4",
                    "field2": "45.5",
                    "field3": "88.0",
                    "field4": "1.6",
                    "field5": "0.9",
                    "field6": "0.016",
                    "field7": "11.0",
                },
            ],
        }
        mock_get.return_value = mock_resp

        df, status = self.client.fetch_historical_dataframe(results=2, include_mapped_columns=True)

        self.assertEqual(len(df), 2)
        self.assertEqual(status.state, "LIVE")
        self.assertIn("field1", df.columns)
        self.assertIn("temperature", df.columns)
        self.assertIn("humidity", df.columns)
        self.assertIn("pm25", df.columns)
        self.assertEqual(df["temperature"].iloc[0], 23.1)
        self.assertEqual(df["pm25"].iloc[1], 11.0)
        self.assertEqual(df["source"].iloc[0], "thingspeak_historical")

    def test_clean_float_handles_missing_values(self):
        """Test clean float parser handles missing, invalid, or null strings safely."""
        self.assertIsNone(self.client._clean_float(None))
        self.assertIsNone(self.client._clean_float(""))
        self.assertIsNone(self.client._clean_float("NaN"))
        self.assertIsNone(self.client._clean_float("null"))
        self.assertIsNone(self.client._clean_float("--"))
        self.assertIsNone(self.client._clean_float("ERR"))
        self.assertEqual(self.client._clean_float("25.6"), 25.6)
        self.assertEqual(self.client._clean_float(42), 42.0)


if __name__ == "__main__":
    unittest.main()
