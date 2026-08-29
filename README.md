# 🚀 device_systems API - Gestión de Usuarios

**Aplicación backend desarrollada con FastAPI para la gestión de usuarios del sistema device_systems**

## 📋 Descripción

Esta es una API REST completa que implementa todas las mejores prácticas de FastAPI para la gestión de usuarios. Incluye validación de datos con Pydantic v2, endpoints GET/POST, filtros avanzados y documentación interactiva.

## ✨ Características Implementadas

✅ **Configuración del proyecto**: Estructura completa y profesional  
✅ **Modelo de usuario Pydantic v2**: Con todas las validaciones requeridas  
✅ **Endpoints GET**:
   - `GET /users` - Obtener todos los usuarios
   - `GET /users/{user_id}` - Obtener usuario por ID
   - `GET /users?role=admin` - Filtrar por rol
   - `GET /users?is_active=true` - Filtrar por estado

✅ **Endpoint POST**:
   - `POST /users` - Crear nuevo usuario con validaciones

✅ **Response Models**: Modelos específicos para cada respuesta  
✅ **Cabeceras HTTP personalizadas**: X-App-Name y X-API-Version  
✅ **Documentación automática**: Swagger UI y ReDoc  
✅ **Validaciones completas**: Email único, formatos válidos, roles permitidos

## 🛠️ Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git

### Paso 1: Clonar el Repositorio
```bash
git clone <URL-del-repositorio>
cd device_systems
```

### Paso 2: Crear Entorno Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias
```bash
pip install -r requirements.txt
```

## 🚀 Ejecución del Servidor

```bash
# Opción 1: Desde la raíz del proyecto
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Opción 2: Directamente
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

La API estará disponible en: **http://127.0.0.1:8000**

## 📚 Documentación Interactiva

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **Página Principal**: http://127.0.0.1:8000

## 📡 Endpoints Disponibles

### 1. Obtener Todos los Usuarios
```http
GET /users
```

**Parámetros Query** (opcionales):
- `role`: Filtrar por rol (admin, support, user)
- `is_active`: Filtrar por estado (true, false)

**Ejemplo:**
```bash
curl http://127.0.0.1:8000/users
curl http://127.0.0.1:8000/users?role=admin
curl http://127.0.0.1:8000/users?is_active=true
```

**Respuesta (200 OK):**
```json
{
  "users": [
    {
      "id": 1,
      "name": "Admin Usuario",
      "email": "admin@device-systems.com",
      "role": "admin",
      "is_active": true
    }
  ],
  "total": 1
}
```

---

### 2. Obtener Usuario por ID
```http
GET /users/{user_id}
```

**Path Parameters:**
- `user_id`: ID único del usuario (obligatorio)

**Ejemplo:**
```bash
curl http://127.0.0.1:8000/users/1
```

**Respuesta (200 OK):**
```json
{
  "id": 1,
  "name": "Admin Usuario",
  "email": "admin@device-systems.com",
  "role": "admin",
  "is_active": true
}
```

**Respuesta (404 Not Found):**
```json
{
  "detail": "Usuario con ID 999 no encontrado"
}
```

---

### 3. Crear Nuevo Usuario
```http
POST /users
Content-Type: application/json
```

**Body** (JSON):
```json
{
  "name": "Nuevo Usuario",
  "email": "nuevo@device-systems.com",
  "role": "user",
  "is_active": true
}
```

**Validaciones:**
- ✓ `name`: Mínimo 3 caracteres, máximo 100
- ✓ `email`: Formato válido y único (sin duplicados)
- ✓ `role`: Valores permitidos: admin, support, user
- ✓ `is_active`: Booleano (true/false)

**Ejemplo:**
```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan Pérez",
    "email": "juan.perez@device-systems.com",
    "role": "support",
    "is_active": true
  }'
```

**Respuesta (201 Created):**
```json
{
  "id": 4,
  "name": "Juan Pérez",
  "email": "juan.perez@device-systems.com",
  "role": "support",
  "is_active": true
}
```

**Respuesta (400 Bad Request) - Email duplicado:**
```json
{
  "detail": "El correo 'juan@device-systems.com' ya está registrado en el sistema"
}
```

---

## 📊 Ejemplos de Uso

### Ejemplo 1: Obtener todos los usuarios activos
```bash
curl http://127.0.0.1:8000/users?is_active=true
```

### Ejemplo 2: Obtener todos los administradores
```bash
curl http://127.0.0.1:8000/users?role=admin
```

### Ejemplo 3: Obtener usuario específico
```bash
curl http://127.0.0.1:8000/users/2
```

### Ejemplo 4: Crear usuario con validación de email
```bash
# ✓ Éxito
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@device-systems.com","role":"user","is_active":true}'

