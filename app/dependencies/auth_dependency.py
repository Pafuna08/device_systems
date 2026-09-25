"""Dependencias de autenticacion (OAuth2 + JWT) y autorizacion por rol."""
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.dependencies.database_dependency import get_db
from app.models.user_model import User
from app.services.user_service import get_user_by_email

# El tokenUrl apunta al endpoint de login; Swagger UI usa esto para el boton "Authorize".
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No se pudo validar las credenciales",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Extrae y valida el usuario autenticado a partir del token JWT enviado."""
    payload = decode_access_token(token)
    if payload is None:
        raise CREDENTIALS_EXCEPTION
    email: str | None = payload.get("sub")
    if email is None:
        raise CREDENTIALS_EXCEPTION
    user = get_user_by_email(db, email)
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user


def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    """Exige ademas que el usuario autenticado este activo."""
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario esta inactivo",
        )
    return user


def require_admin(user: User = Depends(get_current_active_user)) -> User:
    """Exige rol admin."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta operacion requiere rol admin",
        )
    return user


def require_admin_or_support(user: User = Depends(get_current_active_user)) -> User:
    """Exige rol admin o support."""
    if user.role not in ("admin", "support"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta operacion requiere rol admin o support",
        )
    return user
