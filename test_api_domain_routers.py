"""
Comprehensive Tests for AEROsense Domain API Routers.
Validates all /api/v1/* routes: Overview, Devices, Telemetry, Analytics,
Predictions, Anomalies, Alerts, Maintenance, Reports, Integrations, Runs, and Settings.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.api.main import create_app
from backend.database.db_connection import DatabaseConnectionManager
from backend.database.migrations import run_migrations
from backend.services.auth_service import AuthService

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REAL_DB_PATH = PROJECT_ROOT / "data" / "aerosense.db"


@pytest.fixture
def test_setup(tmp_path: Path):
    copy_db = tmp_path / "aerosense_domain_test.db"
    shutil.copy2(REAL_DB_PATH, copy_db)
    mgr = DatabaseConnectionManager(str(copy_db))
    run_migrations(mgr)

    app = create_app(db_manager=mgr)
    auth_svc = AuthService(mgr)
    auth_svc.bootstrap_admin_password("AdminSecret123!")

    client = TestClient(app)
    res_login = client.post("/api/v1/auth/login", json={"email": "admin@aerosense.local", "password": "AdminSecret123!"})
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    return client, headers, mgr


def test_overview_endpoints(test_setup):
    client, headers, mgr = test_setup

    res = client.get("/api/v1/overview/kpi")
    assert res.status_code == 200
    data = res.json()

    # Validate device state
    assert "device" in data
    assert data["device"]["state"] in ("LIVE", "STALE", "OFFLINE")

    # Validate strict units
    metrics = data["latest_reading"]["metrics"]
    assert metrics["temperature"]["unit"] == "°C"
    assert metrics["humidity"]["unit"] == "%"
    assert metrics["smoke"]["unit"] == "ADC"
    assert metrics["carbon_monoxide"]["unit"] == "ADC"
    assert metrics["pm25"]["unit"] == "ADC"

    # Validate AQI gated
    assert data["aqi_gate"]["is_enabled"] is False
    assert data["aqi_gate"]["passed_checks"] == 0

    # Recent readings
    res_rec = client.get("/api/v1/overview/recent-readings?limit=5")
    assert res_rec.status_code == 200
    assert len(res_rec.json()["readings"]) == 5
    assert res_rec.json()["units"]["smoke"] == "ADC"


def test_devices_endpoints(test_setup):
    client, headers, mgr = test_setup

    # List devices
    res = client.get("/api/v1/devices")
    assert res.status_code == 200
    devices = res.json()["devices"]
    assert len(devices) >= 1
    assert devices[0]["device_id"] == "ESP32-AEROSENSE-MAIN"
    assert "freshness_label" in devices[0]

    # Device detail
    res_det = client.get("/api/v1/devices/ESP32-AEROSENSE-MAIN")
    assert res_det.status_code == 200
    detail = res_det.json()
    assert len(detail["sensors"]) == 7


def test_telemetry_endpoints(test_setup):
    client, headers, mgr = test_setup

    # Latest
    res_latest = client.get("/api/v1/telemetry/latest")
    assert res_latest.status_code == 200
    lat = res_latest.json()
    assert lat["channels"]["pm25"]["unit"] == "ADC"

    # History downsampling
    res_hist = client.get("/api/v1/telemetry/history?interval=auto&max_points=50")
    assert res_hist.status_code == 200
    hist = res_hist.json()
    assert len(hist["data"]) > 0
    assert len(hist["data"]) <= 100
    assert hist["units"]["smoke"] == "ADC"

    # Channels
    res_ch = client.get("/api/v1/telemetry/channels")
    assert res_ch.status_code == 200
    assert len(res_ch.json()["channels"]) == 7


def test_analytics_endpoints(test_setup):
    client, headers, mgr = test_setup

    # Stats
    res_stats = client.get("/api/v1/analytics/stats")
    assert res_stats.status_code == 200
    stats = res_stats.json()["statistics"]
    assert "temperature" in stats
    assert stats["temperature"]["mean"] is not None

    # Correlation
    res_corr = client.get("/api/v1/analytics/correlation?method=pearson")
    assert res_corr.status_code == 200
    corr = res_corr.json()
    assert len(corr["correlation_matrix"]) > 0

    # Trends
    res_trend = client.get("/api/v1/analytics/trends?sensor=temperature")
    assert res_trend.status_code == 200
    assert "temperature" in res_trend.json()["trends"]

    # Period comparison
    res_comp = client.get("/api/v1/analytics/comparison?days=7")
    assert res_comp.status_code == 200


def test_predictions_endpoints(test_setup):
    client, headers, mgr = test_setup

    # Models overview
    res_mod = client.get("/api/v1/predictions/models")
    assert res_mod.status_code == 200
    mod = res_mod.json()
    assert "temperature" in mod["best_models"]

    # Forecast
    res_fc = client.post(
        "/api/v1/predictions/forecast",
        json={"sensor_name": "temperature", "horizon": "1h", "persist": False},
    )
    assert res_fc.status_code == 200
    fc = res_fc.json()
    assert fc["success"] is True
    assert len(fc["predictions"]) == 60
    assert "explanation" in fc

    # Logs
    res_logs = client.get("/api/v1/predictions/logs?limit=10")
    assert res_logs.status_code == 200


def test_anomalies_and_alerts_endpoints(test_setup):
    client, headers, mgr = test_setup

    # Anomalies list & summary
    res_anom = client.get("/api/v1/anomalies/events?limit=10")
    assert res_anom.status_code == 200
    assert len(res_anom.json()["events"]) == 10

    res_sum = client.get("/api/v1/anomalies/summary")
    assert res_sum.status_code == 200
    assert res_sum.json()["summary"]["total_anomalies"] >= 1000

    # Alerts rules
    res_rules = client.get("/api/v1/alerts/rules")
    assert res_rules.status_code == 200
    rules = res_rules.json()["rules"]
    assert len(rules) >= 5

    # Create new rule
    new_rule = {
        "rule_name": "Test High PM25 Rule",
        "sensor_key": "pm25",
        "condition_op": "gt",
        "warning_threshold": 1200.0,
        "critical_threshold": 2000.0,
        "cooldown_minutes": 10,
        "severity": "CRITICAL",
        "is_enabled": True,
    }
    res_cr = client.post("/api/v1/alerts/rules", json=new_rule, headers=headers)
    assert res_cr.status_code == 201
    rule_id = res_cr.json()["rule_id"]

    # Update rule
    res_up = client.put(f"/api/v1/alerts/rules/{rule_id}", json={"warning_threshold": 1300.0}, headers=headers)
    assert res_up.status_code == 200

    # Delete rule
    res_del = client.delete(f"/api/v1/alerts/rules/{rule_id}", headers=headers)
    assert res_del.status_code == 200


def test_maintenance_and_reports_endpoints(test_setup):
    client, headers, mgr = test_setup

    # 1. Maintenance task creation and listing
    task_payload = {
        "title": "Clean optical sensor lens",
        "device_id": "ESP32-AEROSENSE-MAIN",
        "sensor_key": "pm25",
        "task_type": "CLEANING",
        "priority": "HIGH",
    }
    res_task = client.post("/api/v1/maintenance/tasks", json=task_payload, headers=headers)
    assert res_task.status_code == 201
    task_id = res_task.json()["task_id"]

    res_tasks = client.get("/api/v1/maintenance/tasks")
    assert res_tasks.status_code == 200
    assert any(t["id"] == task_id for t in res_tasks.json()["tasks"])

    # 2. Report generation (CSV) and download
    rep_payload = {"title": "Test Audit CSV", "report_format": "csv"}
    res_rep = client.post("/api/v1/reports/generate", json=rep_payload, headers=headers)
    assert res_rep.status_code == 201
    rep_id = res_rep.json()["report_id"]

    res_dl = client.get(f"/api/v1/reports/{rep_id}/download")
    assert res_dl.status_code == 200
    assert "timestamp" in res_dl.text


def test_integrations_runs_settings_endpoints(test_setup):
    client, headers, mgr = test_setup

    # Integrations
    res_ts = client.get("/api/v1/integrations/thingspeak")
    assert res_ts.status_code == 200
    assert "channel_id" in res_ts.json()

    # Runs list
    res_runs = client.get("/api/v1/runs", headers=headers)
    assert res_runs.status_code == 200
    assert "runs" in res_runs.json()

    # Activity logs
    res_logs = client.get("/api/v1/activity-logs", headers=headers)
    assert res_logs.status_code == 200
    assert "logs" in res_logs.json()

    # Settings
    res_set = client.get("/api/v1/settings")
    assert res_set.status_code == 200
    assert "settings" in res_set.json()

    # AQI readiness audit
    res_aqi = client.get("/api/v1/settings/aqi-readiness")
    assert res_aqi.status_code == 200
    assert res_aqi.json()["ready"] is False
    assert len(res_aqi.json()["checks"]) == 5
