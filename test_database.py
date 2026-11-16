"""
Unit Tests for Database Initialization & Connection Management
Verifies schema creation, indexes, sensor metadata seeding, connection pragmas, and transaction rollback.
"""

import os
import unittest
import sqlite3
import tempfile

from backend.database.db_connection import DatabaseConnectionManager
from backend.database.db_initializer import initialize_database
from backend.database.models import SystemLog


class TestDatabaseInitialization(unittest.TestCase):

    def setUp(self):
        # Use an isolated temporary SQLite database for test purity
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_aerosense.db")
        self.db_manager = DatabaseConnectionManager(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_database_initialization_creates_all_tables(self):
        """Verify initialize_database creates all 5 expected tables and indexes."""
        success = initialize_database(self.db_path, seed_metadata=True)
        self.assertTrue(success)

        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row["name"] for row in cursor.fetchall()]

            expected_tables = [
                "sensor_readings",
                "sensor_metadata",
                "anomaly_logs",
                "prediction_logs",
                "system_logs",
            ]
            for t in expected_tables:
                self.assertIn(t, tables)

    def test_sensor_metadata_seeded(self):
        """Verify default hardware specifications and bounds are seeded for 7 channels."""
        initialize_database(self.db_path, seed_metadata=True)

        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT sensor_id, sensor_name, unit FROM sensor_metadata ORDER BY sensor_id;")
            rows = cursor.fetchall()

            self.assertEqual(len(rows), 7)
            sensor_ids = [r["sensor_id"] for r in rows]
            self.assertIn("field1", sensor_ids)
            self.assertIn("field7", sensor_ids)

    def test_indexes_created(self):
        """Verify query performance and uniqueness indexes exist."""
        initialize_database(self.db_path, seed_metadata=False)

        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index';")
            indexes = [row["name"] for row in cursor.fetchall()]

            self.assertIn("idx_sensor_readings_timestamp", indexes)
            self.assertIn("idx_sensor_readings_source", indexes)
            self.assertIn("idx_sensor_readings_source_entry_uniq", indexes)

    def test_transaction_rollback_on_error(self):
        """Verify database rollback when an exception occurs inside a transaction."""
        initialize_database(self.db_path, seed_metadata=False)

        try:
            with self.db_manager.transaction() as conn:
                conn.execute(
                    "INSERT INTO system_logs (event_type, event_description) VALUES ('TEST', 'Should rollback');"
                )
                # Intentionally trigger an error
                raise ValueError("Simulated failure to test rollback")
        except ValueError:
            pass

        # Verify nothing was committed
        with self.db_manager.get_connection() as conn:
            count = conn.execute("SELECT COUNT(*) FROM system_logs WHERE event_type = 'TEST';").fetchone()[0]
            self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
