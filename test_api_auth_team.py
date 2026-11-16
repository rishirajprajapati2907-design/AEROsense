"""
Tests for AEROsense Authentication & Team Management APIs.
Validates login, JWT generation, cookie handling, password rotation, RBAC permission enforcement,
and user CRUD operations.
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
def test_db_mgr(tmp_path: Path) -> DatabaseConnectionManager:
    copy_db = tmp_path / "aerosense_auth_test.db"
    shutil.copy2(REAL_DB_PATH, copy_db)
    mgr = DatabaseConnectionManager(str(copy_db))
    run_migrations(mgr)
    return mgr


@pytest.fixture
def client_and_auth(test_db_mgr: DatabaseConnectionManager):
    app = create_app(db_manager=test_db_mgr)
    auth_svc = AuthService(test_db_mgr)
    # Ensure admin has a known password
    auth_svc.bootstrap_admin_password("AdminSecret123!")
    return TestClient(app), auth_svc


def test_auth_login_and_me(client_and_auth):
    client, auth_svc = client_and_auth

    # 1. Failed login
    res_fail = client.post("/api/v1/auth/login", json={"email": "admin@aerosense.local", "password": "wrong"})
    assert res_fail.status_code == 401

    # 2. Successful login
    res_ok = client.post("/api/v1/auth/login", json={"email": "admin@aerosense.local", "password": "AdminSecret123!"})
    assert res_ok.status_code == 200
    data = res_ok.json()
    assert "access_token" in data
    assert data["user"]["role_name"] == "admin"
    assert "manage:users" in data["user"]["permissions"]
    token = data["access_token"]

    # 3. /me with Bearer token
    res_me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    assert res_me.json()["email"] == "admin@aerosense.local"

    # 4. /me using cookie set during login
    res_cookie = client.get("/api/v1/auth/me")
    assert res_cookie.status_code == 200
    assert res_cookie.json()["id"] == data["user"]["id"]


def test_rbac_permission_guards(client_and_auth):
    client, auth_svc = client_and_auth

    # Create an operator and a viewer
    auth_svc.create_user("operator@test.local", "Operator User", "operator", "OperatorPass123!")
    auth_svc.create_user("viewer@test.local", "Viewer User", "viewer", "ViewerPass123!")

    # Login as viewer
    res_viewer = client.post("/api/v1/auth/login", json={"email": "viewer@test.local", "password": "ViewerPass123!"})
    viewer_token = res_viewer.json()["access_token"]

    # Viewer should be denied from managing team users
    res_denied = client.get("/api/v1/team/users", headers={"Authorization": f"Bearer {viewer_token}"})
    assert res_denied.status_code == 403

    # Login as admin
    res_admin = client.post("/api/v1/auth/login", json={"email": "admin@aerosense.local", "password": "AdminSecret123!"})
    admin_token = res_admin.json()["access_token"]

    # Admin should succeed
    res_allowed = client.get("/api/v1/team/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_allowed.status_code == 200
    users = res_allowed.json()["users"]
    assert len(users) >= 3


def test_team_user_lifecycle(client_and_auth):
    client, auth_svc = client_and_auth
    res_admin = client.post("/api/v1/auth/login", json={"email": "admin@aerosense.local", "password": "AdminSecret123!"})
    token = res_admin.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create new user
    new_user_payload = {
        "email": "engineer@aerosense.local",
        "full_name": "Sensor Engineer",
        "role_name": "operator",
        "password": "EngineerPass123!",
        "must_rotate_password": True,
    }
    res_create = client.post("/api/v1/team/users", json=new_user_payload, headers=headers)
    assert res_create.status_code == 201
    created_id = res_create.json()["id"]
    assert res_create.json()["email"] == "engineer@aerosense.local"

    # 2. Update user
    res_update = client.put(
        f"/api/v1/team/users/{created_id}",
        json={"full_name": "Lead Sensor Engineer", "role_name": "operator"},
        headers=headers,
    )
    assert res_update.status_code == 200
    assert res_update.json()["full_name"] == "Lead Sensor Engineer"

    # 3. Delete user
    res_del = client.delete(f"/api/v1/team/users/{created_id}", headers=headers)
    assert res_del.status_code == 200

    # Verify deletion
    res_verify = client.get("/api/v1/team/users", headers=headers)
    emails = [u["email"] for u in res_verify.json()["users"]]
    assert "engineer@aerosense.local" not in emails


def test_change_password_and_logout(client_and_auth):
    client, auth_svc = client_and_auth
    auth_svc.create_user("temp@test.local", "Temp User", "viewer", "TempSecret123!")

    res_login = client.post("/api/v1/auth/login", json={"email": "temp@test.local", "password": "TempSecret123!"})
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Change password
    res_cp = client.post(
        "/api/v1/auth/change-password",
        json={"old_password": "TempSecret123!", "new_password": "NewSecret456!"},
        headers=headers,
    )
    assert res_cp.status_code == 200

    # Old password fails
    res_fail = client.post("/api/v1/auth/login", json={"email": "temp@test.local", "password": "TempSecret123!"})
    assert res_fail.status_code == 401

    # New password succeeds
    res_new = client.post("/api/v1/auth/login", json={"email": "temp@test.local", "password": "NewSecret456!"})
    assert res_new.status_code == 200

    # Logout
    res_logout = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {res_new.json()['access_token']}"})
    assert res_logout.status_code == 200
