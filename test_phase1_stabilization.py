"""
Phase 1 Stabilization, Performance & Architecture Tests.
Validates logging redaction, SQLite migrations on a DB copy, AQI readiness gate,
ThingSpeak TTL caching & retry/backoff, saved model preloading, and FastAPI /health.
"""

from __future__ import annotations

import logging
import os
import shutil
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.api.main import create_app
from backend.core.logging_config import RedactingJsonFormatter, redact_sensitive_text
from backend.database.db_connection import DatabaseConnectionManager
from backend.database.migrations import run_migrations
from backend.database.sensor_repository import SensorRepository
from backend.services.aqi_readiness import AQIReadinessService
from backend.services.anomaly_service import AnomalyService
from backend.services.prediction_service import PredictionService
from backend.services.runs_service import RunsService
from thingspeak_client import ThingSpeakClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REAL_DB_PATH = PROJECT_ROOT / "data" / "aerosense.db"


def test_logging_redacts_secrets():
    sample = "GET https://api.thingspeak.com/feeds.json?api_key=MYSECRETKEY123&results=5 Authorization: Bearer tok_987"
    redacted = redact_sensitive_text(sample)
    assert "MYSECRETKEY123" not in redacted
    assert "tok_987" not in redacted
    assert "REDACTED" in redacted

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Failed with api_key=XYZ789ABC",
        args=(),
        exc_info=None,
    )
    formatted = RedactingJsonFormatter().format(record)
    assert "XYZ789ABC" not in formatted


def test_migrations_idempotent_and_preserve_real_rows(tmp_path: Path):
    assert REAL_DB_PATH.exists(), "Expected baseline SQLite database at data/aerosense.db"
    copy_db = tmp_path / "aerosense_copy.db"
    shutil.copy2(REAL_DB_PATH, copy_db)

    mgr = DatabaseConnectionManager(str(copy_db))
    repo = SensorRepository(mgr)
    count_before = repo.get_reading_count()

    res1 = run_migrations(mgr)
    assert res1["status"] == "OK"
    assert len(res1["migrations"]) == 3

    # Also verify fresh pre-migration DB runs all 3 migrations cleanly
    fresh_mgr = DatabaseConnectionManager(str(tmp_path / "fresh_init.db"))
    fresh_res = run_migrations(fresh_mgr)
    assert len(fresh_res["applied_now"]) == 3

    count_after_1 = repo.get_reading_count()
    assert count_after_1 == count_before == 5024

    # Second run must be a strict no-op
    res2 = run_migrations(mgr)
    assert res2["applied_now"] == []
    assert repo.get_reading_count() == count_before

    # Verify ADC units preserved for fields 3-7 and AQI readiness initially false
    with mgr.transaction() as conn:
        mappings = {
            r["field_key"]: dict(r)
            for r in conn.execute("SELECT * FROM field_mapping;").fetchall()
        }
        assert mappings["field3"]["unit"] == "ADC"
        assert mappings["field7"]["unit"] == "ADC"
        assert mappings["field7"]["is_calibrated"] == 0

    readiness = AQIReadinessService(mgr).evaluate()
    assert readiness["ready"] is False
    assert readiness["aqi_enabled"] is False
    assert readiness["passed_count"] == 0


