# device_systems — FastAPI Avanzado (EV10)

API REST profesional para la gestión de usuarios, dispositivos tecnológicos y préstamos desarrollada con **FastAPI**, **SQLAlchemy 2.0**, **Alembic**, **Pydantic v2** y **SQLite**.

> **Actividad:** GA1-220501096-01-AA1-EV10: Migraciones con Alembic, Asociaciones de Modelos y Consultas con Joins en `device_systems`.  
> **Rama de trabajo unificada:** `device_systems_alembic_relaciones` ➔ `main`

---

## Tabla de Contenidos

1. [Tecnologías Utilizadas](#tecnologías-utilizadas)
2. [Instalación y Ejecución](#instalación-y-ejecución)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Modelos y Asociaciones](#modelos-y-asociaciones)
5. [Endpoints de la API](#endpoints-de-la-api)
6. [Reglas de Negocio y Manejo de Errores](#reglas-de-negocio-y-manejo-de-errores)
7. [Evidencias de Aprendizaje Requeridas por la Guía](#evidencias-de-aprendizaje-requeridas-por-la-guía)
   - [1. Inicialización de Alembic](#1-inicialización-de-alembic)
   - [2. Creación de Migración](#2-creación-de-migración)
   - [3. Aplicación de Migración e Historial](#3-aplicación-de-migración-e-historial)
   - [4. Estructura de Tablas Generadas en SQLite](#4-estructura-de-tablas-generadas-en-sqlite)
   - [5. Documentación Swagger UI](#5-documentación-swagger-ui)
   - [6. Creación de Usuario, Dispositivo y Préstamo](#6-creación-de-usuario-dispositivo-y-préstamo)
   - [7. Regla de Negocio: Dispositivo no Disponible (409 Conflict)](#7-regla-de-negocio-dispositivo-no-disponible-409-conflict)
   - [8. Consultas con Joins (`/loans/details`)](#8-consultas-con-joins-loansdetails)
   - [9. Filtros Avanzados](#9-filtros-avanzados)
   - [10. Devolución de Dispositivo y Liberación](#10-devolución-de-dispositivo-y-liberación)
8. [Pruebas Automatizadas con Pytest](#pruebas-automatizadas-con-pytest)
9. [Reflexión Técnica](#reflexión-técnica)
10. [Guion para la Socialización (5 Minutos)](#guion-para-la-socialización-5-minutos)

---

## Tecnologías Utilizadas

- **Python:** 3.14 / 3.12+
- **FastAPI:** Framework backend web de alto rendimiento.
- **SQLAlchemy 2.0:** ORM declarativo con tipado estático `Mapped` y `mapped_column`.
- **Alembic:** Sistema de control de versiones y migraciones de esquemas de base de datos.
- **Pydantic v2:** Validación estricta de datos, serialización y schemas de respuesta.
- **SQLite:** Base de datos relacional ligera con soporte ACID.
- **Uvicorn:** Servidor ASGI para ejecución asíncrona.
- **Pytest & TestClient:** Pruebas funcionales e integración automatizada.

---

## Instalación y Ejecución

### 1. Clonar el repositorio y entrar al directorio

```powershell
git clone https://github.com/Pafuna08/device_systems.git
cd device_systems
```

### 2. Crear y activar entorno virtual

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 4. Aplicar migraciones con Alembic

```powershell
alembic upgrade head
```

### 5. Iniciar la aplicación

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- **Swagger UI interactivo:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc alternativo:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Estructura del Proyecto

El proyecto sigue una arquitectura modular en capas (Presentación, Servicios, Persistencia, Dependencias):

```text
device_systems/
│── alembic/
│   │── versions/
│   │   └── cff4dc36cc7a_create_devices_and_loans_tables.py
│   │── env.py
│   │── README
│   └── script.py.mako
│── alembic.ini
│── app/
│   │── database/
│   │   └── connection.py
│   │── dependencies/
│   │   ├── database_dependency.py
│   │   └── user_dependencies.py
│   │── models/
│   │   ├── __init__.py
│   │   ├── user_model.py
│   │   ├── device_model.py
│   │   └── loan_model.py
│   │── routes/
│   │   ├── user_routes.py
│   │   ├── device_routes.py
│   │   └── loan_routes.py
│   │── schemas/
│   │   ├── user_schema.py
│   │   ├── device_schema.py
│   │   └── loan_schema.py
│   │── services/
│   │   ├── user_service.py
│   │   ├── device_service.py
│   │   └── loan_service.py
│   │── main.py
│   └── __init__.py
│── evidencias/
│   ├── ev10_01_alembic_init.png
│   ├── ev10_02_alembic_revision.png
│   ├── ev10_03_alembic_upgrade_history.png
│   ├── ev10_04_estructura_tablas.png
│   ├── ev10_05_swagger_general.png
│   ├── ev10_06_post_creaciones.png
│   ├── ev10_07_error_dispositivo_no_disponible.png
│   ├── ev10_08_loans_details_joins.png
│   ├── ev10_09_filtros_avanzados.png
│   ├── ev10_10_devolucion_dispositivo.png
│   └── EV10_RESULTADOS.md
│── tests/
│   └── test_device_systems_api.py
│── device_systems.db
│── requirements.txt
│── README.md
└── .gitignore
```

---

## Modelos y Asociaciones

Se implementó el modelado relacional entre 3 entidades mediante claves foráneas y relaciones bidireccionales con `relationship()` y `back_populates`:

```mermaid
erDiagram
    USERS ||--o{ LOANS : "tiene muchos (1:N)"
    DEVICES ||--o{ LOANS : "aparece en muchos (1:N)"
    USERS {
        int id PK
        string name
        string email UK
        string role
        boolean is_active
        datetime created_at
    }
    DEVICES {
        int id PK
        string name
        string serial_number UK
        string device_type
        string brand
        boolean is_available
        datetime created_at
    }
    LOANS {
        int id PK
        int user_id FK
        int device_id FK
        datetime loan_date
        datetime return_date
        string status
    }
```

- **`User` ➔ `Loan` (One-to-Many):** Un usuario puede tener múltiples préstamos registrados en su historial.
- **`Device` ➔ `Loan` (One-to-Many):** Un dispositivo conserva el historial de todos los préstamos pasados y activos.
- **`Loan` ➔ `User` y `Device` (Many-to-One):** Cada registro de préstamo apunta a exactamente un usuario prestatario y a un dispositivo físico.

---

## Endpoints de la API

### Recurso `/users`

- `GET /users`: Listar usuarios con filtros por `role`, `is_active` y ordenamiento.
- `GET /users/{user_id}`: Consultar usuario por ID.
- `POST /users`: Crear usuario (valida correo duplicado: `400 Bad Request`).
- `PUT /users/{user_id}`: Reemplazar completamente un usuario.
- `PATCH /users/{user_id}`: Actualizar parcialmente datos de usuario.
- `DELETE /users/{user_id}`: Eliminar usuario (`204 No Content`).

### Recurso `/devices`

- `GET /devices`: Listar dispositivos con filtros (`device_type`, `is_available`, `brand`, `search`).
- `GET /devices/{device_id}`: Consultar equipo por ID.
- `POST /devices`: Crear dispositivo (valida número de serie único: `400 Bad Request`).
- `PUT /devices/{device_id}`: Reemplazar dispositivo.
- `PATCH /devices/{device_id}`: Actualizar parcialmente atributos.
- `DELETE /devices/{device_id}`: Eliminar dispositivo (`204 No Content`).

### Recurso `/loans`

- `GET /loans`: Listar préstamos con información anidada y filtros.
- `GET /loans/details`: **Endpoint específico de Joins** con filtros combinados (`status`, `user_email`, `device_type`, `user_id`, `device_id`, `search`).
- `GET /loans/{loan_id}`: Consultar un préstamo puntual con detalles del usuario y dispositivo.
- `POST /loans`: Registrar un préstamo validando usuario, equipo y disponibilidad.
- `PATCH /loans/{loan_id}/return`: Devolver equipo, asignar fecha de retorno y cambiar `is_available` a `True`.
- `GET /users/{user_id}/loans`: Historial de préstamos de un usuario.
- `GET /devices/{device_id}/loans`: Historial de préstamos de un equipo.

---

## Reglas de Negocio y Manejo de Errores

|         Código HTTP          | Significado          | Escenario en la API                                                                                               |
| :--------------------------: | :------------------- | :---------------------------------------------------------------------------------------------------------------- |
|       **201 Created**        | Creado               | Creación exitosa de usuario, dispositivo o préstamo.                                                              |
|          **200 OK**          | Éxito                | Consultas exitosas, filtros aplicados y devolución de préstamo.                                                   |
|      **204 No Content**      | Sin contenido        | Eliminación física exitosa de usuarios o dispositivos.                                                            |
|     **400 Bad Request**      | Solicitud incorrecta | Correo electrónico duplicado en usuarios o número de serie duplicado en dispositivos.                             |
|      **404 Not Found**       | No encontrado        | Usuario, dispositivo o préstamo inexistente en la base de datos.                                                  |
|       **409 Conflict**       | Conflicto de negocio | Intento de prestar un equipo no disponible (`is_available == False`) o intentar devolver un préstamo ya devuelto. |
| **422 Unprocessable Entity** | Error de validación  | Carga útil con tipos inválidos, cadenas que no cumplen longitud mínima o valores fuera de enumeración literal.    |

---

## Evidencias de Aprendizaje Requeridas por la Guía

A continuación se presentan las evidencias visuales y técnicas de cada uno de los 10 aspectos solicitados:

### 1. Inicialización de Alembic

Instalación del paquete `alembic>=1.14.0`, ejecución de `alembic init alembic` y verificación de los archivos creados (`alembic.ini`, `env.py`, `script.py.mako`):

![Inicialización de Alembic](evidencias/ev10_01_alembic_init.png)

---

### 2. Creación de Migración

Generación automática de la revisión mediante `alembic revision --autogenerate -m "create devices and loans tables"` con detección de `Base.metadata`:

![Creación de Migración](evidencias/ev10_02_alembic_revision.png)

---

### 3. Aplicación de Migración e Historial

Aplicación de las modificaciones en la base de datos con `alembic upgrade head`, verificación del estado actual (`alembic current`) e historial (`alembic history`):

![Aplicación de Migración e Historial](evidencias/ev10_03_alembic_upgrade_history.png)

---

### 4. Estructura de Tablas Generadas en SQLite

Esquema relacional de las tablas `users`, `devices`, `loans` y `alembic_version` con claves primarias, índices, restricciones de unicidad y claves foráneas:

![Estructura de Tablas SQLite](evidencias/ev10_04_estructura_tablas.png)

---

### 5. Documentación Swagger UI

Interfaz OpenAPI interactiva disponible en `/docs`, categorizada por los tres tags: `Users`, `Devices` y `Loans` con todos sus métodos:

![Swagger UI General](evidencias/ev10_05_swagger_general.png)

---

### 6. Creación de Usuario, Dispositivo y Préstamo

Registro exitoso de un nuevo usuario, un nuevo equipo tecnológico y la vinculación de ambos mediante la creación de un préstamo con código `201 Created`:

![Creación de Recursos](evidencias/ev10_06_post_creaciones.png)

---

### 7. Regla de Negocio: Dispositivo no Disponible (409 Conflict)

Protección de concurrencia e integridad: cuando un segundo usuario intenta solicitar un equipo que ya se encuentra prestado (`is_available: false`), el sistema rechaza la operación con `409 Conflict`:

![Conflicto Dispositivo no Disponible](evidencias/ev10_07_error_dispositivo_no_disponible.png)

---

### 8. Consultas con Joins (`/loans/details`)

Consulta que combina información entre `loans`, `users` y `devices` usando `select(Loan).join(User).join(Device)` y serializada en `LoanDetailResponse`:

![Consultas con Joins](evidencias/ev10_08_loans_details_joins.png)

---

### 9. Filtros Avanzados

Ejecución de filtros combinados por parámetros en URL: estado del préstamo (`status=active`), tipo de equipo (`device_type=laptop`) y disponibilidad:

![Filtros Avanzados](evidencias/ev10_09_filtros_avanzados.png)

---

### 10. Devolución de Dispositivo y Liberación

Flujo de devolución mediante `PATCH /loans/{loan_id}/return`: el estado pasa a `returned`, se registra la fecha de devolución y el equipo vuelve a estar disponible (`is_available: true`) preservando el historial:

![Devolución de Dispositivo](evidencias/ev10_10_devolucion_dispositivo.png)

---

## Pruebas Automatizadas con Pytest

Se cuenta con una suite de pruebas en [`tests/test_device_systems_api.py`](tests/test_device_systems_api.py) que valida automáticamente los 12 escenarios de la **Fase 13**:

```powershell
.\venv\Scripts\python.exe -m pytest -v
```

Resultado de la ejecución:

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

## Reflexión Técnica

### 1. Importancia del control de versiones en bases de datos con Alembic

En el desarrollo de software moderno, el código de la aplicación y la estructura de la base de datos deben evolucionar de manera coordinada. Las migraciones con Alembic proporcionan:

- **Trazabilidad y reproducibilidad:** Cada cambio en el esquema (creación de tablas, adición de columnas o índices) se documenta como una revisión identificable e inmutable.
- **Entornos consistentes:** Garantiza que el entorno local de desarrollo, el servidor de pruebas y producción compartan exactamente la misma definición de datos sin depender de scripts manuales propensos a error humano.
- **Rollback seguro:** Capacidad de revertir cambios (`downgrade`) en caso de anomalías sin pérdida de control del sistema.

### 2. Integridad referencial y asociaciones entre modelos

El uso de claves foráneas (`ForeignKey`) y asociaciones ORM (`relationship`, `back_populates`) aporta dos ventajas decisivas:

- **Integridad a nivel de motor:** Previene la existencia de registros huérfanos (un préstamo nunca puede apuntar a un usuario o dispositivo inexistente).
- **Productividad y expresividad:** A nivel de aplicación, permite navegar directamente entre objetos (`loan.user.name`, `device.loans`) simplificando la lógica de negocio y las validaciones.

### 3. Consultas avanzadas con Joins y optimización

En lugar de incurrir en el problema del $N+1$ (realizar múltiples consultas separadas a la base de datos por cada registro), el uso de `join()` explícito permite que el motor relacional resuelva en una única operación la combinación de datos entre prestatario, equipo y préstamo. Combinado con operadores flexibles como `ilike()`, `and_()` y `or_()`, la API ofrece capacidades de búsqueda robustas y eficientes para el cliente.

---

## Guion para la Socialización (5 Minutos)

Estructura sugerida para la exposición oral del aprendiz frente al instructor:

1. **¿Qué cambios se realizaron respecto a la versión anterior? (45 s):**  
   _"Evolucionamos la API de un CRUD básico con persistencia exclusiva de usuarios a una plataforma relacional de préstamos tecnológicos. Incorporamos dos nuevos recursos (`/devices` y `/loans`), versionamiento de esquema con Alembic y consultas combinadas con joins."_

2. **¿Cómo se configuró Alembic? (45 s):**  
   _"Se inicializó con `alembic init alembic`. En `alembic.ini` se definió la URL de conexión a SQLite. En `alembic/env.py` se enlazó la metadata del ORM (`target_metadata = Base.metadata`) e importamos los modelos (`User`, `Device`, `Loan`) para que el detector reconozca todas las entidades."_

3. **¿Qué migraciones se generaron? (30 s):**  
   _"Ejecutamos `alembic revision --autogenerate -m 'create devices and loans tables'`, la cual generó el archivo de migración con las tablas `devices` y `loans`, sus índices y llaves foráneas. Posteriormente se aplicó con `alembic upgrade head`."_

4. **¿Cómo se relacionaron User, Device y Loan? (45 s):**  
   _"Diseñamos relaciones uno a muchos entre Usuario y Préstamos, y entre Dispositivo y Préstamos. En la tabla `loans` establecimos dos claves foráneas (`user_id` y `device_id`). En el ORM usamos `relationship()` con `back_populates` en ambos extremos para permitir acceso bidireccional y cascadas ordenadas."_

5. **¿Cómo funcionan las consultas con joins? (45 s):**  
   _"En `loan_service.py` construimos la consulta con `select(Loan).join(User).join(Device)`. Esto combina las tres tablas en una sola instrucción SQL, permitiendo que la API responda en el endpoint `/loans/details` con un esquema Pydantic que anida la información del usuario y del dispositivo."_

6. **¿Cómo se aplicaron los filtros avanzados? (30 s):**  
   _"A través de parámetros de consulta opcionales (`Query`), construyendo filtros dinámicos con `where()`, `and_()`, `or*()`y operadores como`ilike()` para búsquedas insensibles a mayúsculas y minúsculas por estado, correo o tipo de dispositivo."*

7. **¿Qué aprendió sobre modelado relacional en APIs REST? (30 s):**  
   _"Aprendí que la coherencia de datos debe asegurarse tanto en el motor de base de datos con claves foráneas como en la capa de servicios mediante validaciones de negocio (como verificar disponibilidad antes de prestar), y que las migraciones son imprescindibles para la entrega continua y el desarrollo en equipo."_

---

## Catálogo Histórico Integral de Evidencias (Desde la 1 hasta la Actual)

Este repositorio representa la evolución incremental de una API profesional en tres fases consecutivas de formación SENA. Todas las evidencias generadas a lo largo del proceso se conservan en la carpeta [`evidencias/`](evidencias/):

<details>
<summary><strong>📁 Fase 1 (EV08): API REST Básica y CRUD de Usuarios en Memoria (Evidencias 1 a 16)</strong></summary>

En esta primera etapa se construyeron los cimientos de la API: entorno virtual, configuración de FastAPI, schemas Pydantic, endpoints CRUD en memoria y documentación OpenAPI.

| Evidencia                           | Descripción                                                            |                                     Enlace                                      |
| :---------------------------------- | :--------------------------------------------------------------------- | :-----------------------------------------------------------------------------: |
| **1.png**                           | Creación y activación de entorno virtual en PowerShell.                |                             [Ver](evidencias/1.png)                             |
| **2.png**                           | Instalación de dependencias iniciales (`FastAPI`, `Uvicorn`).          |                             [Ver](evidencias/2.png)                             |
| **3.png**                           | Configuración del archivo `main.py` y servidor Uvicorn.                |                             [Ver](evidencias/3.png)                             |
| **4.0.png / 4.1.png**               | Verificación de respuesta en endpoint raíz `/` y `/health`.            |          [Ver 4.0](evidencias/4.0.png) / [Ver 4.1](evidencias/4.1.png)          |
| **5.0.png / 5.1.png**               | Estructura modular inicial y dependencias de proyecto.                 |          [Ver 5.0](evidencias/5.0.png) / [Ver 5.1](evidencias/5.1.png)          |
| **6_swagger_crud.png**              | Documentación Swagger UI con los endpoints CRUD de usuarios.           |                      [Ver](evidencias/6_swagger_crud.png)                       |
| **7_redoc_crud.png / 7.1**          | Documentación alternativa en ReDoc.                                    | [Ver 7](evidencias/7_redoc_crud.png) / [Ver 7.1](evidencias/7.1_redoc_crud.png) |
| **8_post_exitoso.png**              | Creación exitosa de usuario (`POST /users` - 201 Created).             |                      [Ver](evidencias/8_post_exitoso.png)                       |
| **9_put_exitoso.png**               | Reemplazo completo de usuario (`PUT /users/{id}` - 200 OK).            |                       [Ver](evidencias/9_put_exitoso.png)                       |
| **10_patch_exitoso.png**            | Actualización parcial (`PATCH /users/{id}` - 200 OK).                  |                     [Ver](evidencias/10_patch_exitoso.png)                      |
| **11_delete_exitoso.png**           | Eliminación física (`DELETE /users/{id}` - 204 No Content).            |                     [Ver](evidencias/11_delete_exitoso.png)                     |
| **12_error_correo_duplicado.png**   | Validación de unicidad de correo (`400 Bad Request`).                  |                 [Ver](evidencias/12_error_correo_duplicado.png)                 |
| **13_error_datos_invalidos.png**    | Error de validación por esquema Pydantic (`422 Unprocessable Entity`). |                 [Ver](evidencias/13_error_datos_invalidos.png)                  |
| **14_error_patch_vacio.png**        | Validación de cuerpo vacío en PATCH (`400 Bad Request`).               |                   [Ver](evidencias/14_error_patch_vacio.png)                    |
| **15_error_put_inexistente.png**    | Actualización de usuario no encontrado (`404 Not Found`).              |                 [Ver](evidencias/15_error_put_inexistente.png)                  |
| **16_error_delete_inexistente.png** | Eliminación de usuario no encontrado (`404 Not Found`).                |                [Ver](evidencias/16_error_delete_inexistente.png)                |

</details>

<details>
<summary><strong>📁 Fase 2 (EV09): Persistencia en Base de Datos con SQLAlchemy y SQLite (Evidencias 17 a 38)</strong></summary>

En esta segunda etapa se reemplazó el almacenamiento en memoria por persistencia real en base de datos relacional SQLite utilizando SQLAlchemy 2.0 y separación en capas de servicio y dependencias.

| Evidencia                                      | Descripción                                                                            |                            Enlace                            |
| :--------------------------------------------- | :------------------------------------------------------------------------------------- | :----------------------------------------------------------: |
| **17_base_datos_sqlite.md**                    | Documentación de la conexión SQLite y esquema de tabla `users`.                        |          [Ver](evidencias/17_base_datos_sqlite.md)           |
| **18_estructura_proyecto_ev09.png**            | Estructura de directorios modular con carpetas `database/`, `models/`, `services/`.    |      [Ver](evidencias/18_estructura_proyecto_ev09.png)       |
| **19_base_datos_sqlite_ev09.png**              | Inspección física del archivo `device_systems.db` y tabla `users`.                     |       [Ver](evidencias/19_base_datos_sqlite_ev09.png)        |
| **20_swagger_sqlalchemy.png**                  | Swagger UI conectado a base de datos relacional.                                       |         [Ver](evidencias/20_swagger_sqlalchemy.png)          |
| **21_redoc_ev09.png**                          | Documentación ReDoc de la versión con persistencia.                                    |             [Ver](evidencias/21_redoc_ev09.png)              |
| **22_post_usuario_sqlalchemy.png**             | Inserción en base de datos SQLite con ID autoincremental (201 Created).                |       [Ver](evidencias/22_post_usuario_sqlalchemy.png)       |
| **23_get_lista_sqlalchemy.png**                | Consulta `SELECT` de todos los usuarios en base de datos.                              |        [Ver](evidencias/23_get_lista_sqlalchemy.png)         |
| **24_get_usuario_id_sqlalchemy.png**           | Consulta por ID primario con SQLAlchemy.                                               |      [Ver](evidencias/24_get_usuario_id_sqlalchemy.png)      |
| **25_filtro_rol_sqlalchemy.png**               | Filtrado en base de datos por columna `role` (`admin`, `support`, `user`).             |        [Ver](evidencias/25_filtro_rol_sqlalchemy.png)        |
| **26_filtro_estado_sqlalchemy.png**            | Filtrado en base de datos por columna booleana `is_active`.                            |      [Ver](evidencias/26_filtro_estado_sqlalchemy.png)       |
| **27_ordenamiento_sqlalchemy.png**             | Ordenamiento SQL por `created_at` o `name` (`asc`/`desc`).                             |       [Ver](evidencias/27_ordenamiento_sqlalchemy.png)       |
| **28_put_sqlalchemy.png**                      | Actualización persistida mediante sesión de SQLAlchemy.                                |           [Ver](evidencias/28_put_sqlalchemy.png)            |
| **29_patch_sqlalchemy.png**                    | Modificación parcial reflejada en disco.                                               |          [Ver](evidencias/29_patch_sqlalchemy.png)           |
| **30_delete_sqlalchemy.png**                   | Borrado físico `DELETE FROM users WHERE id = :id`.                                     |          [Ver](evidencias/30_delete_sqlalchemy.png)          |
| **31_usuario_eliminado_404.png**               | Verificación de eliminación comprobando que retorna `404 Not Found`.                   |        [Ver](evidencias/31_usuario_eliminado_404.png)        |
| **32_error_email_duplicado_sqlalchemy.png**    | Captura de `IntegrityError` de SQLite ante correo duplicado (`400 Bad Request`).       |  [Ver](evidencias/32_error_email_duplicado_sqlalchemy.png)   |
| **33_error_validacion_sqlalchemy.png**         | Validación de correo y campos con Pydantic v2.                                         |     [Ver](evidencias/33_error_validacion_sqlalchemy.png)     |
| **34_error_patch_vacio_sqlalchemy.png**        | Control de excepciones para payloads vacíos.                                           |    [Ver](evidencias/34_error_patch_vacio_sqlalchemy.png)     |
| **35_error_put_inexistente_sqlalchemy.png**    | Manejo de excepción cuando el registro no existe en SQLite.                            |  [Ver](evidencias/35_error_put_inexistente_sqlalchemy.png)   |
| **36_error_delete_inexistente_sqlalchemy.png** | Manejo de eliminación fallida sobre registro inexistente.                              | [Ver](evidencias/36_error_delete_inexistente_sqlalchemy.png) |
| **37_persistencia_entre_sesiones.png**         | Prueba de persistencia cerrando y reabriendo el servidor Uvicorn sin pérdida de datos. |     [Ver](evidencias/37_persistencia_entre_sesiones.png)     |
| **38_gitflow_ev09.png**                        | Evidencia del flujo de ramas en Git para la entrega EV09.                              |            [Ver](evidencias/38_gitflow_ev09.png)             |

</details>

<details open>
<summary><strong>📁 Fase 3 (EV10 - Actual): Migraciones con Alembic, Asociaciones y Consultas con Joins (Evidencias EV10_01 a EV10_10)</strong></summary>

Fase culminante donde se incorporan migraciones de esquema versionadas con Alembic, modelos de dispositivos y préstamos, integridad referencial y consultas relacionales complejas con joins y filtros.

| Evidencia                                       | Requisito de la Guía                                                                 |                            Captura                            |
| :---------------------------------------------- | :----------------------------------------------------------------------------------- | :-----------------------------------------------------------: |
| **ev10_01_alembic_init.png**                    | Ejecución de `alembic init` y estructura creada.                                     |          [Ver](evidencias/ev10_01_alembic_init.png)           |
| **ev10_02_alembic_revision.png**                | Creación de migración con `alembic revision --autogenerate`.                         |        [Ver](evidencias/ev10_02_alembic_revision.png)         |
| **ev10_03_alembic_upgrade_history.png**         | Aplicación con `alembic upgrade head` e historial `alembic history`.                 |     [Ver](evidencias/ev10_03_alembic_upgrade_history.png)     |
| **ev10_04_estructura_tablas.png**               | Estructura SQL de tablas en SQLite (`users`, `devices`, `loans`).                    |        [Ver](evidencias/ev10_04_estructura_tablas.png)        |
| **ev10_05_swagger_general.png**                 | Swagger UI con tags `Users`, `Devices` y `Loans`, incluyendo `/loans/details`.       |         [Ver](evidencias/ev10_05_swagger_general.png)         |
| **ev10_06_post_creaciones.png**                 | Creación exitosa (201 Created) de usuario, dispositivo y préstamo.                   |         [Ver](evidencias/ev10_06_post_creaciones.png)         |
| **ev10_07_error_dispositivo_no_disponible.png** | Validación de regla de negocio de disponibilidad (409 Conflict).                     | [Ver](evidencias/ev10_07_error_dispositivo_no_disponible.png) |
| **ev10_08_loans_details_joins.png**             | Consultas con Joins entre préstamos, usuarios y dispositivos (`GET /loans/details`). |       [Ver](evidencias/ev10_08_loans_details_joins.png)       |
| **ev10_09_filtros_avanzados.png**               | Filtrado por estado, tipo de equipo y disponibilidad.                                |        [Ver](evidencias/ev10_09_filtros_avanzados.png)        |
| **ev10_10_devolucion_dispositivo.png**          | Devolución de equipo (`PATCH return`) y confirmación de `is_available: true`.        |     [Ver](evidencias/ev10_10_devolucion_dispositivo.png)      |

</details>

---

## 🔐 EV11 — Seguridad: Autenticación, Middleware, CORS, Rate Limiting y Validación Avanzada

**Actividad:** GA1-220501096-01-AA1-EV11 · **Rama:** `device_systems_security`

Esta fase evoluciona `device_systems` (construido en EV09/EV10) agregando una capa completa
de seguridad sin romper la funcionalidad previa de usuarios, dispositivos y préstamos.

### Qué se agregó

| Área                         | Detalle                                                                                                                                                                                                       |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Autenticación**            | OAuth2 Password Flow + JWT (`python-jose`). Endpoints `POST /auth/register`, `POST /auth/login`, `GET /auth/me`.                                                                                              |
| **Hash de contraseñas**      | `passlib[bcrypt]`. Ninguna contraseña se guarda ni se retorna en texto plano (`hashed_password` nunca aparece en las respuestas).                                                                             |
| **Validaciones**             | Pydantic v2 (`field_validator`, `Field`, `ConfigDict(from_attributes=True)`). Contraseña: mínimo 8 caracteres, mayúscula, minúscula, número, sin espacios.                                                    |
| **Autorización por rol**     | Dependencias `get_current_active_user`, `require_admin`, `require_admin_or_support` en `app/dependencies/auth_dependency.py`.                                                                                 |
| **Middleware personalizado** | `app/middlewares/request_middleware.py`: agrega `X-App-Name`, `X-Process-Time`, `X-Request-ID` y registra cada petición en el log.                                                                            |
| **CORS**                     | `CORSMiddleware` configurado para `http://localhost:5173` y `http://localhost:3000` con credenciales.                                                                                                         |
| **Rate limiting**            | `slowapi`: `/auth/login` 5/min, `/auth/register` 3/min, `GET /users` 30/min, `POST /loans` 10/min. Responde `429 Too Many Requests` al exceder el límite.                                                     |
| **Migración**                | `alembic/versions/..._add_authentication_fields_to_users.py`: agrega `hashed_password` sin romper filas existentes (server_default temporal, retirado tras el backfill) y corrige el índice único de `email`. |

### Matriz de protección de rutas implementada

| Ruta                                                        | Protección                                                                                                                                                              |
| ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /users`, `GET /users/{id}`                             | Usuario autenticado                                                                                                                                                     |
| `POST/PUT/PATCH/DELETE /users/*`                            | Rol **admin** (decisión de diseño: el alta pública solo ocurre vía `/auth/register` y siempre crea rol `user`; gestionar cuentas administrativas se restringe a admins) |
| `POST /devices`, `PUT /devices/{id}`, `PATCH /devices/{id}` | Rol **admin o support**                                                                                                                                                 |
| `DELETE /devices/{id}`                                      | Rol **admin**                                                                                                                                                           |
| `POST /loans`                                               | Usuario autenticado                                                                                                                                                     |
| `PATCH /loans/{id}/return`                                  | Rol **admin o support**                                                                                                                                                 |
| `GET /loans/details`                                        | Rol **admin o support**                                                                                                                                                 |

Sin token válido → `401 Unauthorized`. Con token válido pero rol insuficiente → `403 Forbidden`.

### ¿Por qué no usar `allow_origins=["*"]` en producción?

La especificación CORS prohíbe combinar un origen comodín (`*`) con `allow_credentials=True`: si se
permitiera, cualquier sitio web (incluido uno malicioso) podría hacer peticiones autenticadas a la API
usando las cookies o el header `Authorization` de la víctima con solo lograr que abriera una página en
su navegador, ya que el navegador adjuntaría las credenciales automáticamente. Por eso en producción se
debe declarar explícitamente la lista de dominios del frontend autorizado (por ejemplo
`https://app.miempresa.com`), nunca `"*"`, cuando `allow_credentials=True`.

### Variables de entorno nuevas (`.env`)

```
SECRET_KEY=<valor aleatorio largo, ej. python -c "import secrets; print(secrets.token_hex(32))">
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Usuarios semilla (creados automáticamente al iniciar la API)

| Email                      | Password    | Rol     | Activo |
| -------------------------- | ----------- | ------- | ------ |
| admin@device-systems.com   | Admin1234   | admin   | sí     |
| support@device-systems.com | Support1234 | support | sí     |
| user@device-systems.com    | User12345   | user    | no     |

### Cómo probar

```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Swagger UI en `http://127.0.0.1:8000/docs`: usa el botón **Authorize**, inicia sesión con
`POST /auth/login` (username = email) y prueba las rutas protegidas directamente desde ahí.

La suite `tests/test_device_systems_api.py` cubre los 15 escenarios funcionales mínimos de la
Fase 13 de la guía (registro, login, `/auth/me`, accesos sin token / con token inválido / sin
permisos, roles, CORS, cabeceras de middleware y activación del rate limiting):

```bash
pytest tests/ -v
```

### Evidencias reales EV11 (capturas del proyecto)

| Evidencia              | Descripción                                                                                 | Archivo                                                                            |
| ---------------------- | ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Inicio del API         | Página raíz con bienvenida, enlaces a Swagger y ReDoc, y resumen de seguridad.              | [evidencias/ev11_01_root_home.png](evidencias/ev11_01_root_home.png)               |
| Swagger OAuth2         | Swagger UI con el esquema OAuth2PasswordBearer visible y documentación de la API.           | [evidencias/ev11_02_swagger_oauth2.png](evidencias/ev11_02_swagger_oauth2.png)     |
| Flujo de autenticación | Registro, login y consulta a `/auth/me` con token generado.                                 | [evidencias/ev11_03_auth_flow.png](evidencias/ev11_03_auth_flow.png)               |
| Protección de rutas    | Acceso sin token (`401`), token inválido (`401`) y rol insuficiente (`403`).                | [evidencias/ev11_04_protected_routes.png](evidencias/ev11_04_protected_routes.png) |
| CORS y middleware      | Cabeceras `X-App-Name`, `X-Process-Time`, `X-Request-ID` y CORS de `http://localhost:5173`. | [evidencias/ev11_05_cors_middleware.png](evidencias/ev11_05_cors_middleware.png)   |
| Rate limiting          | Validación real de bloqueo por exceso de peticiones con `429 Too Many Requests`.            | [evidencias/ev11_06_rate_limit_429.png](evidencias/ev11_06_rate_limit_429.png)     |

> Todas estas capturas se generaron directamente contra la API en ejecución y corresponden a respuestas reales del proyecto `device_systems`.
