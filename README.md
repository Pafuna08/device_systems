# device_systems — FastAPI Avanzado (EV11 Seguridad)

API REST profesional para la gestión de usuarios, dispositivos tecnológicos y préstamos, desarrollada con **FastAPI**, **SQLAlchemy 2.0**, **Alembic**, **Pydantic v2**, **JWT/OAuth2**, **CORS**, **middleware**, **rate limiting** y **SQLite**.

> **Proyecto final:** `device_systems`  
> **Rama principal actualizada:** `main`  
> **Fase final abordada:** EV11 — Seguridad, autenticación y protección de la API

---

## Índice

1. [Tecnologías](#tecnologías)
2. [Objetivo del proyecto](#objetivo-del-proyecto)
3. [Instalación y ejecución](#instalación-y-ejecución)
4. [Estructura del proyecto](#estructura-del-proyecto)
5. [Funcionalidades implementadas](#funcionalidades-implementadas)
6. [Endpoints principales](#endpoints-principales)
7. [Seguridad aplicada](#seguridad-aplicada)
8. [Evidencias por guía](#evidencias-por-guía)
9. [Pruebas automatizadas](#pruebas-automatizadas)
10. [Conclusión](#conclusión)

---

## Tecnologías

- Python 3.12+
- FastAPI
- SQLAlchemy 2.0
- Alembic
- Pydantic v2
- SQLite
- OAuth2 + JWT (`python-jose`)
- `passlib[bcrypt]`
- `slowapi`
- Uvicorn
- Pytest

---

## Objetivo del proyecto

`device_systems` es una API REST completa que evoluciona desde un CRUD básico hasta una solución profesional con:

- gestión de usuarios
- gestión de dispositivos
- gestión de préstamos
- persistencia relacional
- migraciones con Alembic
- autenticación y autorización
- seguridad con JWT, middleware y CORS
- rate limiting
- pruebas automatizadas

La versión final quedo unificada en la rama `main` como la entrega final del proyecto.

---

## Instalación y ejecución

### 1. Clonar y entrar al proyecto

```bash
git clone https://github.com/Pafuna08/device_systems.git
cd device_systems
```

### 2. Crear entorno virtual

```bash
python -m venv venv
```

Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar migraciones

```bash
alembic upgrade head
```

### 5. Iniciar la API

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Documentación interactiva:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## Estructura del proyecto

```text
device_systems/
├── alembic/
│   ├── versions/
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── app/
│   ├── auth/
│   │   ├── auth_routes.py
│   │   ├── auth_service.py
│   │   └── security.py
│   ├── database/
│   │   └── connection.py
│   ├── dependencies/
│   │   ├── auth_dependency.py
│   │   └── database_dependency.py
│   ├── middlewares/
│   │   ├── rate_limiter.py
│   │   └── request_middleware.py
│   ├── models/
│   │   ├── user_model.py
│   │   ├── device_model.py
│   │   └── loan_model.py
│   ├── routes/
│   │   ├── user_routes.py
│   │   ├── device_routes.py
│   │   └── loan_routes.py
│   ├── schemas/
│   │   ├── auth_schema.py
│   │   ├── user_schema.py
│   │   ├── device_schema.py
│   │   └── loan_schema.py
│   ├── services/
│   │   ├── user_service.py
│   │   ├── device_service.py
│   │   └── loan_service.py
│   ├── main.py
│   └── seed.py
├── evidencias/
│   ├── guia8/
│   ├── ev09/
│   ├── ev10/
│   └── ev11/
├── tests/
│   └── test_device_systems_api.py
├── alembic.ini
├── requirements.txt
├── device_systems.db
├── README.md
├── .env.example
├── .gitignore
└── .env
```

---

## Funcionalidades implementadas

### CRUD de usuarios

- Crear usuarios
- listar usuarios
- buscar por ID
- filtrar por rol y estado
- actualizar parcial o completo
- eliminar usuarios

### CRUD de dispositivos

- crear equipos
- listar equipos
- filtrar por tipo, disponibilidad y marca
- actualizar y eliminar

### Gestión de préstamos

- registrar préstamos
- validar disponibilidad del equipo
- consultar historial por usuario o equipo
- filtrar por estado
- devolver equipo y liberar disponibilidad

### Seguridad y autenticación

- registro de usuario con validación fuerte de contraseña
- hash seguro con `passlib`
- login con OAuth2 + JWT
- rutas protegidas por token
- control por roles (`admin`, `support`, `user`)
- middleware para trazabilidad
- CORS configurado
- rate limiting por endpoint

---

## Endpoints principales

### Autenticación

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

### Usuarios

- `GET /users`
- `GET /users/{user_id}`
- `POST /users`
- `PUT /users/{user_id}`
- `PATCH /users/{user_id}`
- `DELETE /users/{user_id}`

### Dispositivos

- `GET /devices`
- `GET /devices/{device_id}`
- `POST /devices`
- `PUT /devices/{device_id}`
- `PATCH /devices/{device_id}`
- `DELETE /devices/{device_id}`

### Préstamos

- `GET /loans`
- `GET /loans/{loan_id}`
- `POST /loans`
- `PATCH /loans/{loan_id}/return`
- `GET /loans/details`

---

## Seguridad aplicada

Se implementó una capa de seguridad profesional:

- OAuth2 Password Flow
- JWT con firma HMAC (`HS256`)
- `hashed_password` nunca se devuelve al cliente
- rutas protegidas por `Depends()`
- control por roles
- encabezados personalizados (`X-App-Name`, `X-Process-Time`, `X-Request-ID`)
- configuración CORS explícita
- limitación de peticiones por IP con `slowapi`

### Usuarios por defecto

| Email                      | Password    | Rol     |
| -------------------------- | ----------- | ------- |
| admin@device-systems.com   | Admin1234   | admin   |
| support@device-systems.com | Support1234 | support |
| user@device-systems.com    | User12345   | user    |

---

## Evidencias por guía

Las evidencias reales del proyecto quedaron organizadas por fase dentro de la carpeta [evidencias](evidencias):

- [evidencias/guia8](evidencias/guia8)
- [evidencias/ev09](evidencias/ev09)
- [evidencias/ev10](evidencias/ev10)
- [evidencias/ev11](evidencias/ev11)

En la fase final, la evidencia verificada de seguridad está en [evidencias/ev11/EV11_RESULTADOS.md](evidencias/ev11/EV11_RESULTADOS.md) y en las capturas reales del sistema:

### 1. Estructura del proyecto

![Estructura del proyecto](evidencias/ev11/ev11_00_estructura_proyecto.png)

### 2. Migración Alembic aplicada

![Migración Alembic aplicada](evidencias/ev11/ev11_07_migracion_alembic_aplicada.png)

### 3. Registro de usuario

![Registro de usuario](evidencias/ev11/ev11_08_registro_usuario.png)

### 4. Login y token generado

![Login y token JWT](evidencias/ev11/ev11_09_login_token_JWT.png)

### 5. Consulta a /auth/me

![Perfil autenticado /auth/me](evidencias/ev11/ev11_03_auth_flow.png)

### 6. Acceso sin token

![Acceso sin token](evidencias/ev11/ev11_10_acceso_sin_token.png)

### 7. Acceso con rol no permitido

![Acceso con rol no permitido](evidencias/ev11/ev11_04_protected_routes.png)

### 8. Swagger/OpenAPI con OAuth2

![Swagger/OpenAPI con OAuth2](evidencias/ev11/ev11_02_swagger_oauth2.png)

### 9. Cabeceras del middleware

![Cabeceras del middleware](evidencias/ev11/ev11_05_cabecera_middleware.png)

### 10. Prueba de rate limiting

![Rate limiting activado](evidencias/ev11/ev11_06_rate_limit_429.png)

### 11. Página principal de la API

![Página raíz de la API](evidencias/ev11/ev11_01_root_home.png)

> Estas capturas fueron tomadas del proyecto en ejecución y corresponden a la evidencia real generada por la API.

---

## Explicación de CORS configurado

Se configuró `CORSMiddleware` en la aplicación para permitir explícitamente únicamente los orígenes locales autorizados:

- `http://localhost:5173`
- `http://localhost:3000`

La configuración incluye:

- `allow_credentials=True`
- `allow_methods=["*"]`
- `allow_headers=["*"]`

Esto permite que clientes frontend locales puedan consumir la API de forma segura sin abrir el acceso completo a cualquier dominio. No se recomienda usar `allow_origins=["*"]` en producción cuando hay credenciales, porque la especificación CORS no permite combinar origen comodín con autenticación de navegador. Si se hiciera eso, cualquier sitio externo podría intentar hacer peticiones autenticadas usando tokens o cookies del usuario, lo que supondría un riesgo serio de seguridad.

---

## Pruebas automatizadas

Se cuenta con una suite funcional real en:

- [tests/test_device_systems_api.py](tests/test_device_systems_api.py)

Ejecución verificada en esta sesión:

```bash
python -m pytest tests/ -q
```

Resultado real obtenido:

```text
18 passed in 5.42s
```

Esto confirma que la API cumple con la funcionalidad principal de la guía final y que el proyecto está estable para entrega.

---

## Reflexión final sobre la importancia de la seguridad en APIs REST

La seguridad en una API REST no es un detalle opcional: es una parte fundamental del diseño del sistema. Al exponer endpoints que gestionan usuarios, dispositivos, préstamos y datos sensibles, es imprescindible proteger la aplicación con autenticación, validación de entradas, control de roles, límites de peticiones y trazabilidad de accesos.

En este proyecto, el uso de JWT con OAuth2, contraseñas con hash, rutas protegidas, middleware personalizado y rate limiting reduce el riesgo de accesos no autorizados, abuso del servicio, inyección de lógica por parte de clientes no confiables y errores de seguridad que podrían comprometer la integridad del sistema. En un entorno real, una API insegura puede poner en riesgo tanto la información como la continuidad del negocio. Por eso la seguridad debe integrarse desde el inicio del desarrollo y no agregarse como un arreglo final.

---

## Cumplimiento de la guía final

La entrega final del proyecto cumple los requisitos esenciales de la guía EV11:

- registro seguro con validación de contraseña
- hash de contraseñas con `passlib[bcrypt]`
- autenticación con OAuth2 + JWT
- rutas protegidas con `401` y permisos por rol con `403`
- middleware personalizado con trazabilidad
- CORS configurado explícitamente para orígenes locales
- rate limiting con `429 Too Many Requests`
- migración Alembic para campos de autenticación
- documentación Swagger/OpenAPI actualizada
- archivo [.env.example](.env.example)
- repository ordenado y finalizado sobre la rama `main`

---

## Conclusión

Este repositorio refleja el desarrollo completo de `device_systems` desde las fases iniciales hasta la fase final de seguridad. La rama principal `main` queda actualizada con la versión final del proyecto y la evidencia se organiza por guía para que la entrega sea clara, profesional y verificable.

La entrega final no solo incluye la API funcional, sino también evidencias documentadas y pruebas reales que validan el funcionamiento del sistema en el propio proyecto.