def test_aqi_readiness_passes_only_when_all_five_checks_satisfied(tmp_path: Path):
    copy_db = tmp_path / "aerosense_cal.db"
    shutil.copy2(REAL_DB_PATH, copy_db)
    mgr = DatabaseConnectionManager(str(copy_db))
    run_migrations(mgr)

    future_expiry = (datetime.now(timezone.utc) + timedelta(days=90)).isoformat()
    now_iso = datetime.now(timezone.utc).isoformat()

    with mgr.transaction() as conn:
        # Calibrate both pm25 and carbon_monoxide to physical units + verified curves + US_EPA standard
        conn.execute(
            "UPDATE field_mapping SET unit = 'µg/m³', is_calibrated = 1, calibration_date = ? "
            "WHERE sensor_key = 'pm25';",
            (now_iso,),
        )
        conn.execute(
            "UPDATE field_mapping SET unit = 'ppm', is_calibrated = 1, calibration_date = ? "
            "WHERE sensor_key = 'carbon_monoxide';",
            (now_iso,),
        )
        for sensor_key, cal_unit in (("pm25", "µg/m³"), ("carbon_monoxide", "ppm")):
            conn.execute(
                """
                INSERT INTO calibration_records (
                    device_id, sensor_key, method, reference_instrument,
                    calibrated_unit, slope, intercept, calibrated_at, valid_until, is_verified
                ) VALUES ('ESP32-AEROSENSE-MAIN', ?, 'Co-location linear regression', 'Reference BAM-1020',
                          ?, 0.42, 1.5, ?, ?, 1);
                """,
                (sensor_key, cal_unit, now_iso, future_expiry),
            )
        conn.execute(
            "UPDATE app_settings SET setting_value = 'US_EPA' WHERE setting_key = 'aqi_standard';"
        )

    readiness = AQIReadinessService(mgr).evaluate()
    assert readiness["ready"] is True
    assert readiness["passed_count"] == 5
    assert readiness["aqi_standard"] == "US_EPA"


def test_thingspeak_ttl_cache_and_retry_and_no_random_generator():
    assert not hasattr(ThingSpeakClient, "generate_demo_dataset")
    client = ThingSpeakClient(
        channel_id=3540991,
        read_api_key="TEST_KEY",
        cache_ttl_seconds=15.0,
        max_retries=2,
        retry_backoff_seconds=0.01,
    )

    resp_503 = MagicMock(status_code=503, text="Service Unavailable")
    resp_200 = MagicMock(status_code=200)
    resp_200.json.return_value = {
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_id": 999,
        "field1": "24.1",
        "field2": "48.0",
        "field3": "120.0",
        "field4": "95.0",
        "field5": "110.0",
        "field6": "80.0",
        "field7": "42.0",
    }

    with patch.object(client.session, "get", side_effect=[resp_503, resp_200]) as mock_get:
        entry1, status1 = client.fetch_latest()
        assert entry1 is not None
        assert status1.state == "LIVE"
        assert mock_get.call_count == 2

        # Second call within TTL hits cache without issuing another HTTP request
        entry2, _ = client.fetch_latest()
        assert entry2.entry_id == 999
        assert mock_get.call_count == 2


def test_runs_service_and_fastapi_health(tmp_path: Path):
    copy_db = tmp_path / "aerosense_api.db"
    shutil.copy2(REAL_DB_PATH, copy_db)
    mgr = DatabaseConnectionManager(str(copy_db))

    app = create_app(db_manager=mgr)
    with TestClient(app) as test_client:
        runs = RunsService(mgr)
        run_id, out = runs.record_quick_run("test_sync", lambda: {"rows_affected": 3})
        assert run_id.startswith("run_")
        assert out["rows_affected"] == 3
        listed = runs.list_runs(run_type="test_sync", limit=5)
        assert len(listed) == 1
        assert listed[0]["status"] == "SUCCESS"

        r1 = test_client.get("/health")
        assert r1.status_code == 200
        payload = r1.json()
        assert payload["status"] == "ok"
        assert payload["database"]["row_counts"]["sensor_readings"] == 5024
        assert payload["database"]["migrations_applied"] == 3
        assert payload["aqi_readiness"]["ready"] is False

        r2 = test_client.get("/api/v1/health")
        assert r2.status_code == 200


def test_vectorized_anomaly_and_saved_model_preload(tmp_path: Path):
    copy_db = tmp_path / "aerosense_perf.db"
    shutil.copy2(REAL_DB_PATH, copy_db)
    mgr = DatabaseConnectionManager(str(copy_db))

    t0 = time.perf_counter()
    anomaly_svc = AnomalyService(db_manager=mgr)
    df_anom = anomaly_svc.get_anomalies_dataframe(limit=2500)
    anom_ms = (time.perf_counter() - t0) * 1000.0
    assert not df_anom.empty
    assert anom_ms < 1000.0

    pred_svc = PredictionService(db_manager=mgr)
    preloaded = pred_svc.preload_saved_models()
    assert preloaded["count"] >= 1
    assert "temperature" in preloaded["loaded_sensors"]
