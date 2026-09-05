# Resultados de pruebas funcionales

Pruebas ejecutadas contra `http://127.0.0.1:8000` el 5 de septiembre de 2026.

| Prueba | Resultado |
|---|---:|
| `PUT /users/1` | `200 OK` |
| `PATCH /users/1` | `200 OK` |
| `DELETE /users/3` | `204 No Content` |
| `GET /users/999` | `404 Not Found` |
| `PATCH /users/1` con `{}` | `400 Bad Request` |

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

Las capturas visuales `6_swagger_crud.png` y `7_redoc_crud.png` documentan la interfaz. Las capturas adicionales de respuestas pueden guardarse con los nombres `8_put_patch_resultado.png` y `10_delete_error_404.png`.