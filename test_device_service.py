"""
Unit Tests for ESP32 Device Repository and Device Management Service
Verifies device registration, configuration storage, status evaluation (ONLINE, STALE, OFFLINE),
heartbeat tracking, health scoring, and timestamp-based state calculations.
"""

import os
import unittest
import tempfile
from datetime import datetime, timedelta

from backend.database.db_connection import DatabaseConnectionManager
from backend.database.device_repository import DeviceRepository
from backend.database.models import DeviceRecord
from backend.services.device_service import DeviceService, DEFAULT_DEVICE_ID


class TestDeviceService(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_devices.db")
        self.db_manager = DatabaseConnectionManager(self.db_path)
        self.repo = DeviceRepository(self.db_manager)
        self.service = DeviceService(self.repo)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_device_registration(self):
        """Verify default ESP32 station is created and initialized as OFFLINE."""
        dev = self.service.get_device(DEFAULT_DEVICE_ID)
        self.assertIsNotNone(dev)
        self.assertEqual(dev.device_id, DEFAULT_DEVICE_ID)
        self.assertEqual(dev.status, "OFFLINE")
        self.assertEqual(dev.channel_id, 3540991)

    def test_device_status_offline_when_no_data(self):
        """Verify device remains OFFLINE when no packets have ever been transmitted."""
        status, elapsed = self.service.evaluate_device_status(DEFAULT_DEVICE_ID)
        self.assertEqual(status, "OFFLINE")
        self.assertIsNone(elapsed)

    def test_device_status_online_with_fresh_packet(self):
        """Verify device transitions to ONLINE when fresh packet timestamp is recorded."""
        now = datetime.now()
        fresh_ts = (now - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")

        self.service.record_heartbeat(DEFAULT_DEVICE_ID, timestamp=fresh_ts, success=True)
        status, elapsed = self.service.evaluate_device_status(DEFAULT_DEVICE_ID, current_time=now)

        self.assertEqual(status, "ONLINE")
        self.assertIsNotNone(elapsed)
        self.assertTrue(elapsed < 300)

    def test_device_status_stale_when_delayed(self):
        """Verify device transitions to STALE when packet age exceeds stale threshold (15m)."""
        now = datetime.now()
        stale_ts = (now - timedelta(minutes=25)).strftime("%Y-%m-%d %H:%M:%S")

        self.service.record_heartbeat(DEFAULT_DEVICE_ID, timestamp=stale_ts, success=True)
        status, elapsed = self.service.evaluate_device_status(DEFAULT_DEVICE_ID, current_time=now)

        self.assertEqual(status, "STALE")
        self.assertIsNotNone(elapsed)
        self.assertTrue(elapsed > 900)

    def test_device_status_offline_when_exceeding_timeout(self):
        """Verify device transitions to OFFLINE when packet age exceeds offline threshold (1h)."""
        now = datetime.now()
        old_ts = (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

        self.service.record_heartbeat(DEFAULT_DEVICE_ID, timestamp=old_ts, success=True)
        status, elapsed = self.service.evaluate_device_status(DEFAULT_DEVICE_ID, current_time=now)

        self.assertEqual(status, "OFFLINE")
        self.assertIsNotNone(elapsed)
        self.assertTrue(elapsed > 3600)

    def test_device_health_diagnostics(self):
        """Verify health score calculation reflects device operational state."""
        health = self.service.get_device_health(DEFAULT_DEVICE_ID)
        self.assertEqual(health["device_id"], DEFAULT_DEVICE_ID)
        self.assertEqual(health["status"], "OFFLINE")
        self.assertTrue(health["is_offline"])
        self.assertIn("health_score", health)

    def test_sensor_channel_mapping(self):
        """Verify sensor channel bindings match physical sensor field mappings."""
        mapping = self.service.get_sensor_mapping(DEFAULT_DEVICE_ID)
        self.assertIn("field1", mapping)
        self.assertEqual(mapping["field1"]["name"], "Temperature")
        self.assertEqual(mapping["field2"]["name"], "Relative Humidity")
        self.assertIn("field7", mapping)


if __name__ == "__main__":
    unittest.main()
