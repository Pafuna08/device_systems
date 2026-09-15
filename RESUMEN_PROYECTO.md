# Resumen del proyecto EV09

`device_systems` evoluciono de una API con datos en memoria a una API REST con CRUD persistente en SQLite mediante SQLAlchemy.

## Cambios de la guia EV09

- La persistencia simulada fue reemplazada por SQLite en `app/database/connection.py`.
- El modelo ORM esta en `app/models/user_model.py`.
- La logica de negocio esta en `app/services/user_service.py`.
- Las sesiones se inyectan desde `app/dependencies/database_dependency.py`.
- La dependencia `get_user_or_404` esta en `app/dependencies/user_dependencies.py`.
- Los schemas `UserCreate`, `UserUpdate` y `UserPatch` distinguen entrada, PUT y PATCH.
- Las rutas usan estados HTTP explicitos y documentacion OpenAPI.
- Se actualizo la documentacion, las colecciones y el flujo Git Flow.
- SQLAlchemy crea la tabla `users` con email unico, roles validos, nombre obligatorio, estado y fecha de creacion.
- `get_db()` inyecta sesiones y cada operacion hace commit o rollback en la base.
- Las evidencias `18` a `38` documentan estructura, SQLite, CRUD, errores, persistencia y Git Flow.

## Verificacion

Se comprobaron GET, POST, PUT, PATCH y DELETE con `TestClient` sobre SQLite, ademas de usuario inexistente, PATCH vacio, correo duplicado, filtros, ordenamiento y datos invalidos. El contrato OpenAPI confirma los seis endpoints de usuarios.

## Presentacion de cinco minutos

1. Mostrar la estructura por responsabilidades.
2. Explicar la diferencia entre PUT y PATCH.
3. Mostrar `Depends(get_user_or_404)` y el error 404 centralizado.
4. Probar Swagger y los casos de error.
5. Mostrar ramas y commits de Git Flow.
