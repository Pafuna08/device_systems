from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


DeviceType = Literal["laptop", "tablet", "proyector", "camara", "router", "monitor"]


class DeviceBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=150, description="Nombre del dispositivo")
    serial_number: str = Field(..., min_length=3, max_length=100, description="Número de serie único")
    device_type: DeviceType = Field(..., description="Tipo de equipo tecnológico")
    brand: Optional[str] = Field(None, max_length=100, description="Marca del dispositivo")
    is_available: bool = Field(default=True, description="Disponibilidad del equipo")


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(DeviceBase):
    pass


class DevicePatch(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=150)
    serial_number: Optional[str] = Field(None, min_length=3, max_length=100)
    device_type: Optional[DeviceType] = None
    brand: Optional[str] = Field(None, max_length=100)
    is_available: Optional[bool] = None


class DeviceResponse(DeviceBase):
    id: int = Field(..., description="Identificador del dispositivo")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeviceSummaryResponse(BaseModel):
    id: int
    name: str
    serial_number: str
    device_type: str
    brand: Optional[str] = None
    is_available: bool

    model_config = ConfigDict(from_attributes=True)
