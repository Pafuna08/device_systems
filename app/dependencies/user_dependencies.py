"""Dependencias reutilizables para usuarios y sesiones SQLAlchemy."""

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.models.user_model import User
from app.services.user_service import get_user_by_id


def get_user_or_404(
    user_id: int = Path(..., gt=0, description="ID unico del usuario"),
    db: Session = Depends(get_db),
) -> User:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado",
        )
    return user