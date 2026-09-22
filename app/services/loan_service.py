from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User


def list_loans(
    db: Session,
    status: Optional[str] = None,
    user_email: Optional[str] = None,
    device_type: Optional[str] = None,
    user_id: Optional[int] = None,
    device_id: Optional[int] = None,
    search: Optional[str] = None,
) -> list[Loan]:
    query = select(Loan).join(User, Loan.user_id == User.id).join(Device, Loan.device_id == Device.id)
    conditions = []
    if status is not None:
        conditions.append(Loan.status == status)
    if user_email is not None:
        conditions.append(User.email.ilike(f"%{user_email}%"))
    if device_type is not None:
        conditions.append(Device.device_type.ilike(f"%{device_type}%"))
    if user_id is not None:
        conditions.append(Loan.user_id == user_id)
    if device_id is not None:
        conditions.append(Loan.device_id == device_id)
    if search:
        conditions.append(
            or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                Device.name.ilike(f"%{search}%"),
                Device.serial_number.ilike(f"%{search}%"),
            )
        )
    if conditions:
        query = query.where(and_(*conditions))
    query = query.order_by(Loan.loan_date.desc())
    return list(db.scalars(query).all())


def get_loan_by_id(db: Session, loan_id: int) -> Optional[Loan]:
    return db.get(Loan, loan_id)


def create_loan(db: Session, loan_data: dict) -> Loan:
    loan = Loan(**loan_data)
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def update_loan(db: Session, loan: Loan, loan_data: dict) -> Loan:
    for field, value in loan_data.items():
        setattr(loan, field, value)
    db.commit()
    db.refresh(loan)
    return loan


def return_loan(db: Session, loan: Loan, device: Device) -> Loan:
    loan.status = "returned"
    loan.return_date = datetime.utcnow()
    device.is_available = True
    db.commit()
    db.refresh(loan)
    db.refresh(device)
    return loan


def get_loans_by_user(db: Session, user_id: int) -> list[Loan]:
    return list(db.scalars(select(Loan).where(Loan.user_id == user_id).order_by(Loan.loan_date.desc())).all())


def get_loans_by_device(db: Session, device_id: int) -> list[Loan]:
    return list(db.scalars(select(Loan).where(Loan.device_id == device_id).order_by(Loan.loan_date.desc())).all())
