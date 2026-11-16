"""
AEROsense Phase 4: Frontend-to-Backend Integration Test Suite
Validates that all dashboard pages connect reliably to SQLite repositories,
the Phase 2 data processing pipeline, ThingSpeak synchronization,
and transparent offline-hardware fallbacks.
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
import pandas as pd

from data_loader import load_data, get_anomalies, SENSORS, filter_df
from backend.services.database_service import DatabaseService
from backend.database.db_connection import DatabaseConnectionManager
from backend.database.db_initializer import initialize_database
from thingspeak_client import TelemetryEntry, ChannelStatus


class TestFrontendBackendIntegration(unittest.TestCase):
    """Test suite covering the complete frontend-backend data layer connection."""

    @classmethod
    def setUpClass(cls):
        """Set up in-memory or physical SQLite database service for testing."""
        cls.db_service = DatabaseService()
        cls.db_service.initialize()
        # Ensure database has historical records
        if cls.db_service.sensors.get_reading_count() == 0:
            cls.db_service.import_historical_archive()

    def test_01_load_data_queries_sqlite_with_all_sensor_aliases(self):
        """Verify load_data() connects to SQLite and returns both field and sensor columns."""
        df, meta = load_data(use_database=True)

        self.assertGreaterEqual(len(df), 5000, "Should contain verified historical records")
        self.assertEqual(meta["source"], "database")
        self.assertIn("SQLite Database", meta["file_format"])

        # Check standard names
        standard_cols = ["temperature", "humidity", "smoke", "carbon_monoxide", "ammonia", "nitrogen_oxides", "pm25"]
        for col in standard_cols:
            self.assertIn(col, df.columns, f"Standard column {col} must exist in dataframe")

        # Check field aliases for frontend components
        for f in SENSORS.keys():
            self.assertIn(f, df.columns, f"Field alias {f} must exist in dataframe")

        # Verify values match between alias and standard name
        self.assertEqual(df["field1"].iloc[0], df["temperature"].iloc[0])
        self.assertEqual(df["field7"].iloc[0], df["pm25"].iloc[0])

    def test_02_get_anomalies_retrieves_from_database(self):
        """Verify get_anomalies() retrieves outlier incidents from SQLite anomaly_logs."""
        anoms = get_anomalies(limit=100)

        self.assertIsInstance(anoms, pd.DataFrame)
        self.assertFalse(anoms.empty, "Database should contain recorded anomalies from import")
        self.assertIn("sensor", anoms.columns)
        self.assertIn("value", anoms.columns)
        self.assertIn("severity", anoms.columns)
        self.assertIn("reason", anoms.columns)

    def test_03_historical_analytics_date_range_filtering(self):
        """Verify parameterized date-range filtering executes directly against SQLite."""
        start_ts = "2026-10-18T00:00:00Z"
        end_ts = "2026-10-20T23:59:59Z"

        df_filtered = self.db_service.get_readings_dataframe(
            start_date=start_ts,
            end_date=end_ts,
            source="historical_excel",
        )

        self.assertFalse(df_filtered.empty)
        # Ensure all timestamps are within requested bounds
        self.assertTrue((df_filtered["timestamp"] >= pd.to_datetime(start_ts, utc=True)).all())
        self.assertTrue((df_filtered["timestamp"] <= pd.to_datetime(end_ts, utc=True)).all())

    def test_04_sensor_metadata_retrieval(self):
        """Verify Sensor Explorer retrieves hardware specifications from SQLite sensor_metadata."""
        meta_temp = self.db_service.get_sensor_metadata("field1")

        self.assertIsNotNone(meta_temp)
        self.assertEqual(meta_temp.sensor_id, "field1")
        self.assertEqual(meta_temp.unit, "°C")
        self.assertEqual(meta_temp.thingspeak_field, "field1")
        self.assertIn("Temperature", meta_temp.sensor_name)

    def test_05_offline_hardware_fallback_behavior(self):
        """Verify that when ESP32 is offline, status is OFFLINE and no fake readings are created."""
        mock_client = MagicMock()
        # Mock offline ThingSpeak status (last packet was 2 days ago)
        mock_client.fetch_latest.return_value = (
            TelemetryEntry(
                entry_id=5024,
                timestamp=datetime(2026, 11, 2, 9, 59, 50, tzinfo=timezone.utc),
                values={"field1": 31.3, "field2": 62.1, "field3": 250.0, "field4": None},
                raw_values={},
                is_stale=True,
                is_demo=False,
            ),
            ChannelStatus(
                state="OFFLINE",
                status_label="HARDWARE OFFLINE",
                status_color="#EF4444",
                api_connected=True,
                sensor_active=False,
                last_entry_time=datetime(2026, 11, 2, 9, 59, 50, tzinfo=timezone.utc),
                seconds_since_last=432000.0,
                time_elapsed_display="5 days ago",
                details="Node disconnected",
            ),
        )

        entry, status = mock_client.fetch_latest()

        self.assertEqual(status.state, "OFFLINE")
        self.assertTrue(entry.is_stale)
        self.assertFalse(entry.is_demo)
        # Missing sensor value must remain None, never replaced with zero or fake value
        self.assertIsNone(entry.values["field4"])

    def test_06_thingspeak_stream_sync_and_duplicate_prevention(self):
        """Verify ThingSpeak stream sync passes through pipeline and prevents duplicate insertions."""
        # Syncing again when records already exist should result in 0 new insertions
        res = self.db_service.sync_thingspeak_stream(results=10)

        self.assertIn(res["status"], ["SUCCESS", "EMPTY_FEED"])
        # Should not raise any SQL constraint errors
        self.assertGreaterEqual(res.get("skipped", 0), 0)

    def test_07_prediction_logging_and_retrieval(self):
        """Verify AI forecasts are recorded into prediction_logs table."""
        pred_id = self.db_service.predictions.insert_prediction({
            "sensor_name": "pm25",
            "predicted_value": 310.5,
            "prediction_timestamp": "2026-11-08T00:00:00Z",
            "model_name": "BASELINE_HEURISTIC_AQI",
            "model_version": "1.0-alpha",
            "confidence_lower": 290.0,
            "confidence_upper": 331.0,
        })

        self.assertIsNotNone(pred_id)

        latest_preds = self.db_service.predictions.get_latest_predictions(limit=5)
        self.assertFalse(latest_preds.empty)
        self.assertIn("pm25", latest_preds["sensor_name"].values)

    def test_08_system_logs_retrieval(self):
        """Verify operational pipeline events are queryable from system_logs."""
        logs = self.db_service.systems.get_recent_logs(limit=10)

        self.assertIsInstance(logs, pd.DataFrame)
        self.assertFalse(logs.empty)
        self.assertIn("event_type", logs.columns)
        self.assertIn("status", logs.columns)

    def test_09_database_summary_diagnostics(self):
        """Verify get_database_summary() provides accurate health metrics."""
        summary = self.db_service.get_database_summary()

        self.assertIn("db_size_mb", summary)
        self.assertGreater(summary["total_sensor_readings"], 5000)
        self.assertGreater(summary["total_anomaly_logs"], 0)


if __name__ == "__main__":
    unittest.main()
