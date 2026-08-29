# 🚀 QUICKSTART - device_systems API

Guía rápida para iniciar el proyecto localmente.

## ⚡ Iniciación Rápida (5 minutos)

### 1. Crear entorno virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Iniciar servidor
```bash
# Modo desarrollo (con recarga automática)
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Acceder a la API
- **Página principal**: http://127.0.0.1:8000
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 📝 Ejemplos Rápidos

### Obtener todos los usuarios
```bash
curl http://127.0.0.1:8000/users
```

### Crear nuevo usuario
```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan Pérez",
    "email": "juan@device-systems.com",
    "role": "user",
    "is_active": true
  }'
```

### Filtrar por rol
```bash
curl "http://127.0.0.1:8000/users?role=admin"
```

### Obtener usuario por ID
```bash
curl http://127.0.0.1:8000/users/1
```

## 📊 Probar en Postman/Thunder Client

1. **Importar colección**:
   - Postman: `device_systems_postman.json`
   - Thunder Client: `device_systems_thunder.json`

2. **Ejecutar requests** desde la interfaz gráfica

## 🐛 Troubleshooting

### Error: "No module named 'fastapi'"
- Solución: Asegúrate de activar el entorno virtual y ejecutar `pip install -r requirements.txt`

### Error: "Address already in use"
- Solución: Cambia el puerto con `--port 9000`

### Error de email duplicado
- Solución: Usa un email único para crear nuevo usuario

## 📚 Documentación Completa

Consulta [README.md](README.md) para documentación completa
