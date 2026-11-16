"""
Unit Tests for Database Backup and Recovery Service (Phase 10)
"""

import os
import shutil
import tempfile
import unittest
import sqlite3
from backend.database.db_initializer import initialize_database
from backend.database.backup_service import DatabaseBackupService


class TestDatabaseBackupService(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_aerosense.db")
        self.backup_dir = os.path.join(self.test_dir, "backups")
        
        initialize_database(self.db_path, seed_metadata=True)
        # Seed a test record
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO sensor_readings (timestamp, temperature, humidity, source) VALUES (?, ?, ?, ?)",
            ("2026-11-09T10:00:00Z", 24.5, 48.2, "test_seed")
        )
        conn.commit()
        conn.close()

        self.service = DatabaseBackupService(db_path=self.db_path, backup_dir=self.backup_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_create_backup_success(self):
        result = self.service.create_backup(label="unit_test")
        self.assertEqual(result["status"], "SUCCESS")
        self.assertTrue(os.path.exists(result["backup_path"]))
        self.assertTrue(result["integrity"]["healthy"])
        self.assertGreaterEqual(result["integrity"]["table_counts"]["sensor_readings"], 1)

    def test_verify_integrity_valid_and_missing(self):
        # Valid database
        res = self.service.verify_integrity()
        self.assertTrue(res["healthy"])
        self.assertEqual(res["pragma_status"], "ok")

        # Missing database
        res_missing = self.service.verify_integrity(os.path.join(self.test_dir, "nonexistent.db"))
        self.assertFalse(res_missing["healthy"])

    def test_restore_backup(self):
        backup_res = self.service.create_backup(label="pre_corrupt")
        backup_path = backup_res["backup_path"]

        # Modify original database
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM sensor_readings;")
        conn.commit()
        conn.close()

        # Verify deletion
        conn = sqlite3.connect(self.db_path)
        count = conn.execute("SELECT COUNT(*) FROM sensor_readings;").fetchone()[0]
        conn.close()
        self.assertEqual(count, 0)

        # Restore from backup
        restore_res = self.service.restore_backup(backup_path)
        self.assertEqual(restore_res["status"], "RESTORED")

        # Check records restored
        conn = sqlite3.connect(self.db_path)
        restored_count = conn.execute("SELECT COUNT(*) FROM sensor_readings;").fetchone()[0]
        conn.close()
        self.assertEqual(restored_count, 1)

    def test_list_backups(self):
        self.service.create_backup(label="b1")
        self.service.create_backup(label="b2")
        backups = self.service.list_backups()
        self.assertEqual(len(backups), 2)
        self.assertTrue(backups[0]["filename"].endswith(".db"))


if __name__ == "__main__":
    unittest.main()
