"""
Esquemas de validación de usuarios con Pydantic v2
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, Literal

from app.schemas.auth_schema import _validate_strong_password
from pydantic import field_validator


class UserBase(BaseModel):
    """Modelo base con campos comunes"""
    name: str = Field(
        ..., 
        min_length=3, 
        max_length=100,
        description="Nombre del usuario (mínimo 3 caracteres)"
    )
    email: EmailStr = Field(
        ..., 
        description="Correo electrónico válido del usuario"
    )
    role: Literal["admin", "support", "user"] = Field(
        default="user",
        description="Rol del usuario: admin, support o user"
    )
    is_active: bool = Field(
        default=True,
        description="Estado del usuario (activo/inactivo)"
    )


class UserCreate(UserBase):
    """Modelo para crear un nuevo usuario (uso administrativo vía /users)."""
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="Minimo 8 caracteres, con mayuscula, minuscula, numero y sin espacios",
    )

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, value: str) -> str:
        return _validate_strong_password(value)


class UserUpdate(UserBase):
    """Modelo para reemplazar completamente un usuario."""
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="Minimo 8 caracteres, con mayuscula, minuscula, numero y sin espacios",
    )

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, value: str) -> str:
        return _validate_strong_password(value)


UserReplace = UserUpdate


class UserPatch(BaseModel):
    """Modelo para actualizar parcialmente un usuario."""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[Literal["admin", "support", "user"]] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return _validate_strong_password(value)


class UserResponse(UserBase):
    """Modelo de respuesta con ID incluido"""
    id: int = Field(..., description="ID único del usuario")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponseWithoutEmail(BaseModel):
    """Modelo de respuesta que incluye datos básicos del usuario."""
    id: int
    name: str
    email: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Modelo para listar múltiples usuarios"""
    users: list[UserResponse]
    total: int = Field(..., description="Total de usuarios")

    model_config = ConfigDict(from_attributes=True)
