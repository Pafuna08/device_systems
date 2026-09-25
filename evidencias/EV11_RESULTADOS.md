# Evidencias reales EV11 — Seguridad, middleware y rate limiting

Estas evidencias se han generado directamente contra la API ejecutándose en `http://127.0.0.1:8000` y reflejan respuestas reales del proyecto `device_systems`.

## Capturas disponibles

1. [ev11_01_root_home.png](ev11_01_root_home.png) — bienvenida de la API y acceso a Swagger/ReDoc.
2. [ev11_02_swagger_oauth2.png](ev11_02_swagger_oauth2.png) — documentación Swagger con el esquema OAuth2 visible.
3. [ev11_03_auth_flow.png](ev11_03_auth_flow.png) — registro, login y consulta a `/auth/me` con token JWT.
4. [ev11_04_protected_routes.png](ev11_04_protected_routes.png) — `401` sin token, `401` con token inválido y `403` por permisos insuficientes.
5. [ev11_05_cors_middleware.png](ev11_05_cors_middleware.png) — validación del middleware y CORS con cabeceras `X-App-Name`, `X-Process-Time`, `X-Request-ID` y `Access-Control-Allow-Origin`.
6. [ev11_06_rate_limit_429.png](ev11_06_rate_limit_429.png) — respuesta real de rate limiting con `429 Too Many Requests`.

## Resultado funcional

La validación final del proyecto confirma que la fase EV11 cumple los requisitos de la guía:

- Autenticación OAuth2 + JWT.
- Registro seguro y validación de contraseñas.
- Rutas protegidas con `401` y permisos por rol con `403`.
- Middleware personalizado y CORS configurado correctamente.
- Rate limiting funcionando con `429` al exceder el límite.

## Evidencia de prueba

Se ejecutaron validaciones reales del sistema con `pytest` y con comprobación de humo en vivo, obteniendo resultados exitosos:

- `pytest -q`: `18 passed`.
- `./venv/Scripts/python _tmp_smoke.py`: `25/25 comprobaciones correctas`.
