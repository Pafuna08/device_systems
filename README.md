# device_systems API

API REST para administrar usuarios con FastAPI, Pydantic v2 y una base de datos en memoria. Esta version implementa la guia GA1-220501096-01-AA1-EV08: CRUD completo, errores HTTP, Swagger/OpenAPI y Dependency Injection.

## Tecnologias

- Python 3.14
- FastAPI y Uvicorn
- Pydantic v2
- Git Flow y GitHub
- Postman y Thunder Client

## Instalacion y ejecucion

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Documentacion: `http://127.0.0.1:8000/docs` y `http://127.0.0.1:8000/redoc`.

## Estructura

```text
app/
├── main.py
├── data/users_db.py
├── dependencies/user_dependencies.py
├── routes/user_routes.py
├── schemas/user_schema.py
└── services/user_service.py
```

`routes` recibe peticiones, `schemas` valida datos, `services` concentra la logica, `data` simula persistencia y `dependencies` reutiliza validaciones con `Depends()`.

## Endpoints

| Metodo | Ruta | Exito | Funcion |
|---|---|---:|---|
| GET | `/users` | 200 | Lista y filtra por `role` o `is_active` |
| GET | `/users/{user_id}` | 200 | Consulta por ID |
| POST | `/users` | 201 | Crea un usuario |
| PUT | `/users/{user_id}` | 200 | Reemplaza todos los campos |
| PATCH | `/users/{user_id}` | 200 | Actualiza solo campos enviados |
| DELETE | `/users/{user_id}` | 204 | Elimina sin cuerpo de respuesta |

Roles validos: `admin`, `support`, `user`. El correo debe ser valido y unico.

## Ejemplos

Crear:

```json
{"name": "Carlos Mendoza", "email": "carlos.mendoza@device-systems.com", "role": "support", "is_active": true}
```

Actualizar parcialmente:

```json
{"role": "admin"}
```

```bash
curl -X PATCH http://127.0.0.1:8000/users/1 -H "Content-Type: application/json" -d "{\"role\":\"support\"}"
curl -X DELETE http://127.0.0.1:8000/users/1
```

## Errores y Dependency Injection

- `400`: correo duplicado o PATCH sin campos.
- `404`: usuario inexistente.
- `422`: datos invalidos de Pydantic.
- `500`: error inesperado con respuesta JSON estructurada.

`get_user_or_404` vive en `app/dependencies/user_dependencies.py` y se inyecta en GET, PUT, PATCH y DELETE:

```python
async def patch_existing_user(user_data: UserPatch, user: dict = Depends(get_user_or_404)):
    ...
```

Asi se centraliza la busqueda y el error 404 sin repetirlo en cada endpoint.

## Pruebas y evidencias

Importar `device_systems_postman.json` en Postman o `device_systems_thunder.json` en Thunder Client. Revisar Swagger en `/docs` y ReDoc en `/redoc`. La carpeta `evidencias/` conserva capturas del proyecto y las nuevas pruebas se validan con los endpoints CRUD.

## Git Flow aplicado

```text
main
└── feature/crud-users
    ├── feat: separar datos, servicios y dependencias
    ├── feat: implementar CRUD completo de usuarios
    └── docs: actualizar guia intermedia y pruebas
```

Flujo recomendado:

```bash
git switch main
git pull origin main
git switch -c feature/nombre-del-cambio
git add .
git commit -m "feat: describir el cambio"
git push -u origin feature/nombre-del-cambio
```

Luego se crea un Pull Request hacia `main` y se elimina la rama cuando se haga merge.

## Licencia

Proyecto academico para aprendizaje de FastAPI.