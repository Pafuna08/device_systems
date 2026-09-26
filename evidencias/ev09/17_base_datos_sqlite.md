# Evidencia de persistencia SQLite

La API crea `device_systems.db` al iniciar. La tabla `users` se genera desde `app/models/user_model.py` mediante `Base.metadata.create_all()`.

## Esquema generado

| Columna | Tipo | Restriccion |
|---|---|---|
| `id` | INTEGER | Primary key, index |
| `name` | VARCHAR(100) | NOT NULL, minimo 3 caracteres |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE, index |
| `role` | VARCHAR(20) | NOT NULL, admin/support/user |
| `is_active` | BOOLEAN | NOT NULL, default true |
| `created_at` | DATETIME | NOT NULL, fecha automatica |

## Verificacion

```text
Base de datos: sqlite:///./device_systems.db
Tabla: users
Filas iniciales: 3
Persistencia: confirmada con POST, GET, PUT, PATCH y DELETE
```

El archivo `.db` se excluye de Git porque es una base local de desarrollo. El modelo y este registro permiten reproducir su estructura.