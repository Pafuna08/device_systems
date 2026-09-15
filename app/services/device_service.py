from __future__ import annotations

from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.device_model import Device


def list_devices(
    db: Session,
    device_type: Optional[str] = None,
    is_available: Optional[bool] = None,
    brand: Optional[str] = None,
    search: Optional[str] = None,
) -> list[Device]:
    query = select(Device)
    if device_type is not None:
        query = query.where(Device.device_type == device_type)
    if is_available is not None:
        query = query.where(Device.is_available == is_available)
    if brand is not None:
        query = query.where(Device.brand == brand)
    if search:
        term = f"%{search.lower()}%"
        query = query.where(
            or_(
                Device.name.ilike(term),
                Device.serial_number.ilike(term),
                Device.device_type.ilike(term),
                Device.brand.ilike(term),
            )
        )
    query = query.order_by(Device.created_at.desc())
    return list(db.scalars(query).all())


def get_device_by_id(db: Session, device_id: int) -> Optional[Device]:
    return db.get(Device, device_id)


def get_device_by_serial_number(db: Session, serial_number: str) -> Optional[Device]:
    return db.scalar(select(Device).where(Device.serial_number == serial_number))


def create_device(db: Session, device_data: dict) -> Device:
    device = Device(**device_data)
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def update_device(db: Session, device: Device, device_data: dict) -> Device:
    for field, value in device_data.items():
        setattr(device, field, value)
    db.commit()
    db.refresh(device)
    return device


def delete_device(db: Session, device: Device) -> None:
    db.delete(device)
    db.commit()
