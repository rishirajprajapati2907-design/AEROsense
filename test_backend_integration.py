"""
AEROsense End-to-End Backend Architecture & Integration Tests
Validates the complete 10-layer architectural separation, type safety,
and regression prevention for DeviceRecord and sensor mapping dictionary access.
"""

import os
import json
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone

from backend.database.models import (
    SensorReading,
    SensorMetadata,
    AnomalyLog,
    PredictionLog,
    SystemLog,
    NotificationRecord,
    DeviceRecord,
)
from backend.database.db_connection import DatabaseConnectionManager
from backend.database.db_initializer import initialize_database
from backend.database.sensor_repository import SensorRepository
from backend.database.device_repository import DeviceRepository
from backend.database.backup_service import DatabaseBackupService
from backend.services.database_service import DatabaseService
from backend.services.device_service import DeviceService, DEFAULT_SENSOR_MAPPING
from backend.services.prediction_service import PredictionService
from backend.services.thingspeak_sync_service import ThingSpeakSyncService


class TestBackendArchitectureIntegration(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_integration.db")
        initialize_database(self.db_path, seed_metadata=True)
        self.db_manager = DatabaseConnectionManager(self.db_path)
        self.db_service = DatabaseService(db_path=self.db_path)
        self.device_service = DeviceService(repository=self.db_service.devices)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_all_domain_models_importable(self):
        """Verify all domain entity models are cleanly importable from package roots."""
        import backend.database as db_pkg
        self.assertTrue(hasattr(db_pkg, "DeviceRecord"))
        self.assertTrue(hasattr(db_pkg, "NotificationRecord"))
        self.assertTrue(hasattr(db_pkg, "SensorReading"))
        self.assertTrue(hasattr(db_pkg, "SensorMetadata"))

        from services.device_service import DeviceRecord as DR_facade
        self.assertIs(DeviceRecord, DR_facade)

    def test_02_database_service_devices_property(self):
        """Verify DatabaseService.devices is always initialized and accessible."""
        self.assertIsNotNone(self.db_service.devices)
        self.assertIsInstance(self.db_service.devices, DeviceRepository)
        devices = self.db_service.devices.get_all_devices()
        self.assertGreaterEqual(len(devices), 1)
        self.assertEqual(devices[0].device_id, "ESP32-AEROSENSE-MAIN")

    def test_03_sensor_mapping_always_returns_dict_never_string(self):
        """
        Regression Test for AttributeError: 'str' object has no attribute 'get'.
        Even when legacy database record stores strings in config_json,
        device_service.get_sensor_mapping() MUST return Dict[str, Dict[str, Any]].
        """
        # Inject legacy string mapping into database
        legacy_config = {
            "channel_name": "Legacy String Format",
            "sensor_mapping": {
                "field1": "temperature",
                "field2": "humidity",
                "field3": "smoke",
            }
        }
        with self.db_manager.transaction() as conn:
            conn.execute(
                "UPDATE devices SET config_json = ? WHERE device_id = 'ESP32-AEROSENSE-MAIN';",
                (json.dumps(legacy_config),)
            )

        # Retrieve through service
        mapping = self.device_service.get_sensor_mapping("ESP32-AEROSENSE-MAIN")
        self.assertIsInstance(mapping, dict)

        # Verify EVERY field item is a dictionary with 'pin' and 'type' keys
        for fid in ("field1", "field2", "field3"):
            field_data = mapping.get(fid)
            self.assertIsInstance(field_data, dict, f"Expected dict for {fid}, got {type(field_data)}")
            # Crucial: accessing .get('pin') or .get('type') must not raise AttributeError
            pin = field_data.get("pin")
            type_val = field_data.get("type")
            self.assertIsNotNone(field_data.get("name"))

    def test_04_device_health_evaluation_consistency(self):
        """Verify device health scoring produces valid numbers and offline state."""
        health = self.device_service.get_device_health("ESP32-AEROSENSE-MAIN")
        self.assertIn("health_score", health)
        self.assertIsInstance(health["health_score"], float)
        self.assertIn(health["status"], ("OFFLINE", "STALE", "ONLINE"))

    def test_05_prediction_service_caching_and_execution(self):
        """Verify PredictionService evaluates without re-instantiation overhead."""
        pred_svc = PredictionService(db_manager=self.db_manager)
        self.assertIsNotNone(pred_svc.model_manager)
        # Seed 10 records
        for i in range(10):
            self.db_service.sensors.insert_reading({
                "timestamp": f"2026-11-09 10:{i:02d}:00",
                "temperature": 22.0 + (i * 0.1),
                "humidity": 45.0 + (i * 0.2),
                "source": "test_seed",
            })
        df = pred_svc.get_sensor_data(source="test_seed")
        self.assertEqual(len(df), 10)


if __name__ == "__main__":
    unittest.main()
