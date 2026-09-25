"""Modelo SQLAlchemy de la tabla users."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("length(name) >= 3", name="ck_users_name_min_length"),
        CheckConstraint(
            "role IN ('admin', 'support', 'user')", name="ck_users_role_allowed"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    loans: Mapped[list["Loan"]] = relationship(
        "Loan",
        back_populates="user",
        cascade="all, delete-orphan",
    )