# Evidencias Funcionales — Actividad EV10 (FastAPI Avanzado)

**Actividad:** GA1-220501096-01-AA1-EV10  
**Proyecto:** `device_systems`  
**Tecnologías:** FastAPI, SQLAlchemy 2, Alembic, SQLite, Pydantic v2, Pytest  
**Fecha de Verificación:** 22 de septiembre de 2026  

---

## 1. Migraciones con Alembic

Comandos verificados en el entorno:

```text
> alembic current
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
cff4dc36cc7a (head)

> alembic history --verbose
Rev: cff4dc36cc7a (head)
Parent: <base>
Path: alembic\versions\cff4dc36cc7a_create_devices_and_loans_tables.py
    create devices and loans tables
    Create Date: 2026-09-15 18:49:06.369425
```

---

## 2. Escenario Completo de Validación Funcional

Las siguientes operaciones se verificaron contra la API en vivo y mediante `FastAPI TestClient`:

| Operación / Endpoint | Estado HTTP | Resultado Verificado |
| :--- | :---: | :--- |
| `POST /users` | **201 Created** | Usuario creado con ID asignado y correo validado. |
| `POST /devices` | **201 Created** | Dispositivo registrado con serial único y disponibilidad en `True`. |
| `POST /loans` | **201 Created** | Préstamo registrado; dispositivo pasa automáticamente a `is_available: false`. |
| `POST /loans` (equipo ocupado) | **409 Conflict** | Bloqueo exitoso con mensaje: *"El dispositivo no está disponible para préstamo"*. |
| `GET /loans/details` | **200 OK** | Consulta con Joins entre `loans`, `users` y `devices` con datos anidados completos. |
| `GET /loans/details?status=active&device_type=laptop` | **200 OK** | Filtro combinado por estado y tipo de equipo. |
| `GET /users/{user_id}/loans` | **200 OK** | Historial de préstamos asociados a un usuario específico. |
| `GET /devices/{device_id}/loans` | **200 OK** | Historial de préstamos asociados a un dispositivo. |
| `PATCH /loans/{loan_id}/return` | **200 OK** | Estado cambia a `returned`, asigna `return_date` y libera el equipo (`is_available: true`). |
| `PATCH /loans/{loan_id}/return` (repetido) | **409 Conflict** | Error de regla de negocio: *"El préstamo ya fue devuelto"*. |
| `GET /devices/{device_id}` | **200 OK** | Confirmación de `is_available: true` tras la devolución. |
| `GET /loans?status=invalid` | **422 Unprocessable Entity** | Validación estricta por esquema literal (`active`, `returned`, `overdue`). |

---

## 3. Pruebas Automatizadas con Pytest

```text
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\PABLO 08\OneDrive\Escritorio\Python Avanzado\device_systems
plugins: anyio-4.14.2
collected 3 items

tests/test_device_systems_api.py::test_swagger_docs_available PASSED     [ 33%]
tests/test_device_systems_api.py::test_users_endpoint_lists_users PASSED [ 66%]
tests/test_device_systems_api.py::test_phase_13_minimal_functional_scenarios PASSED [100%]

======================== 3 passed, 4 warnings in 2.64s ========================
```

---

## 4. Índice de Capturas de Pantalla Generadas

Todas las capturas se encuentran almacenadas en el directorio `evidencias/` y embebidas en el `README.md`:

1. [`ev10_01_alembic_init.png`](ev10_01_alembic_init.png): Ejecución de `alembic init` y estructura de directorios generada.
2. [`ev10_02_alembic_revision.png`](ev10_02_alembic_revision.png): Generación de la migración con `--autogenerate`.
3. [`ev10_03_alembic_upgrade_history.png`](ev10_03_alembic_upgrade_history.png): Aplicación con `upgrade head` y consulta de `history`.
4. [`ev10_04_estructura_tablas.png`](ev10_04_estructura_tablas.png): Estructura relacional de las tablas SQLite (`users`, `devices`, `loans`).
5. [`ev10_05_swagger_general.png`](ev10_05_swagger_general.png): Swagger UI con los tres tags (`Users`, `Devices`, `Loans`) y todos los endpoints.
6. [`ev10_06_post_creaciones.png`](ev10_06_post_creaciones.png): Creación exitosa (201 Created) de Usuario, Dispositivo y Préstamo.
7. [`ev10_07_error_dispositivo_no_disponible.png`](ev10_07_error_dispositivo_no_disponible.png): Validación de regla de negocio (409 Conflict) al intentar prestar un equipo no disponible.
8. [`ev10_08_loans_details_joins.png`](ev10_08_loans_details_joins.png): Endpoint `GET /loans/details` mostrando la consulta relacional con Joins.
9. [`ev10_09_filtros_avanzados.png`](ev10_09_filtros_avanzados.png): Filtrado por query params (`status`, `device_type`, disponibilidad).
10. [`ev10_10_devolucion_dispositivo.png`](ev10_10_devolucion_dispositivo.png): Devolución exitosa con cambio de estado y liberación de disponibilidad del dispositivo.
