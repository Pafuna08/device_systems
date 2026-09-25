"""
Pruebas funcionales de device_systems - EV10 (CRUD/Alembic) + EV11 (Seguridad).

Cubre los 15 escenarios minimos de la Fase 13 de la guia:
registro, login, /auth/me, rutas protegidas, roles, CORS, middleware
y rate limiting.
"""
import os
import subprocess
import sys
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.middlewares.rate_limiter import limiter

client = TestClient(app)

ADMIN_EMAIL = "admin@device-systems.com"
ADMIN_PASSWORD = "Admin1234"
SUPPORT_EMAIL = "support@device-systems.com"
SUPPORT_PASSWORD = "Support1234"


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Evita que el limite de peticiones de un test afecte a los demas."""
    limiter.reset()
    yield


def _login(email: str, password: str) -> str:
    response = client.post("/auth/login", data={"username": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _register_user(role: str = "user") -> tuple[str, str]:
    """Registra un usuario nuevo (siempre rol 'user' via /auth/register) y retorna (email, token)."""
    email = f"pytest_{uuid4().hex[:10]}@example.com"
    response = client.post(
        "/auth/register",
        json={"name": "Usuario Pytest", "email": email, "password": "Pytest1234"},
    )
    assert response.status_code == 201, response.text
    token = _login(email, "Pytest1234")
    return email, token


def test_swagger_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_exposes_oauth2_scheme():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    assert "OAuth2PasswordBearer" in spec.get("components", {}).get("securitySchemes", {})
    assert "/auth/login" in spec["paths"]
    assert "/auth/register" in spec["paths"]


def test_migrations_history_includes_security_revision():
    migration_dir = os.path.join("alembic", "versions")
    assert os.path.isdir(migration_dir)
    migration_files = os.listdir(migration_dir)
    assert any("create_devices_and_loans_tables" in name for name in migration_files)
    assert any("add_authentication_fields_to_users" in name for name in migration_files)

    history = subprocess.run(
        [sys.executable, "-m", "alembic", "history"],
        capture_output=True,
        text=True,
        cwd=".",
    )
    assert history.returncode == 0, history.stderr or history.stdout
    assert "create devices and loans tables" in history.stdout
    assert "add authentication fields to users" in history.stdout


# --- Fase 13: escenarios minimos -------------------------------------------

def test_01_register_user():
    email = f"pytest_{uuid4().hex[:10]}@example.com"
    response = client.post(
        "/auth/register",
        json={"name": "Usuario Registro", "email": email, "password": "Pytest1234"},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["email"] == email
    assert body["role"] == "user"
    assert "hashed_password" not in body


def test_02_register_weak_password_rejected():
    response = client.post(
        "/auth/register",
        json={"name": "Debil", "email": f"pytest_{uuid4().hex[:8]}@example.com", "password": "abc"},
    )
    assert response.status_code == 422


def test_03_register_duplicate_email_rejected():
    email = f"pytest_{uuid4().hex[:10]}@example.com"
    payload = {"name": "Duplicado", "email": email, "password": "Pytest1234"}
    first = client.post("/auth/register", json=payload)
    assert first.status_code == 201
    second = client.post("/auth/register", json=payload)
    assert second.status_code == 400


def test_04_login_correct():
    email, token = _register_user()
    assert token


def test_05_login_wrong_password():
    email = f"pytest_{uuid4().hex[:10]}@example.com"
    client.post("/auth/register", json={"name": "X", "email": email, "password": "Pytest1234"})
    response = client.post("/auth/login", data={"username": email, "password": "Incorrecta1"})
    assert response.status_code == 401


def test_06_auth_me():
    email, token = _register_user()
    response = client.get("/auth/me", headers=_auth_header(token))
    assert response.status_code == 200
    assert response.json()["email"] == email


def test_07_protected_route_without_token():
    response = client.get("/users")
    assert response.status_code == 401


def test_08_protected_route_with_invalid_token():
    response = client.get("/users", headers=_auth_header("token.invalido.123"))
    assert response.status_code == 401


def test_09_user_without_permissions_forbidden():
    _, token = _register_user()
    response = client.get("/loans/details", headers=_auth_header(token))
    assert response.status_code == 403


def test_10_create_device_with_allowed_role():
    support_token = _login(SUPPORT_EMAIL, SUPPORT_PASSWORD)
    response = client.post(
        "/devices",
        headers=_auth_header(support_token),
        json={
            "name": "Camara Logitech",
            "serial_number": f"CAM-{uuid4().hex[:8].upper()}",
            "device_type": "camara",
            "brand": "Logitech",
            "is_available": True,
        },
    )
    assert response.status_code == 201, response.text


def test_11_delete_device_with_forbidden_role():
    admin_token = _login(ADMIN_EMAIL, ADMIN_PASSWORD)
    create_resp = client.post(
        "/devices",
        headers=_auth_header(admin_token),
        json={
            "name": "Monitor LG",
            "serial_number": f"MON-{uuid4().hex[:8].upper()}",
            "device_type": "monitor",
            "brand": "LG",
            "is_available": True,
        },
    )
    device_id = create_resp.json()["id"]

    _, user_token = _register_user()
    denied = client.delete(f"/devices/{device_id}", headers=_auth_header(user_token))
    assert denied.status_code == 403

    cleanup = client.delete(f"/devices/{device_id}", headers=_auth_header(admin_token))
    assert cleanup.status_code == 204


def test_12_cors_configuration():
    response = client.options(
        "/devices",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_13_custom_middleware_headers():
    response = client.get("/health")
    assert response.headers.get("x-app-name") == "device_systems"
    assert "x-process-time" in response.headers
    assert "x-request-id" in response.headers


def test_14_rate_limiting_triggers_429():
    last_status = None
    for _ in range(7):
        resp = client.post(
            "/auth/login",
            data={"username": "nadie@example.com", "password": "Whatever1"},
        )
        last_status = resp.status_code
    assert last_status == 429


def test_15_full_flow_users_devices_loans():
    admin_token = _login(ADMIN_EMAIL, ADMIN_PASSWORD)
    support_token = _login(SUPPORT_EMAIL, SUPPORT_PASSWORD)
    _, user_token = _register_user()

    device_resp = client.post(
        "/devices",
        headers=_auth_header(support_token),
        json={
            "name": "Laptop Prueba E2E",
            "serial_number": f"E2E-{uuid4().hex[:8].upper()}",
            "device_type": "laptop",
            "brand": "Dell",
            "is_available": True,
        },
    )
    assert device_resp.status_code == 201
    device_id = device_resp.json()["id"]

    me_resp = client.get("/auth/me", headers=_auth_header(user_token))
    user_id = me_resp.json()["id"]

    loan_resp = client.post(
        "/loans",
        headers=_auth_header(user_token),
        json={"user_id": user_id, "device_id": device_id, "status": "active"},
    )
    assert loan_resp.status_code == 201, loan_resp.text
    loan_id = loan_resp.json()["id"]

    details_denied = client.get("/loans/details", headers=_auth_header(user_token))
    assert details_denied.status_code == 403

    details_ok = client.get("/loans/details", headers=_auth_header(admin_token))
    assert details_ok.status_code == 200

    return_denied = client.patch(f"/loans/{loan_id}/return", headers=_auth_header(user_token))
    assert return_denied.status_code == 403

    return_ok = client.patch(f"/loans/{loan_id}/return", headers=_auth_header(support_token))
    assert return_ok.status_code == 200
    assert return_ok.json()["status"] == "returned"

    device_after = client.get(f"/devices/{device_id}", headers=_auth_header(admin_token))
    assert device_after.status_code == 200