# ✗ Error - Email inválido
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"invalid-email","role":"user"}'

# ✗ Error - Nombre muy corto
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"AB","email":"test@device-systems.com","role":"user"}'
```

## 🧪 Pruebas con Herramientas

### Usando Swagger UI
1. Abre http://127.0.0.1:8000/docs en tu navegador
2. Haz clic en el endpoint que deseas probar
3. Completa los parámetros y haz clic en "Execute"

### Usando Postman
1. Descarga Postman desde https://www.postman.com
2. Importa la colección `device_systems_postman.json`
3. Ejecuta las pruebas desde la interfaz

### Usando Thunder Client
1. Instala la extensión Thunder Client en VS Code
2. Abre el archivo `device_systems_thunder.json`
3. Realiza las pruebas directamente

## 📁 Estructura del Proyecto

```
device_systems/
│
├── app/
│   ├── __init__.py              # Paquete principal
│   ├── main.py                  # Aplicación FastAPI
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user_schema.py       # Modelos Pydantic v2
│   └── routes/
│       ├── __init__.py
│       └── user_routes.py       # Endpoints GET y POST
│
├── device_systems_postman.json  # Colección Postman
├── device_systems_thunder.json  # Colección Thunder Client
├── requirements.txt              # Dependencias Python
├── .gitignore                   # Archivos ignorados por Git
├── README.md                    # Este archivo
└── .env.example                 # Ejemplo de variables de entorno
```

## 🔒 Validaciones Implementadas

### Modelo de Usuario

| Campo | Tipo | Validación | Ejemplo |
|-------|------|-----------|---------|
| `id` | int | Auto-generado | 1 |
| `name` | str | Mín 3 chars, máx 100 | "Juan Pérez" |
| `email` | EmailStr | Formato válido, único | "juan@device-systems.com" |
| `role` | str | admin, support, user | "admin" |
| `is_active` | bool | true/false | true |

## 🎯 Conceptos FastAPI Utilizados

✅ **FastAPI Basics**: Creación de aplicación y routing  
✅ **HTTP Methods**: GET y POST implementados  
✅ **Path Parameters**: `GET /users/{user_id}`  
✅ **Query Parameters**: Filtros por rol e is_active  
✅ **Pydantic v2**: Validación de datos con EmailStr y Literal  
✅ **Response Models**: Modelos específicos por endpoint  
✅ **HTTP Headers**: Cabeceras personalizadas (middleware)  
✅ **Status Codes**: 200, 201, 400, 404  
✅ **Exception Handling**: HTTPException y manejadores globales  
✅ **Auto Documentation**: Swagger UI y ReDoc

## 🚀 Próximos Pasos (Mejoras Futuras)

- [ ] Agregar autenticación JWT
- [ ] Implementar base de datos (PostgreSQL)
- [ ] CRUD completo (PUT, DELETE)
- [ ] Tests unitarios con pytest
- [ ] Despliegue en Docker
- [ ] CI/CD con GitHub Actions
- [ ] Logging estructurado

## 📝 Reflexión sobre FastAPI

FastAPI es un framework moderno y poderoso para construir APIs REST en Python. Durante el desarrollo de `device_systems` aprendimos:

1. **Productividad**: FastAPI permite desarrollar rápidamente con código limpio
2. **Validación**: Pydantic proporciona validación automática y mensajes de error claros
3. **Documentación**: Swagger UI se genera automáticamente desde el código
4. **Performance**: Comparado con Flask, FastAPI es significativamente más rápido
5. **Type Hints**: El uso de type hints mejora la legibilidad y permite mejor autocompletado
6. **Developer Experience**: La documentación interactiva mejora enormemente la experiencia

## 📞 Soporte

Para reportar problemas o sugerencias, abre un issue en el repositorio de GitHub.

## 📜 Licencia

Este proyecto es de código abierto y está disponible bajo la Licencia MIT.

---

**Desarrollado por**: [Tu Nombre]  
**Fecha**: 2024  
**Versión**: 1.0.0
