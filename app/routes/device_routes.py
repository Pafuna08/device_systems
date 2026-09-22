from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.models.device_model import Device
from app.schemas.device_schema import DeviceCreate, DevicePatch, DeviceResponse, DeviceUpdate
from app.services.device_service import (
    create_device,
    delete_device,
    get_device_by_id,
    get_device_by_serial_number,
    list_devices,
    update_device,
)

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.get(
    "",
    response_model=list[DeviceResponse],
    summary="Listar dispositivos",
    description="Retorna dispositivos con filtros por tipo, disponibilidad, marca y texto libre.",
    response_description="Listado de dispositivos",
)
async def get_all_devices(
    db: Session = Depends(get_db),
    device_type: Optional[str] = Query(None, description="Filtrar por tipo de dispositivo"),
    is_available: Optional[bool] = Query(None, description="Filtrar por disponibilidad"),
    brand: Optional[str] = Query(None, description="Filtrar por marca"),
    search: Optional[str] = Query(None, description="Buscar por nombre, marca, serial o tipo"),
):
    return list_devices(
        db,
        device_type=device_type,
        is_available=is_available,
        brand=brand,
        search=search,
    )


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Consultar dispositivo",
    description="Retorna un dispositivo por su identificador.",
    response_description="Dispositivo encontrado",
)
async def get_device(device_id: int, db: Session = Depends(get_db)):
    device = get_device_by_id(db, device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado")
    return device


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear dispositivo",
    description="Registra un nuevo dispositivo disponible para préstamo.",
    response_description="Dispositivo creado",
)
async def create_new_device(device_data: DeviceCreate, db: Session = Depends(get_db)):
    if get_device_by_serial_number(db, device_data.serial_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El número de serie '{device_data.serial_number}' ya existe",
        )
    return create_device(db, device_data.model_dump())


@router.put(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Reemplazar dispositivo",
    description="Sobrescribe la información completa de un dispositivo.",
    response_description="Dispositivo actualizado",
)
async def replace_existing_device(
    device_id: int,
    device_data: DeviceUpdate,
    db: Session = Depends(get_db),
):
    device = get_device_by_id(db, device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado")
    if device_data.serial_number != device.serial_number:
        existing = get_device_by_serial_number(db, device_data.serial_number)
        if existing and existing.id != device.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Número de serie duplicado")
    return update_device(db, device, device_data.model_dump())


@router.patch(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Actualizar dispositivo parcialmente",
    description="Actualiza solo los campos enviados por el cliente.",
    response_description="Dispositivo actualizado parcialmente",
)
async def patch_existing_device(
    device_id: int,
    device_data: DevicePatch,
    db: Session = Depends(get_db),
):
    device = get_device_by_id(db, device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado")
    changes = device_data.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debe enviar al menos un campo")
    if 'serial_number' in changes:
        existing = get_device_by_serial_number(db, changes['serial_number'])
        if existing and existing.id != device.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Número de serie duplicado")
    return update_device(db, device, changes)


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar dispositivo",
    description="Elimina físicamente un dispositivo de la base de datos.",
    response_description="Dispositivo eliminado",
)
async def delete_existing_device(device_id: int, db: Session = Depends(get_db)):
    device = get_device_by_id(db, device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado")
    delete_device(db, device)
