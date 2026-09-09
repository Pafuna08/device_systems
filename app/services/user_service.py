"""Operaciones CRUD y consultas de usuarios con SQLAlchemy."""

from typing import Optional

from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from app.models.user_model import User


def list_users(
    db: Session,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    sort_by: str = "created_at",
    sort_order: str = "asc",
) -> list[User]:
    query = select(User)
    if role is not None:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    sort_column = User.name if sort_by == "name" else User.created_at
    query = query.order_by(
        desc(sort_column) if sort_order == "desc" else asc(sort_column)
    )
    return list(db.scalars(query).all())


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    query = select(User).where(User.email == email.lower())
    return db.scalar(query)


def create_user(db: Session, user_data: dict) -> User:
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def replace_user(db: Session, user: User, user_data: dict) -> User:
    for field, value in user_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, user_data: dict) -> User:
    for field, value in user_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()