"""Endpoints CRUD del recurso users con persistencia SQLAlchemy."""

from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.security import get_password_hash
from app.dependencies.auth_dependency import get_current_active_user, require_admin
from app.dependencies.database_dependency import get_db
from app.dependencies.user_dependencies import get_user_or_404
from app.middlewares.rate_limiter import limiter
from app.models.user_model import User
from app.schemas.user_schema import (
    UserCreate,
    UserListResponse,
    UserPatch,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import (
    create_user,
    delete_user,
    get_user_by_email,
    list_users,
    replace_user,
    update_user,
)

router = APIRouter(prefix="/users", tags=["Users"])


def duplicate_email_error(email: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"El correo '{email}' ya esta registrado en el sistema",
    )


@router.get(
    "",
    response_model=UserListResponse,
    summary="Listar usuarios",
    description="Retorna usuarios filtrados y ordenados desde SQLite.",
    response_description="Lista de usuarios encontrados",
)
@limiter.limit("30/minute")
async def get_all_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    role: Optional[Literal["admin", "support", "user"]] = Query(
        None, description="Filtrar por rol"
    ),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado"),
    sort_by: Literal["name", "created_at"] = Query(
        "created_at", description="Campo de ordenamiento"
    ),
    sort_order: Literal["asc", "desc"] = Query(
        "asc", description="Direccion del ordenamiento"
    ),
):
    users = list_users(
        db, role=role, is_active=is_active, sort_by=sort_by, sort_order=sort_order
    )
    return UserListResponse(users=users, total=len(users))


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Consultar usuario",
    description="Retorna un usuario por su identificador desde SQLite.",
    response_description="Usuario encontrado",
)
async def get_user_by_id(
    user: User = Depends(get_user_or_404),
    current_user: User = Depends(get_current_active_user),
):
    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description=(
        "Registra un usuario en la base de datos con correo unico. "
        "Requiere rol admin (para autoregistro publico usar POST /auth/register)."
    ),
    response_description="Usuario creado",
)
async def create_new_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    normalized_email = str(user_data.email).lower()
    if get_user_by_email(db, normalized_email) is not None:
        raise duplicate_email_error(normalized_email)
    payload = user_data.model_dump()
    password = payload.pop("password")
    payload["hashed_password"] = get_password_hash(password)
    payload["email"] = normalized_email
    try:
        return create_user(db, payload)
    except IntegrityError:
        db.rollback()
        raise duplicate_email_error(normalized_email) from None


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Reemplazar usuario",
    description="Reemplaza todos los campos de un usuario existente en SQLite. Requiere rol admin.",
    response_description="Usuario actualizado completamente",
)
async def replace_existing_user(
    user_data: UserUpdate,
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    normalized_email = str(user_data.email).lower()
    existing_user = get_user_by_email(db, normalized_email)
    if existing_user is not None and existing_user.id != user.id:
        raise duplicate_email_error(normalized_email)
    payload = user_data.model_dump()
    password = payload.pop("password")
    payload["hashed_password"] = get_password_hash(password)
    payload["email"] = normalized_email
    return replace_user(db, user, payload)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario parcialmente",
    description="Modifica solo los campos enviados en la base de datos. Requiere rol admin.",
    response_description="Usuario actualizado parcialmente",
)
async def patch_existing_user(
    user_data: UserPatch,
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    changes = user_data.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )
    if "email" in changes:
        normalized_email = str(changes["email"]).lower()
        existing_user = get_user_by_email(db, normalized_email)
        if existing_user is not None and existing_user.id != user.id:
            raise duplicate_email_error(normalized_email)
        changes["email"] = normalized_email
    if "password" in changes:
        changes["hashed_password"] = get_password_hash(changes.pop("password"))
    return update_user(db, user, changes)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="Elimina un usuario de SQLite sin retornar contenido. Requiere rol admin.",
    response_description="Usuario eliminado",
)
async def delete_existing_user(
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    delete_user(db, user)