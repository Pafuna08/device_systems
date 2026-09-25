"""
Esquemas de validacion para autenticacion (registro, login y tokens) con Pydantic v2.
"""
from __future__ import annotations

import re
from typing import Literal, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


def _validate_strong_password(value: str) -> str:
    if any(ch.isspace() for ch in value):
        raise ValueError("La contrasena no debe contener espacios en blanco")
    if len(value) < 8:
        raise ValueError("La contrasena debe tener minimo 8 caracteres")
    if not re.search(r"[A-Z]", value):
        raise ValueError("La contrasena debe tener al menos una letra mayuscula")
    if not re.search(r"[a-z]", value):
        raise ValueError("La contrasena debe tener al menos una letra minuscula")
    if not re.search(r"\d", value):
        raise ValueError("La contrasena debe tener al menos un numero")
    return value


class UserRegister(BaseModel):
    """Datos requeridos para registrar un nuevo usuario."""

    name: str = Field(..., min_length=3, max_length=100, description="Nombre completo")
    email: EmailStr = Field(..., description="Correo electronico valido y unico")
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description=(
            "Minimo 8 caracteres, con mayuscula, minuscula, numero y sin espacios"
        ),
    )
    role: Literal["admin", "support", "user"] = Field(
        default="user",
        description="Rol solicitado. El registro publico solo permite 'user'.",
    )

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, value: str) -> str:
        return _validate_strong_password(value)

    @model_validator(mode="after")
    def password_must_not_reveal_identity(self) -> "UserRegister":
        """Regla cruzada entre campos (Pydantic v2 `model_validator`).

        La contrasena no puede contener el nombre ni la parte local del correo
        del propio usuario: son datos publicos y producirian contrasenas
        predecibles (recomendacion OWASP).
        """
        password = self.password.lower()

        local_part = str(self.email).split("@", 1)[0].lower()
        if len(local_part) >= 3 and local_part in password:
            raise ValueError("La contrasena no debe contener el correo del usuario")

        compact_name = self.name.replace(" ", "").lower()
        if len(compact_name) >= 3 and compact_name in password:
            raise ValueError("La contrasena no debe contener el nombre del usuario")

        return self


class UserLogin(BaseModel):
    """Credenciales para autenticar un usuario."""

    email: EmailStr = Field(..., description="Correo electronico registrado")
    password: str = Field(..., min_length=1, description="Contrasena del usuario")


class Token(BaseModel):
    """Respuesta del endpoint de login con el token de acceso."""

    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    """Datos que viajan dentro del payload (claims) del JWT."""

    email: Optional[str] = None
    role: Optional[str] = None
