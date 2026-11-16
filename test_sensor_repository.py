"""
Unit Tests for Sensor Repository & Database Service Integration
Tests single insertion, bulk imports, duplicate rejection, NULL sensor values,
date range filtering, sensor-specific series, CSV exports, and historical archive import.
"""

import os
import unittest
import tempfile
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta

from backend.database.db_connection import DatabaseConnectionManager
from backend.database.db_initializer import initialize_database
from backend.database.sensor_repository import SensorRepository
from backend.database.anomaly_repository import AnomalyRepository
from backend.database.prediction_repository import PredictionRepository
from backend.database.system_repository import SystemRepository
from backend.database.models import SensorReading, AnomalyLog, PredictionLog
from backend.services.database_service import DatabaseService


class TestSensorRepository(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_repo.db")
        initialize_database(self.db_path, seed_metadata=True)

        self.db_manager = DatabaseConnectionManager(self.db_path)
        self.repo = SensorRepository(self.db_manager)
        self.anomaly_repo = AnomalyRepository(self.db_manager)
        self.prediction_repo = PredictionRepository(self.db_manager)
        self.system_repo = SystemRepository(self.db_manager)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_single_reading_insertion_and_retrieval(self):
        """Test inserting a single sensor reading and retrieving it accurately."""
        reading = SensorReading(
            timestamp="2026-06-01T12:00:00Z",
            temperature=24.5,
            humidity=50.2,
            smoke=110.0,
            carbon_monoxide=2.4,
            ammonia=1.1,
            nitrogen_oxides=0.025,
            pm25=15.0,
            source="test_node",
            entry_id="901",
        )

        row_id = self.repo.insert_reading(reading)
        self.assertIsNotNone(row_id)

        latest = self.repo.get_latest_reading()
        self.assertIsNotNone(latest)
        self.assertEqual(latest.temperature, 24.5)
        self.assertEqual(latest.humidity, 50.2)
        self.assertEqual(latest.source, "test_node")
        self.assertEqual(latest.entry_id, "901")

    def test_missing_sensor_values_allowed_as_null(self):
        """Test missing readings are stored as NULL and never coerced to 0.0."""
        reading = SensorReading(
            timestamp="2026-06-01T12:05:00Z",
            temperature=22.0,
            humidity=None,  # Missing sensor
            pm25=None,       # Missing sensor
            source="test_nulls",
            entry_id="902",
        )

        row_id = self.repo.insert_reading(reading)
        self.assertIsNotNone(row_id)

        fetched = self.repo.get_latest_reading(source="test_nulls")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.temperature, 22.0)
        self.assertIsNone(fetched.humidity)
        self.assertIsNone(fetched.pm25)

    def test_duplicate_prevention(self):
        """Verify re-inserting the same reading with matching source and entry_id is prevented."""
        reading = SensorReading(
            timestamp="2026-06-01T12:10:00Z",
            temperature=23.0,
            humidity=48.0,
            source="test_source",
            entry_id="905",
        )

        # First insert succeeds
        id1 = self.repo.insert_reading(reading)
        self.assertIsNotNone(id1)

        # Second insert with identical source and entry_id is ignored
        id2 = self.repo.insert_reading(reading)
        self.assertIsNone(id2)

        # Count remains 1
        count = self.repo.get_reading_count(source="test_source")
        self.assertEqual(count, 1)

    def test_bulk_insert_and_duplicate_skip(self):
        """Verify bulk insertion handles new records and ignores duplicates."""
        df = pd.DataFrame({
            "timestamp": ["2026-06-01T10:00:00Z", "2026-06-01T10:01:00Z", "2026-06-01T10:02:00Z"],
            "temperature": [21.0, 21.5, 22.0],
            "humidity": [45.0, 46.0, 47.0],
            "entry_id": ["1", "2", "3"],
        })

        # Insert 3 records
        inserted, skipped = self.repo.bulk_insert_readings(df, source="bulk_test")
        self.assertEqual(inserted, 3)
        self.assertEqual(skipped, 0)

        # Re-insert the same 3 records + 1 new record
        df_extended = pd.DataFrame({
            "timestamp": ["2026-06-01T10:00:00Z", "2026-06-01T10:01:00Z", "2026-06-01T10:02:00Z", "2026-06-01T10:03:00Z"],
            "temperature": [21.0, 21.5, 22.0, 22.5],
            "humidity": [45.0, 46.0, 47.0, 48.0],
            "entry_id": ["1", "2", "3", "4"],
        })

        inserted2, skipped2 = self.repo.bulk_insert_readings(df_extended, source="bulk_test")
        self.assertEqual(inserted2, 1)   # Only record 4 is inserted
        self.assertEqual(skipped2, 3)    # Records 1-3 skipped

        self.assertEqual(self.repo.get_reading_count(source="bulk_test"), 4)

    def test_date_range_queries(self):
        """Test querying readings by start and end timestamps."""
        records = [
            {"timestamp": "2026-06-01T08:00:00Z", "temperature": 19.0, "source": "range_test", "entry_id": "r1"},
            {"timestamp": "2026-06-01T12:00:00Z", "temperature": 24.0, "source": "range_test", "entry_id": "r2"},
            {"timestamp": "2026-06-01T16:00:00Z", "temperature": 23.0, "source": "range_test", "entry_id": "r3"},
            {"timestamp": "2026-06-02T10:00:00Z", "temperature": 20.0, "source": "range_test", "entry_id": "r4"},
        ]
        self.repo.bulk_insert_readings(records, source="range_test")

        df_filtered = self.repo.get_readings_by_date_range(
            start_date="2026-06-01T10:00:00Z",
            end_date="2026-06-01T18:00:00Z",
            source="range_test",
        )

        self.assertEqual(len(df_filtered), 2)
        self.assertEqual(df_filtered["entry_id"].tolist(), ["r2", "r3"])

    def test_sensor_specific_series_query(self):
        """Test retrieving time-series for a single sensor channel."""
        records = [
            {"timestamp": "2026-06-01T10:00:00Z", "pm25": 14.0, "source": "s_test", "entry_id": "p1"},
            {"timestamp": "2026-06-01T10:01:00Z", "pm25": 16.0, "source": "s_test", "entry_id": "p2"},
        ]
        self.repo.bulk_insert_readings(records, source="s_test")

        df_pm = self.repo.get_readings_by_sensor("pm25", limit=10, source="s_test")
        self.assertEqual(len(df_pm), 2)
        self.assertIn("pm25", df_pm.columns)
        self.assertNotIn("temperature", df_pm.columns)

    def test_export_to_csv(self):
        """Test CSV export generates a readable file with expected row count."""
        records = [
            {"timestamp": "2026-06-01T10:00:00Z", "temperature": 22.0, "source": "csv_test", "entry_id": "c1"},
            {"timestamp": "2026-06-01T10:01:00Z", "temperature": 23.0, "source": "csv_test", "entry_id": "c2"},
        ]
        self.repo.bulk_insert_readings(records, source="csv_test")

        export_path = os.path.join(self.temp_dir.name, "exported_readings.csv")
        out_path = self.repo.export_to_csv(export_path, source="csv_test")

        self.assertTrue(os.path.exists(out_path))
        exported_df = pd.read_csv(out_path)
        self.assertEqual(len(exported_df), 2)

    def test_anomaly_and_prediction_logging(self):
        """Test logging and retrieving anomaly and prediction records."""
        # Anomaly log
        anom_id = self.anomaly_repo.insert_anomaly(
            AnomalyLog(
                sensor_name="pm25",
                detected_value=560.9,
                timestamp="2026-06-01T12:00:00Z",
                method="SATURATION",
                severity="CRITICAL",
                explanation="Hardware saturation ceiling reached",
            )
        )
        self.assertIsNotNone(anom_id)
        anoms = self.anomaly_repo.get_recent_anomalies(limit=5)
        self.assertEqual(len(anoms), 1)

        # Prediction log
        pred_id = self.prediction_repo.insert_prediction(
            PredictionLog(
                sensor_name="temperature",
                predicted_value=23.8,
                prediction_timestamp="2026-06-01T13:00:00Z",
                model_name="ARIMA",
                model_version="1.0",
            )
        )
        self.assertIsNotNone(pred_id)
        preds = self.prediction_repo.get_latest_predictions(sensor_name="temperature")
        self.assertEqual(len(preds), 1)

    def test_historical_archive_import_via_database_service(self):
        """Integration test: import physical 5,024-row historical dataset via DatabaseService."""
        service = DatabaseService(db_path=self.db_path)
        service.initialize(seed_metadata=True)

        res = service.import_historical_archive(force=False)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["inserted"], 5024)

        # Confirm idempotent duplicate protection: second import should skip
        res2 = service.import_historical_archive(force=False)
        self.assertEqual(res2["status"], "ALREADY_IMPORTED")
        self.assertEqual(res2["inserted"], 0)

        # Confirm total count in DB is exactly 5,024
        summary = service.get_database_summary()
        self.assertEqual(summary["total_sensor_readings"], 5024)
        self.assertEqual(summary["historical_records"], 5024)


if __name__ == "__main__":
    unittest.main()
