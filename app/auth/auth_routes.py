"""Endpoints del recurso /auth: registro, login y perfil del usuario autenticado."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.auth_service import authenticate_user, register_user
from app.auth.security import create_access_token
from app.dependencies.auth_dependency import get_current_active_user
from app.dependencies.database_dependency import get_db
from app.middlewares.rate_limiter import limiter
from app.models.user_model import User
from app.schemas.auth_schema import Token, UserLogin, UserRegister
from app.schemas.user_schema import UserResponse
from app.services.user_service import get_user_by_email

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario",
    description=(
        "Registra un nuevo usuario con contrasena segura (hasheada con bcrypt). "
        "El autoregistro publico siempre crea usuarios con rol 'user'; "
        "los roles admin/support solo los asigna un administrador via POST /users."
    ),
    response_description="Usuario registrado",
)
@limiter.limit("3/minute")
async def register(request: Request, user_data: UserRegister, db: Session = Depends(get_db)):
    normalized_email = str(user_data.email).lower()
    if get_user_by_email(db, normalized_email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El correo '{normalized_email}' ya esta registrado en el sistema",
        )
    # El registro publico nunca permite autoasignarse admin/support.
    return register_user(
        db,
        name=user_data.name,
        email=normalized_email,
        password=user_data.password,
        role="user",
    )


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesion",
    description="Autentica un usuario con email y contrasena y retorna un token JWT (OAuth2 password flow).",
    response_description="Token de acceso",
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # OAuth2PasswordRequestForm envia 'username'; en device_systems el username es el email.
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario esta inactivo",
        )
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/login-json",
    response_model=Token,
    summary="Iniciar sesion (JSON)",
    description="Variante de /auth/login que acepta JSON {email, password} en vez de un formulario.",
    response_description="Token de acceso",
    include_in_schema=False,
)
@limiter.limit("5/minute")
async def login_json(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, email=credentials.email, password=credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Perfil del usuario autenticado",
    description="Retorna los datos del usuario duenio del token enviado en Authorization: Bearer <token>.",
    response_description="Usuario autenticado",
)
async def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user
