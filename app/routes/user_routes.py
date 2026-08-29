"""
Rutas de usuarios - Endpoints GET y POST
"""
from fastapi import APIRouter, Query, Path, HTTPException, status
from typing import Optional, Literal
from app.schemas.user_schema import (
    UserCreate, 
    UserResponse, 
    UserListResponse
)

# Inicializar router
router = APIRouter(prefix="/users", tags=["users"])

# Base de datos simulada (en memoria)
fake_users_db = {
    1: {
        "id": 1,
        "name": "Admin Usuario",
        "email": "admin@device-systems.com",
        "role": "admin",
        "is_active": True
    },
    2: {
        "id": 2,
        "name": "Support Usuario",
        "email": "support@device-systems.com",
        "role": "support",
        "is_active": True
    },
    3: {
        "id": 3,
        "name": "Usuario Normal",
        "email": "user@device-systems.com",
        "role": "user",
        "is_active": False
    }
}

# Contador para generar IDs
next_user_id = 4


@router.get(
    "",
    response_model=UserListResponse,
    summary="Obtener todos los usuarios",
    description="Retorna la lista de todos los usuarios registrados en el sistema"
)
async def get_all_users(
    role: Optional[Literal["admin", "support", "user"]] = Query(
        None,
        description="Filtrar por rol del usuario"
    ),
    is_active: Optional[bool] = Query(
        None,
        description="Filtrar por estado (activo/inactivo)"
    )
):
    """
    Obtiene todos los usuarios con filtros opcionales.
    
    Parámetros de query:
    - **role**: Filtrar por rol (admin, support, user)
    - **is_active**: Filtrar por estado activo (true/false)
    """
    users = list(fake_users_db.values())
    
    # Aplicar filtro de rol si se proporciona
    if role:
        users = [u for u in users if u["role"] == role]
    
    # Aplicar filtro de estado activo si se proporciona
    if is_active is not None:
        users = [u for u in users if u["is_active"] == is_active]
    
    return UserListResponse(users=users, total=len(users))


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obtener usuario por ID",
    description="Retorna los detalles de un usuario específico por su ID",
    responses={
        404: {"description": "Usuario no encontrado"}
    }
)
async def get_user_by_id(
    user_id: int = Path(
        ...,
        gt=0,
        description="ID único del usuario"
    )
):
    """
    Obtiene un usuario específico por su ID.
    
    Path Parameters:
    - **user_id**: ID del usuario (debe ser mayor a 0)
    """
    if user_id not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )
    
    return fake_users_db[user_id]


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo usuario",
    description="Registra un nuevo usuario en el sistema con validación de datos",
    responses={
        201: {"description": "Usuario creado exitosamente"},
        400: {"description": "Correo ya existe en el sistema"}
    }
)
async def create_user(user: UserCreate):
    """
    Crea un nuevo usuario en el sistema.
    
    Body:
    - **name**: Nombre del usuario (mínimo 3 caracteres)
    - **email**: Correo electrónico único y válido
    - **role**: Rol del usuario (admin, support, user)
    - **is_active**: Estado del usuario
    
    Validaciones:
    - El email debe ser único
    - El nombre debe tener mínimo 3 caracteres
    - El rol debe ser uno de los permitidos
    """
    global next_user_id
    
    # Validar que el email no esté duplicado
    for user_data in fake_users_db.values():
        if user_data["email"].lower() == user.email.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El correo '{user.email}' ya está registrado en el sistema"
            )
    
    # Crear nuevo usuario
    new_user = {
        "id": next_user_id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active
    }
    
    fake_users_db[next_user_id] = new_user
    next_user_id += 1
    
    return new_user
