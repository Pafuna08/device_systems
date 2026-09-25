"""Logica de negocio para registro y autenticacion de usuarios."""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.auth.security import get_password_hash, verify_password
from app.models.user_model import User
from app.services.user_service import create_user, get_user_by_email


def register_user(db: Session, name: str, email: str, password: str, role: str = "user") -> User:
    """Crea un usuario nuevo con la contrasena hasheada. El email se normaliza a minusculas."""
    normalized_email = email.lower()
    user = User(
        name=name,
        email=normalized_email,
        role=role,
        is_active=True,
        hashed_password=get_password_hash(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Retorna el usuario si las credenciales son validas, o None en caso contrario."""
    user = get_user_by_email(db, email.lower())
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
