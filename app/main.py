"""
Aplicacion principal de FastAPI - device_systems (v3.0.0 - EV11 Seguridad)
API REST para la gestion de usuarios, dispositivos y prestamos, protegida con
OAuth2 + JWT, middleware personalizado, CORS y rate limiting.
"""
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.auth import auth_routes
from app.middlewares.rate_limiter import limiter
from app.middlewares.request_middleware import RequestTracingMiddleware

# Se importan los modelos para que Base.metadata conozca todas las tablas
# antes de ejecutar create_all() dentro de initialize_database().
from app.models.device_model import Device  # noqa: F401
from app.models.loan_model import Loan  # noqa: F401
from app.models.user_model import User  # noqa: F401
from app.routes import device_routes, loan_routes, user_routes
from app.seed import initialize_database

initialize_database()

# Crear aplicacion FastAPI
app = FastAPI(
    title="device_systems API",
    description=(
        "API REST segura para la gestion de usuarios, dispositivos y prestamos, "
        "con autenticacion OAuth2 + JWT, control de roles, middleware de "
        "trazabilidad, CORS y rate limiting."
    ),
    version="3.0.0",
    contact={"name": "Pafuna08", "url": "https://github.com/Pafuna08/device_systems"},
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Auth", "description": "Registro, login (OAuth2 + JWT) y perfil del usuario autenticado."},
        {"name": "Users", "description": "Gestion de usuarios. Requiere autenticacion; escritura requiere rol admin."},
        {"name": "Devices", "description": "Gestion de dispositivos. Escritura requiere rol admin o support."},
        {"name": "Loans", "description": "Gestion de prestamos. Requiere autenticacion; algunas rutas requieren rol admin/support."},
        {"name": "Security", "description": "Endpoints de estado y salud de la API."},
    ],
)

# --- Fase 11: Rate limiting (slowapi) -------------------------------------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Fase 9: CORS -----------------------------------------------------------
# En desarrollo se permiten explicitamente los origenes del frontend local.
# En produccion NUNCA se debe usar allow_origins=["*"] junto con
# allow_credentials=True: el estandar CORS prohibe combinar comodin de origen
# con credenciales (cookies/Authorization), y hacerlo expondria la API a
# peticiones autenticadas desde cualquier sitio malicioso. Se debe listar
# explicitamente cada dominio autorizado del frontend en produccion.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Fase 10: Middleware personalizado de trazabilidad -----------------------
app.add_middleware(RequestTracingMiddleware)

# Incluir rutas
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(device_routes.router)
app.include_router(loan_routes.router)


@app.get(
    "/",
    response_class=HTMLResponse,
    summary="Pagina principal",
    description="Pagina de bienvenida a la API",
    tags=["Security"],
)
async def root():
    """
    Pagina principal de bienvenida a la API device_systems
    """
    return """
    <html>
        <head>
            <title>device_systems API</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    background-color: #f5f5f5;
                }
                .container {
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 { color: #333; }
                p { color: #666; }
                .link {
                    display: inline-block;
                    margin: 10px 10px 10px 0;
                    padding: 10px 15px;
                    background-color: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                }
                .link:hover { background-color: #0056b3; }
                .info {
                    background-color: #e7f3ff;
                    padding: 15px;
                    border-left: 4px solid #007bff;
                    border-radius: 4px;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Bienvenido a device_systems API (v3.0.0 - Seguridad)</h1>
                <p>API REST protegida con OAuth2 + JWT para la gestion de usuarios, dispositivos y prestamos.</p>

                <div class="info">
                    <h3>Documentacion Interactiva</h3>
                    <a href="/docs" class="link">Swagger UI</a>
                    <a href="/redoc" class="link">ReDoc</a>
                </div>

                <div class="info">
                    <h3>Autenticacion</h3>
                    <ul>
                        <li><strong>POST /auth/register</strong> - Registrar usuario</li>
                        <li><strong>POST /auth/login</strong> - Iniciar sesion (retorna JWT)</li>
                        <li><strong>GET /auth/me</strong> - Perfil del usuario autenticado</li>
                    </ul>
                </div>

                <div class="info">
                    <h3>Cabeceras HTTP Personalizadas</h3>
                    <ul>
                        <li><strong>X-App-Name</strong>: device_systems</li>
                        <li><strong>X-Process-Time</strong>: tiempo de respuesta</li>
                        <li><strong>X-Request-ID</strong>: identificador de la peticion</li>
                    </ul>
                </div>
            </div>
        </body>
    </html>
    """


@app.get(
    "/health",
    summary="Health Check",
    description="Verifica que la API este funcionando",
    tags=["Security"],
)
async def health_check():
    """
    Endpoint para verificar que la API esta en linea
    """
    return {
        "status": "healthy",
        "service": "device_systems",
        "version": "3.0.0",
    }


# Manejador de excepciones global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Manejador global de excepciones
    """
    return JSONResponse(
        status_code=500,
        content={"error": True, "message": "Ocurrio un error en el servidor"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
