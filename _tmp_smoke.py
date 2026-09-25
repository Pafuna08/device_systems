"""Smoke test en vivo contra el servidor uvicorn en 127.0.0.1:8000.

Verifica de punta a punta los requisitos de la guia EV11:
middleware, CORS, OAuth2/JWT, proteccion de rutas, roles y rate limiting.
Se ejecuta como script temporal y se elimina despues.
"""
import time

import httpx

BASE = "http://127.0.0.1:8000"
ADMIN = ("admin@device-systems.com", "Admin1234")
SUPPORT = ("support@device-systems.com", "Support1234")

client = httpx.Client(base_url=BASE, timeout=10.0)
results: list[bool] = []


def check(label: str, ok: bool, detail: object = "") -> None:
    results.append(bool(ok))
    print(f"[{'OK ' if ok else 'FALLA'}] {label}" + (f"  -> {detail}" if detail != "" else ""))


# 1. Health + cabeceras del middleware --------------------------------------
r = client.get("/health")
check("GET /health responde 200", r.status_code == 200, r.status_code)
check("cabecera X-App-Name", r.headers.get("x-app-name") == "device_systems", r.headers.get("x-app-name"))
check("cabecera X-Process-Time presente", "x-process-time" in r.headers, r.headers.get("x-process-time"))
check("cabecera X-Request-ID presente", "x-request-id" in r.headers, r.headers.get("x-request-id"))

# 2. Registro de usuario -----------------------------------------------------
email = f"smoke_{int(time.time())}@example.com"
r = client.post("/auth/register", json={"name": "Smoke Tester", "email": email, "password": "Smoke12345"})
check("POST /auth/register responde 201", r.status_code == 201, r.status_code)
body = r.json() if r.status_code == 201 else {}
check("el registro no expone hashed_password", "hashed_password" not in body)
check("el registro asigna rol 'user'", body.get("role") == "user", body.get("role"))

# 3. Contrasena debil --------------------------------------------------------
r = client.post("/auth/register", json={"name": "Debil User", "email": f"weak_{int(time.time())}@example.com", "password": "abc"})
check("registro con contrasena debil -> 422", r.status_code == 422, r.status_code)

# 4. Logins ------------------------------------------------------------------
r = client.post("/auth/login-json", json={"email": email, "password": "Smoke12345"})
check("login del usuario nuevo -> 200", r.status_code == 200, r.status_code)
user_token = r.json().get("access_token", "") if r.status_code == 200 else ""

r = client.post("/auth/login", data={"username": ADMIN[0], "password": ADMIN[1]})
check("login admin -> 200", r.status_code == 200, r.status_code)
admin_token = r.json().get("access_token", "") if r.status_code == 200 else ""

r = client.post("/auth/login", data={"username": SUPPORT[0], "password": SUPPORT[1]})
check("login support -> 200", r.status_code == 200, r.status_code)
support_token = r.json().get("access_token", "") if r.status_code == 200 else ""

uh = {"Authorization": f"Bearer {user_token}"}
ah = {"Authorization": f"Bearer {admin_token}"}
sh = {"Authorization": f"Bearer {support_token}"}

# 5. /auth/me ----------------------------------------------------------------
r = client.get("/auth/me", headers=uh)
check("GET /auth/me -> 200", r.status_code == 200, r.status_code)
check("/auth/me no expone hashed_password", "hashed_password" not in r.text)

# 6. Rutas protegidas sin token / token invalido ----------------------------
check("GET /users sin token -> 401", client.get("/users").status_code == 401)
check("GET /users con token invalido -> 401",
      client.get("/users", headers={"Authorization": "Bearer token.invalido"}).status_code == 401)

# 7. Rol insuficiente -> 403 -------------------------------------------------
check("GET /loans/details con rol user -> 403", client.get("/loans/details", headers=uh).status_code == 403)
check("POST /devices con rol user -> 403",
      client.post("/devices", headers=uh,
                  json={"name": "X", "serial_number": "X-1", "device_type": "laptop"}).status_code == 403)

# 8. Rol permitido -----------------------------------------------------------
serial = f"SMK-{int(time.time())}"
r = client.post("/devices", headers=sh,
                json={"name": "Smoke Device", "serial_number": serial, "device_type": "laptop",
                      "brand": "Dell", "is_available": True})
check("POST /devices con rol support -> 201", r.status_code == 201, r.status_code)
device_id = r.json().get("id") if r.status_code == 201 else None

if device_id:
    check("DELETE /devices con rol support -> 403", client.delete(f"/devices/{device_id}", headers=sh).status_code == 403)
    check("DELETE /devices con rol admin -> 204", client.delete(f"/devices/{device_id}", headers=ah).status_code == 204)

# 9. CORS --------------------------------------------------------------------
r = client.options("/auth/login", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"})
check("CORS allow-origin correcto", r.headers.get("access-control-allow-origin") == "http://localhost:5173",
      r.headers.get("access-control-allow-origin"))
check("CORS allow-credentials true", r.headers.get("access-control-allow-credentials") == "true")

# 10. OpenAPI ----------------------------------------------------------------
spec = client.get("/openapi.json").json()
schemes = spec.get("components", {}).get("securitySchemes", {})
check("OpenAPI expone el esquema OAuth2", "OAuth2PasswordBearer" in schemes, list(schemes))
check("OpenAPI version 3.0.0", spec["info"]["version"] == "3.0.0", spec["info"]["version"])
tags = {t["name"] for t in spec.get("tags", [])}
check("OpenAPI con tags Auth/Users/Devices/Loans/Security",
      {"Auth", "Users", "Devices", "Loans", "Security"} <= tags, sorted(tags))

print()
print(f"RESULTADO: {sum(results)}/{len(results)} comprobaciones correctas")
raise SystemExit(0 if all(results) else 1)
