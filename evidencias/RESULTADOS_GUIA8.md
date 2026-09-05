# Resultados de pruebas funcionales

Pruebas ejecutadas contra `http://127.0.0.1:8000` el 5 de septiembre de 2026.

| Prueba | Resultado |
|---|---:|
| `GET /users` | `200 OK` |
| `GET /users/1` | `200 OK` |
| `GET /users?role=admin` | `200 OK` |
| `GET /users?is_active=true` | `200 OK` |
| `POST /users` | `201 Created` |
| `PUT /users/1` | `200 OK` |
| `PATCH /users/1` | `200 OK` |
| `DELETE /users/3` | `204 No Content` |
| `GET /users/999` | `404 Not Found` |
| `POST /users` con correo duplicado | `400 Bad Request` |
| `POST /users` con datos invalidos | `422 Unprocessable Entity` |
| `PUT /users/999` | `404 Not Found` |
| `PATCH /users/1` con `{}` | `400 Bad Request` |
| `DELETE /users/999` | `404 Not Found` |

## Respuestas capturadas

Despues de PUT y PATCH, `GET /users/1` retorno:

```json
{
  "name": "Admin Evidencia",
  "email": "admin.evidencia@device-systems.com",
  "role": "support",
  "is_active": true,
  "id": 1
}
```

Despues de eliminar el usuario 3, la consulta retorno:

```json
{"detail":"Usuario con ID 3 no encontrado"}
```

Capturas visuales incorporadas:

- `6_swagger_crud.png`: Swagger con los endpoints CRUD.
- `7_redoc_crud.png`: ReDoc con la documentacion OpenAPI.
- `8_put_patch_resultado.png`: respuesta exitosa despues de PUT y PATCH.
- `10_delete_error_404.png`: respuesta 404 despues de eliminar el usuario.