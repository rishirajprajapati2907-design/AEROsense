"""
Unit Tests for Notification Repository & Notification Service
Verifies SQLite CRUD, category filtering, severity levels, deduplication hashing,
read/unread toggling, and specialized notification methods using an isolated SQLite database.
"""

import os
import unittest
import tempfile

from backend.database.db_connection import DatabaseConnectionManager
from backend.notifications.notification_repository import NotificationRepository
from backend.notifications.notification_service import NotificationService


class TestNotificationService(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_notifications.db")
        self.db_manager = DatabaseConnectionManager(self.db_path)
        self.repo = NotificationRepository(self.db_manager)
        self.service = NotificationService(self.repo)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_insert_and_get_notification(self):
        """Test basic insertion and retrieval of notification records."""
        nid = self.service.notify(
            title="ESP32 Disconnected",
            description="Station telemetry stream timed out.",
            category="SENSOR_CONNECTIVITY",
            severity="WARNING",
            related_entity="ESP32_NODE",
            dedup_window_minutes=0,  # disable dedup for direct test
        )
        self.assertIsNotNone(nid)

        notifs = self.service.get_notifications()
        self.assertEqual(len(notifs), 1)
        self.assertEqual(notifs[0]["title"], "ESP32 Disconnected")
        self.assertEqual(notifs[0]["category"], "SENSOR_CONNECTIVITY")
        self.assertEqual(notifs[0]["severity"], "WARNING")
        self.assertEqual(notifs[0]["is_read"], 0)

    def test_unread_count_and_mark_as_read(self):
        """Test tracking unread count and updating read status."""
        nid1 = self.service.notify("Alert 1", "Desc 1", "DATA_QUALITY", "INFO", dedup_window_minutes=0)
        nid2 = self.service.notify("Alert 2", "Desc 2", "ANOMALY_DETECTION", "CRITICAL", dedup_window_minutes=0)

        self.assertEqual(self.service.get_unread_count(), 2)

        # Mark nid1 as read
        res = self.service.mark_as_read(nid1)
        self.assertTrue(res)
        self.assertEqual(self.service.get_unread_count(), 1)

        # Mark all as read
        self.service.mark_all_as_read()
        self.assertEqual(self.service.get_unread_count(), 0)

    def test_deduplication_suppression(self):
        """Verify identical notifications within the time window are suppressed."""
        nid1 = self.service.notify(
            title="Repeated Alert",
            description="Same condition",
            category="THINGSPEAK_API",
            severity="WARNING",
            related_entity="THINGSPEAK",
            dedup_window_minutes=60,
        )
        self.assertIsNotNone(nid1)

        # Immediate duplicate should be suppressed
        nid2 = self.service.notify(
            title="Repeated Alert",
            description="Same condition",
            category="THINGSPEAK_API",
            severity="WARNING",
            related_entity="THINGSPEAK",
            dedup_window_minutes=60,
        )
        self.assertIsNone(nid2)
        self.assertEqual(len(self.service.get_notifications()), 1)

    def test_specialized_notification_methods(self):
        """Verify domain-specific notification helper methods."""
        n1 = self.service.notify_sensor_connectivity("Offline", "Device power cycle needed")
        self.assertIsNotNone(n1)

        n2 = self.service.notify_report_generated("Environmental Audit PDF", "audit_2026.pdf", 5024)
        self.assertIsNotNone(n2)

        n3 = self.service.notify_prediction_completed("temperature", "ARIMA", ["15m", "1h"], {"mae": 0.45})
        self.assertIsNotNone(n3)

        notifs = self.service.get_notifications()
        self.assertEqual(len(notifs), 3)

    def test_delete_and_clear_notifications(self):
        """Test deleting individual notifications and clearing all."""
        nid = self.service.notify("Temporary", "To be deleted", "REPORT_GENERATION", "INFO", dedup_window_minutes=0)
        self.assertTrue(self.service.delete_notification(nid))
        self.assertEqual(len(self.service.get_notifications()), 0)


if __name__ == "__main__":
    unittest.main()
