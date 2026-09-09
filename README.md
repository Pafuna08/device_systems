# device_systems API

API REST para administrar usuarios con FastAPI, Pydantic v2 y SQLAlchemy sobre SQLite. Esta version implementa la guia GA1-220501096-01-AA1-EV09: persistencia real, CRUD completo, constraints, errores HTTP, Swagger/OpenAPI y Dependency Injection.

## Tecnologias

- Python 3.14
- FastAPI y Uvicorn
- Pydantic v2 y email-validator
- SQLAlchemy 2 y SQLite
- Postman, Thunder Client, Git y GitHub

## Instalacion y ejecucion

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

La base local `device_systems.db` se crea automaticamente al iniciar la API. Documentacion: `http://127.0.0.1:8000/docs` y `http://127.0.0.1:8000/redoc`.

## Estructura del proyecto

```text
app/
├── main.py
├── database/connection.py
├── models/user_model.py
├── dependencies/database_dependency.py
├── dependencies/user_dependencies.py
├── routes/user_routes.py
├── schemas/user_schema.py
└── services/user_service.py
```

`database` configura engine, sesiones y Base declarativa. `models` representa tablas SQLAlchemy. `schemas` valida entrada y salida con Pydantic. `services` concentra consultas CRUD. `routes` expone HTTP. `dependencies` inyecta sesiones y usuarios.

## Persistencia, modelo y schemas

`app/database/connection.py` usa `sqlite:///./device_systems.db`, `create_engine`, `SessionLocal` y `Base`. `app/models/user_model.py` define la tabla `users` con `id`, `name`, `email`, `role`, `is_active` y `created_at`.

El modelo SQLAlchemy representa la tabla y sus restricciones en la base de datos. Los schemas Pydantic (`UserCreate`, `UserUpdate`, `UserPatch` y `UserResponse`) representan los datos que entran y salen por la API; no sustituyen al modelo ORM.

Constraints aplicados: `id` como primary key, `email` como `unique` y obligatorio, `is_active` por defecto `True`, `created_at` automático, nombre mínimo de tres caracteres y roles limitados a `admin`, `support` y `user`.

## Endpoints

| Metodo | Ruta | Exito | Funcion |
|---|---|---:|---|
| GET | `/users` | 200 | Lista, filtra y ordena usuarios desde SQLite |
| GET | `/users/{user_id}` | 200 | Consulta por ID |
| POST | `/users` | 201 | Crea un usuario en la base |
| PUT | `/users/{user_id}` | 200 | Reemplaza todos los campos |
| PATCH | `/users/{user_id}` | 200 | Actualiza solo campos enviados |
| DELETE | `/users/{user_id}` | 204 | Elimina de la base sin cuerpo |

Filtros: `/users?role=admin` y `/users?is_active=true`. Ordenamiento: `sort_by=name|created_at` y `sort_order=asc|desc`.

## Ejemplos de peticiones y respuestas

Crear usuario:

```json
{"name":"Carlos Mendoza","email":"carlos@device-systems.com","role":"support","is_active":true}
```

Respuesta `201 Created`:

```json
{"id":4,"name":"Carlos Mendoza","email":"carlos@device-systems.com","role":"support","is_active":true,"created_at":"2026-09-09T19:31:19"}
```

Actualizar parcialmente:

```bash
curl -X PATCH http://127.0.0.1:8000/users/1 -H "Content-Type: application/json" -d "{\"role\":\"support\"}"
```

Respuesta `200 OK`:

```json
{"id":1,"name":"Admin Usuario","email":"admin@device-systems.com","role":"support","is_active":true,"created_at":"2026-09-09T19:31:19"}
```

Eliminar:

```bash
curl -X DELETE http://127.0.0.1:8000/users/1
```

Respuesta: `204 No Content`, sin cuerpo.

## Códigos y manejo de errores

- `201 Created`: usuario creado.
- `200 OK`: consultas y actualizaciones correctas.
- `204 No Content`: eliminación correcta.
- `400 Bad Request`: correo duplicado o PATCH sin campos.
- `404 Not Found`: usuario inexistente.
- `422 Unprocessable Entity`: datos inválidos, email o rol no permitido.

Las rutas usan `HTTPException` para errores de negocio. La constraint `unique` de SQLite protege el correo y el servicio captura `IntegrityError` al crear. Pydantic valida formato de email, nombre, rol y tipos antes de consultar la base.

## Dependency Injection

`get_db()` crea una sesión SQLAlchemy por solicitud y la cierra en `finally`. `get_user_or_404()` recibe esa sesión con `Depends()` y reutiliza la consulta por ID en GET, PUT, PATCH y DELETE.

```python
def get_user_or_404(user_id: int = Path(..., gt=0), db: Session = Depends(get_db)) -> User:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
```

## Pruebas y evidencias

Las colecciones `device_systems_postman.json` y `device_systems_thunder.json` contienen las peticiones CRUD, filtros y errores. La carpeta `evidencias/` incluye Swagger, ReDoc, estructura y pruebas de endpoints:

- [`6_swagger_crud.png`](evidencias/6_swagger_crud.png)
- [`7_redoc_crud.png`](evidencias/7_redoc_crud.png)
- [`7.1_redoc_crud.png`](evidencias/7.1_redoc_crud.png)
- [`8_post_exitoso.png`](evidencias/8_post_exitoso.png)
- [`9_put_exitoso.png`](evidencias/9_put_exitoso.png)
- [`10_patch_exitoso.png`](evidencias/10_patch_exitoso.png)
- [`11_delete_exitoso.png`](evidencias/11_delete_exitoso.png)
- [`12_error_correo_duplicado.png`](evidencias/12_error_correo_duplicado.png)
- [`13_error_datos_invalidos.png`](evidencias/13_error_datos_invalidos.png)
- [`14_error_patch_vacio.png`](evidencias/14_error_patch_vacio.png)
- [`15_error_put_inexistente.png`](evidencias/15_error_put_inexistente.png)
- [`16_error_delete_inexistente.png`](evidencias/16_error_delete_inexistente.png)
- [`17_base_datos_sqlite.md`](evidencias/17_base_datos_sqlite.md): esquema y verificacion de SQLite.
- [`RESULTADOS_GUIA8.md`](evidencias/RESULTADOS_GUIA8.md)

El archivo SQLite se genera al ejecutar la API y está excluido de Git. Su estructura reproducible queda definida por el modelo SQLAlchemy y `Base.metadata.create_all()`.

## Reflexion final

La evolucion de `device_systems` paso de datos temporales en memoria a persistencia real con SQLite y SQLAlchemy. Separar el modelo ORM de los schemas Pydantic permite controlar la base de datos sin mezclarla con el contrato HTTP. Las constraints protegen la integridad, las sesiones permiten CRUD transaccional y Swagger, ReDoc y Git Flow hacen el proyecto verificable. El siguiente paso natural seria usar migraciones con Alembic y una base de datos de producción.

## Git Flow aplicado

La migración se desarrolla en ramas con commits trazables:

```text
main
└── feature/sqlalchemy-persistence
    ├── feat: configurar SQLite y modelo SQLAlchemy
    ├── feat: migrar CRUD de usuarios a SQLAlchemy
    └── docs: actualizar evidencias de persistencia
```

```bash
git switch main
git pull origin main
git switch -c feature/nombre-del-cambio
git add .
git commit -m "feat: describir el cambio"
git push -u origin feature/nombre-del-cambio
```

## Licencia

Proyecto academico para aprendizaje de FastAPI y SQLAlchemy.