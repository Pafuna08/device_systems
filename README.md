# device_systems

API REST para gestionar usuarios, dispositivos y préstamos con FastAPI, SQLAlchemy, Alembic y SQLite. Esta versión corresponde a la guía de actividades avanzadas para migraciones, asociaciones y consultas con joins.

## Tecnologías

- Python 3.14
- FastAPI
- SQLAlchemy 2
- Alembic
- Pydantic v2
- SQLite
- Uvicorn
- pytest

## Instalación y ejecución

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Documentación interactiva:

- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Estructura del proyecto

```text
device_systems/
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── README
├── app/
│   ├── database/
│   │   └── connection.py
│   ├── dependencies/
│   │   ├── database_dependency.py
│   │   └── user_dependencies.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user_model.py
│   │   ├── device_model.py
│   │   └── loan_model.py
│   ├── routes/
│   │   ├── user_routes.py
│   │   ├── device_routes.py
│   │   └── loan_routes.py
│   ├── schemas/
│   │   ├── user_schema.py
│   │   ├── device_schema.py
│   │   └── loan_schema.py
│   ├── services/
│   │   ├── user_service.py
│   │   ├── device_service.py
│   │   └── loan_service.py
│   ├── main.py
│   └── __init__.py
├── alembic.ini
├── requirements.txt
├── device_systems.db
├── tests/
│   └── test_device_systems_api.py
├── README.md
└── .gitignore
```

## Configuración de Alembic

Se inicializó Alembic desde la raíz y se configuró para apuntar a SQLite y a la metadata global de SQLAlchemy:

```bash
alembic init alembic
alembic revision --autogenerate -m "create devices and loans tables"
alembic upgrade head
alembic history
```

Evidencia verificada:

```text
<base> -> cff4dc36cc7a (head), create devices and loans tables
```

## Modelos y relaciones

### User

- id
- name
- email
- role
- is_active
- created_at
- loans: relación con Loan

### Device

- id
- name
- serial_number
- device_type
- brand
- is_available
- created_at
- loans: relación con Loan

### Loan

- id
- user_id
- device_id
- loan_date
- return_date
- status

Relaciones implementadas:

- User -> Loan: one-to-many
- Device -> Loan: one-to-many
- Loan -> User y Device: many-to-one

## Endpoints principales

### Users

- GET /users
- GET /users/{user_id}
- POST /users
- PUT /users/{user_id}
- PATCH /users/{user_id}
- DELETE /users/{user_id}

### Devices

- GET /devices
- GET /devices/{device_id}
- POST /devices
- PUT /devices/{device_id}
- PATCH /devices/{device_id}
- DELETE /devices/{device_id}

### Loans

- GET /loans
- GET /loans/{loan_id}
- POST /loans
- PATCH /loans/{loan_id}/return
- GET /users/{user_id}/loans
- GET /devices/{device_id}/loans

## Filtros y consultas avanzadas

Se incluyeron filtros como:

- GET /devices?device_type=laptop
- GET /devices?is_available=true
- GET /devices?brand=lenovo
- GET /devices?search=thinkpad
- GET /loans?status=active
- GET /loans?user_email=aprendiz@sena.edu.co
- GET /loans?device_type=laptop
- GET /users/{user_id}/loans
- GET /devices/{device_id}/loans

Las consultas usan joins entre User, Device y Loan, con where, and_, or_ e ilike para búsquedas flexibles.

## Reglas de negocio y manejo de errores

- 201 Created cuando crea usuario, dispositivo o préstamo
- 200 OK para consultas y devoluciones
- 204 No Content para eliminaciones
- 404 Not Found si no existe el recurso
- 400 Bad Request para serial duplicado o correo duplicado
- 409 Conflict para dispositivo no disponible o préstamo ya devuelto
- 422 Unprocessable Entity para datos inválidos

## Swagger / OpenAPI

La API está documentada con etiquetas por recurso:

- Users
- Devices
- Loans

La documentación disponible en:

- /docs
- /redoc

## Evidencia de pruebas realizadas

Se realizaron pruebas reales con pytest usando FastAPI TestClient.

Comando ejecutado:

```bash
.\venv\Scripts\python.exe -m pytest -q
```

Resultado verificado:

```text
3 passed in 1.40s
```

Se ejecutaron además las migraciones:

```bash
.\venv\Scripts\alembic.exe revision --autogenerate -m "create devices and loans tables"
.\venv\Scripts\alembic.exe upgrade head
.\venv\Scripts\alembic.exe history
```

Resultado verificado:

```text
<base> -> cff4dc36cc7a (head), create devices and loans tables
```

También se verificó la disponibilidad de Swagger y algunos endpoints:

```bash
.\venv\Scripts\python.exe -c "from fastapi.testclient import TestClient; from app.main import app; client = TestClient(app); print(client.get('/docs').status_code); print(client.get('/loans?status=active').status_code); print(client.get('/users/1/loans').status_code)"
```

Resultado verificado:

```text
200
200
200
```

## Reflexión

La aplicación evoluciona de un CRUD simple de usuarios a un sistema con relaciones reales entre modelos, integridad referencial, control de versiones con Alembic y consultas multidominio con joins. Esto es una base sólida para APIs REST profesionales y escalables.
