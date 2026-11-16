"""
Tests verifying FastAPI serves the built React SPA and static assets cleanly.
"""

import os
import shutil
from pathlib import Path
from fastapi.testclient import TestClient
from backend.api.main import create_app
from backend.database.db_connection import DatabaseConnectionManager
from backend.database.migrations import run_migrations

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REAL_DB_PATH = PROJECT_ROOT / "data" / "aerosense.db"


def test_spa_and_static_serving(tmp_path):
    copy_db = tmp_path / "aerosense_spa_test.db"
    shutil.copy2(REAL_DB_PATH, copy_db)
    db_mgr = DatabaseConnectionManager(str(copy_db))
    run_migrations(db_mgr)
    app = create_app(db_manager=db_mgr)
    client = TestClient(app)

    # 1. API routes must return JSON, not HTML
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["status"] == "ok"

    api_health = client.get("/api/v1/health")
    assert api_health.status_code == 200
    assert api_health.json()["status"] == "ok"

    # 2. Nonexistent API route returns 404
    missing_api = client.get("/api/v1/does_not_exist")
    assert missing_api.status_code == 404

    # 3. Root returns SPA index.html
    root_resp = client.get("/")
    assert root_resp.status_code == 200
    assert "text/html" in root_resp.headers.get("content-type", "")
    assert "<!doctype html>" in root_resp.text.lower() or "<html" in root_resp.text.lower()

    # 4. Client-side routes return index.html for client routing
    for route in ["/overview", "/live", "/devices", "/analytics", "/predictions", "/settings"]:
        resp = client.get(route)
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("content-type", "")

    # 5. Static assets under /assets/ exist and return 200
    dist_dir = PROJECT_ROOT / "frontend" / "dist"
    assets_dir = dist_dir / "assets"
    if assets_dir.is_dir():
        files = list(assets_dir.iterdir())
        if files:
            first_asset = files[0].name
            asset_resp = client.get(f"/assets/{first_asset}")
            assert asset_resp.status_code == 200


