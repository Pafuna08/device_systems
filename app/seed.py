"""Creacion del esquema y datos semilla de device_systems (idempotente).

Se ejecuta al arrancar la aplicacion para garantizar que siempre existan:
- las tablas del esquema,
- una cuenta admin, una support y una user de demostracion,
- algunos dispositivos de ejemplo.

La siembra es idempotente: solo crea los registros cuyo email o serial no
existe todavia. Puede ejecutarse en cada arranque sin duplicar datos y sin
sobrescribir contrasenas que el usuario ya haya cambiado.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app.auth.security import get_password_hash
from app.database.connection import Base, SessionLocal, engine
from app.models.device_model import Device
from app.models.user_model import User

logger = logging.getLogger("device_systems.seed")

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SEED_USERS: list[dict[str, Any]] = [
    {
        "name": "Admin Usuario",
        "email": "admin@device-systems.com",
        "role": "admin",
        "is_active": True,
        "password": "Admin1234",
    },
    {
        "name": "Support Usuario",
        "email": "support@device-systems.com",
        "role": "support",
        "is_active": True,
        "password": "Support1234",
    },
    {
        "name": "Usuario Normal",
        "email": "user@device-systems.com",
        "role": "user",
        "is_active": False,
        "password": "User12345",
    },
]

SEED_DEVICES: list[dict[str, Any]] = [
    {
        "name": "Laptop Lenovo ThinkPad",
        "serial_number": "LEN-2024-001",
        "device_type": "laptop",
        "brand": "Lenovo",
        "is_available": True,
    },
    {
        "name": "Tablet Samsung Galaxy",
        "serial_number": "SAM-2024-010",
        "device_type": "tablet",
        "brand": "Samsung",
        "is_available": True,
    },
]


def _stamp_alembic_head_if_missing() -> None:
    """Marca la cabeza de Alembic cuando el esquema lo creo `create_all`.

    Si la base fue generada directamente por la aplicacion (sin pasar por
    Alembic) no existe la tabla `alembic_version`, y un `alembic upgrade head`
    posterior fallaria intentando recrear tablas ya existentes. Marcando la
    cabeza se mantiene la coherencia entre ambos caminos.

    Cualquier fallo aqui se registra como advertencia y nunca impide el
    arranque de la API.
    """
    if "alembic_version" in inspect(engine).get_table_names():
        return

    try:
        from alembic import command
        from alembic.config import Config

        alembic_ini = PROJECT_ROOT / "alembic.ini"
        if not alembic_ini.is_file():
            return
        command.stamp(Config(str(alembic_ini)), "head")
        logger.info("Esquema creado por la app: version de Alembic marcada en 'head'.")
    except Exception as exc:  # pragma: no cover - defensivo, no debe romper el arranque
        logger.warning("No se pudo marcar la version de Alembic: %s", exc)


def _seed_users(db: Session) -> int:
    """Crea las cuentas semilla que aun no existan. Retorna cuantas creo."""
    created = 0
    for seed in SEED_USERS:
        exists = db.scalar(select(User.id).where(User.email == seed["email"]))
        if exists is not None:
            continue
        db.add(
            User(
                name=seed["name"],
                email=seed["email"],
                role=seed["role"],
                is_active=seed["is_active"],
                hashed_password=get_password_hash(seed["password"]),
            )
        )
        created += 1
    return created


def _seed_devices(db: Session) -> int:
    """Crea los dispositivos semilla que aun no existan. Retorna cuantos creo."""
    created = 0
    for seed in SEED_DEVICES:
        exists = db.scalar(
            select(Device.id).where(Device.serial_number == seed["serial_number"])
        )
        if exists is not None:
            continue
        db.add(Device(**seed))
        created += 1
    return created


def initialize_database() -> None:
    """Garantiza el esquema y los datos semilla de la aplicacion."""
    Base.metadata.create_all(bind=engine)
    _stamp_alembic_head_if_missing()

    with SessionLocal() as db:
        users_created = _seed_users(db)
        devices_created = _seed_devices(db)
        db.commit()

    if users_created or devices_created:
        logger.info(
            "Datos semilla creados: users=%s devices=%s",
            users_created,
            devices_created,
        )
