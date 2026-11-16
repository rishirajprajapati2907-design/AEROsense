"""
Unit Tests for Daily/Weekly Summaries & Notification Rules
Verifies diurnal aggregations, peak hours, weekly compliance scores, and rule trigger evaluations.
"""

import os
import unittest
import tempfile
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from backend.database.db_connection import DatabaseConnectionManager
from backend.notifications.notification_repository import NotificationRepository
from backend.notifications.notification_service import NotificationService
from backend.notifications.notification_rules import NotificationRules
from backend.reporting.daily_report import DailySummaryReport
from backend.reporting.weekly_report import WeeklySummaryReport


class TestReportingAndRules(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_rules.db")
        self.db_manager = DatabaseConnectionManager(self.db_path)
        self.repo = NotificationRepository(self.db_manager)
        self.notif_service = NotificationService(self.repo)
        self.rules = NotificationRules(self.notif_service)

        self.daily_reporter = DailySummaryReport()
        self.weekly_reporter = WeeklySummaryReport()

        # Build 7-day test dataframe
        dates = pd.date_range("2026-06-01 00:00", periods=7*24, freq="1h")
        self.df_7days = pd.DataFrame({
            "timestamp": [d.strftime("%Y-%m-%d %H:%M:%S") for d in dates],
            "temperature": np.random.uniform(21.0, 25.0, len(dates)),
            "humidity": np.random.uniform(40.0, 55.0, len(dates)),
            "smoke": np.random.uniform(90.0, 110.0, len(dates)),
            "carbon_monoxide": np.random.uniform(1.0, 2.5, len(dates)),
            "ammonia": np.random.uniform(0.5, 1.2, len(dates)),
            "nitrogen_oxides": np.random.uniform(0.01, 0.03, len(dates)),
            "pm25": np.random.uniform(10.0, 20.0, len(dates)),
            "source": "simulated_historical",
        })

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_daily_summary_aggregation(self):
        """Test daily aggregation calculations for a single date."""
        target_date = "2026-06-02"
        anomalies = [
            {"sensor_name": "carbon_monoxide", "timestamp": "2026-06-02 14:00:00", "severity": "WARNING"},
        ]
        res = self.daily_reporter.generate_daily_summary(self.df_7days, target_date, anomalies)

        self.assertEqual(res["date"], target_date)
        self.assertEqual(res["total_readings"], 24)
        self.assertEqual(res["anomaly_count"], 1)
        self.assertIn("temperature", res["sensor_stats"])
        self.assertIn("peak_hours", res)
        self.assertTrue(len(res["observations"]) > 0)

    def test_weekly_summary_aggregation(self):
        """Test 7-day rolling window weekly review."""
        res = self.weekly_reporter.generate_weekly_summary(self.df_7days, end_date="2026-06-07")

        self.assertEqual(len(res["daily_breakdown"]), 7)
        self.assertTrue(res["total_readings"] > 100)
        self.assertIn("weekly_grade", res)
        self.assertIn("trend_direction", res)
        self.assertTrue(res["overall_score"] > 50)

    def test_notification_rules_connectivity(self):
        """Test rule trigger when sensor stream is offline or stale."""
        class MockSource:
            is_offline = True
            is_stale = False
            mode = "HISTORICAL"

        nid = self.rules.check_sensor_connectivity(MockSource())
        self.assertIsNotNone(nid)

        notifs = self.notif_service.get_notifications()
        self.assertEqual(len(notifs), 1)
        self.assertEqual(notifs[0]["category"], "SENSOR_CONNECTIVITY")
        self.assertIn("Offline", notifs[0]["title"])

    def test_notification_rules_data_quality(self):
        """Test rule trigger on degraded data quality."""
        bad_quality_report = {
            "completeness_percentage": 78.5,
            "missing_percentage": 21.5,
            "invalid_rows_count": 80,
        }
        nid = self.rules.check_data_quality(bad_quality_report)
        self.assertIsNotNone(nid)

        notifs = self.notif_service.get_notifications()
        self.assertEqual(notifs[0]["category"], "DATA_QUALITY")

    def test_notification_rules_anomaly_cluster(self):
        """Test rule trigger on anomaly clusters."""
        anomaly_list = [{"sensor_name": "smoke"}] * 7
        nids = self.rules.check_anomaly_clusters(anomaly_list, cluster_threshold=5)
        self.assertEqual(len(nids), 1)

        notifs = self.notif_service.get_notifications()
        self.assertEqual(notifs[0]["category"], "ANOMALY_DETECTION")
        self.assertIn("Smoke", notifs[0]["title"])


if __name__ == "__main__":
    unittest.main()
