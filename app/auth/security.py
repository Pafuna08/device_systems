"""
Utilidades de seguridad para device_systems.

Contiene:
- Hash y verificacion de contrasenas con passlib (bcrypt).
- Creacion y validacion de tokens JWT (OAuth2) con python-jose.

Ninguna contrasena debe guardarse ni mostrarse en texto plano.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

# --------------------------------------------------------------------------
# Configuracion (se lee de variables de entorno, ver .env / .env.example)
# --------------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-change-me-in-.env")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --------------------------------------------------------------------------
# Contrasenas
# --------------------------------------------------------------------------
def get_password_hash(password: str) -> str:
    """Genera el hash bcrypt de una contrasena en texto plano."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que una contrasena en texto plano coincida con su hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, TypeError):
        # Hash invalido/corrupto (p. ej. cuentas migradas sin password real).
        return False


# --------------------------------------------------------------------------
# JWT
# --------------------------------------------------------------------------
def create_access_token(
    data: dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Crea un token JWT firmado a partir de un payload (claims)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """Decodifica y valida un token JWT. Retorna None si es invalido/expirado."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
