"""
Tests for AEROsense APScheduler Background Pipelines.
Validates concurrency locks, scheduled sync execution, duplicate-run prevention,
anomaly detection pipelines, and alert rule evaluation with cooldowns.
"""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from backend.database.db_connection import DatabaseConnectionManager
from backend.database.migrations import run_migrations
from backend.database.models import SensorReading
from backend.scheduler.scheduler import AerosenseScheduler, _SYNC_LOCK, _ANOMALY_LOCK
from backend.services.runs_service import RunsService
from thingspeak_client import ChannelStatus, TelemetryEntry

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REAL_DB_PATH = PROJECT_ROOT / "data" / "aerosense.db"


@pytest.fixture
def scheduler_test_setup(tmp_path: Path):
    copy_db = tmp_path / "aerosense_sched_test.db"
    shutil.copy2(REAL_DB_PATH, copy_db)
    mgr = DatabaseConnectionManager(str(copy_db))
    run_migrations(mgr)

    sched = AerosenseScheduler(db_manager=mgr)
    return sched, mgr


def test_concurrency_lock_prevents_duplicate_runs(scheduler_test_setup):
    sched, mgr = scheduler_test_setup

    # Lock sync lock manually
    _SYNC_LOCK.acquire()
    try:
        res = sched.sync_once()
        assert res["status"] == "SKIPPED"
        assert res["reason"] == "LOCKED"
    finally:
        _SYNC_LOCK.release()

    # Lock anomaly lock manually
    _ANOMALY_LOCK.acquire()
    try:
        res_anom = sched.detect_anomalies_once()
        assert res_anom["status"] == "SKIPPED"
        assert res_anom["reason"] == "LOCKED"
    finally:
        _ANOMALY_LOCK.release()


def test_sync_once_handles_new_telemetry_and_records_run(scheduler_test_setup):
    sched, mgr = scheduler_test_setup

    mock_entry = TelemetryEntry(
        entry_id=987654,
        timestamp=datetime.now(timezone.utc),
        values={
            "field1": 24.5,
            "field2": 52.0,
            "field3": 1400.0,  # Above warning threshold (1200) -> will trigger alert
            "field4": 150.0,
            "field5": 80.0,
            "field6": 60.0,
            "field7": 45.0,
        },
        raw_values={},
        source="thingspeak_live",
    )
    mock_status = ChannelStatus(
        state="LIVE",
        status_label="LIVE",
        status_color="#10B981",
        api_connected=True,
        sensor_active=True,
    )

    with patch("backend.scheduler.scheduler.ThingSpeakClient.fetch_latest", return_value=(mock_entry, mock_status)):
        res1 = sched.sync_once()
        assert res1["status"] == "INSERTED"
        assert res1["rows_affected"] == 1
        assert res1["alerts_fired"] >= 1  # Smoke alert rule triggered

        # Second sync with same entry_id should detect duplicate
        res2 = sched.sync_once()
        assert res2["status"] == "UP_TO_DATE"
        assert res2["rows_affected"] == 0

    # Verify run ledger recorded both runs
    runs_svc = RunsService(mgr)
    runs = runs_svc.list_runs(run_type="scheduled_telemetry_sync", limit=5)
    assert len(runs) >= 2


def test_alert_rule_cooldown_prevents_duplicate_events(scheduler_test_setup):
    sched, mgr = scheduler_test_setup

    reading = SensorReading(
        timestamp=datetime.now(timezone.utc).isoformat(),
        temperature=40.0,  # Threshold for High Ambient Temperature is > 30.0 / 35.0
        humidity=50.0,
        smoke=200.0,
        carbon_monoxide=10.0,
        ammonia=10.0,
        nitrogen_oxides=10.0,
        pm25=10.0,
        source="test",
    )

    # First evaluation triggers alert
    fired_first = sched.evaluate_alert_rules(reading)
    assert fired_first >= 1

    # Immediate second evaluation should be suppressed by cooldown
    fired_second = sched.evaluate_alert_rules(reading)
    assert fired_second == 0


def test_detect_anomalies_once(scheduler_test_setup):
    sched, mgr = scheduler_test_setup

    res = sched.detect_anomalies_once(limit_readings=200)
    assert res["status"] == "SUCCESS"
    assert "anomalies_detected" in res

    # Verify run recorded in ledger
    runs_svc = RunsService(mgr)
    runs = runs_svc.list_runs(run_type="scheduled_anomaly_detection", limit=5)
    assert len(runs) >= 1
    assert runs[0]["status"] == "SUCCESS"


def test_scheduler_lifecycle(scheduler_test_setup):
    sched, mgr = scheduler_test_setup

    assert sched._is_running is False
    sched.start()
    assert sched._is_running is True

    job_ids = [j.id for j in sched.scheduler.get_jobs()]
    assert "job_telemetry_sync" in job_ids
    assert "job_anomaly_detection" in job_ids

    sched.shutdown(wait=False)
    assert sched._is_running is False
