from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.dependencies.auth_dependency import get_current_active_user, require_admin_or_support
from app.dependencies.database_dependency import get_db
from app.middlewares.rate_limiter import limiter
from app.models.user_model import User
from app.schemas.loan_schema import LoanCreate, LoanDetailResponse, LoanResponse
from app.services.device_service import get_device_by_id
from app.services.loan_service import (
    create_loan,
    get_loan_by_id,
    get_loans_by_device,
    get_loans_by_user,
    list_loans,
    return_loan,
)
from app.services.user_service import get_user_by_id

router = APIRouter(tags=["Loans"])


@router.get(
    "/loans",
    response_model=list[LoanDetailResponse],
    summary="Listar préstamos",
    description="Consulta préstamos con información relacionada de usuario y dispositivo y filtros avanzados.",
    response_description="Lista de préstamos",
)
async def get_all_loans(
    db: Session = Depends(get_db),
    status: str | None = Query(None, description="Filtrar por estado del préstamo"),
    user_email: str | None = Query(None, description="Buscar por email del usuario"),
    device_type: str | None = Query(None, description="Filtrar por tipo de dispositivo"),
    user_id: int | None = Query(None, description="Filtrar por usuario"),
    device_id: int | None = Query(None, description="Filtrar por dispositivo"),
    search: str | None = Query(None, description="Búsqueda libre"),
):
    loans = list_loans(
        db,
        status=status,
        user_email=user_email,
        device_type=device_type,
        user_id=user_id,
        device_id=device_id,
        search=search,
    )
    result = []
    for loan in loans:
        result.append(
            LoanDetailResponse(
                id=loan.id,
                status=loan.status,
                loan_date=loan.loan_date,
                return_date=loan.return_date,
                user={
                    'id': loan.user.id,
                    'name': loan.user.name,
                    'email': loan.user.email,
                    'role': loan.user.role,
                    'is_active': loan.user.is_active,
                },
                device={
                    'id': loan.device.id,
                    'name': loan.device.name,
                    'serial_number': loan.device.serial_number,
                    'device_type': loan.device.device_type,
                    'brand': loan.device.brand,
                    'is_available': loan.device.is_available,
                },
            )
        )
    return result


@router.get(
    "/loans/details",
    response_model=list[LoanDetailResponse],
    summary="Consultar detalles de préstamos",
    description="Consulta detallada de préstamos con información combinada de usuario y dispositivo mediante joins y filtros. Requiere rol admin o support.",
    response_description="Lista detallada de préstamos",
)
async def get_loans_details(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_support),
    status: str | None = Query(None, description="Filtrar por estado del préstamo"),
    user_email: str | None = Query(None, description="Buscar por email del usuario"),
    device_type: str | None = Query(None, description="Filtrar por tipo de dispositivo"),
    user_id: int | None = Query(None, description="Filtrar por usuario"),
    device_id: int | None = Query(None, description="Filtrar por dispositivo"),
    search: str | None = Query(None, description="Búsqueda libre"),
):
    loans = list_loans(
        db,
        status=status,
        user_email=user_email,
        device_type=device_type,
        user_id=user_id,
        device_id=device_id,
        search=search,
    )
    result = []
    for loan in loans:
        result.append(
            LoanDetailResponse(
                id=loan.id,
                status=loan.status,
                loan_date=loan.loan_date,
                return_date=loan.return_date,
                user={
                    'id': loan.user.id,
                    'name': loan.user.name,
                    'email': loan.user.email,
                    'role': loan.user.role,
                    'is_active': loan.user.is_active,
                },
                device={
                    'id': loan.device.id,
                    'name': loan.device.name,
                    'serial_number': loan.device.serial_number,
                    'device_type': loan.device.device_type,
                    'brand': loan.device.brand,
                    'is_available': loan.device.is_available,
                },
            )
        )
    return result


@router.get(
    "/loans/{loan_id}",
    response_model=LoanDetailResponse,
    summary="Consultar préstamo",
    description="Retorna los datos de un préstamo con información del usuario y del dispositivo.",
    response_description="Préstamo encontrado",
)
async def get_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = get_loan_by_id(db, loan_id)
    if loan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Préstamo no encontrado")
    return LoanDetailResponse(
        id=loan.id,
        status=loan.status,
        loan_date=loan.loan_date,
        return_date=loan.return_date,
        user={
            'id': loan.user.id,
            'name': loan.user.name,
            'email': loan.user.email,
            'role': loan.user.role,
            'is_active': loan.user.is_active,
        },
        device={
            'id': loan.device.id,
            'name': loan.device.name,
            'serial_number': loan.device.serial_number,
            'device_type': loan.device.device_type,
            'brand': loan.device.brand,
            'is_available': loan.device.is_available,
        },
    )


@router.post(
    "/loans",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear préstamo",
    description="Registra un préstamo siempre que el usuario y el dispositivo existan y el equipo esté disponible.",
    response_description="Préstamo creado",
)
@limiter.limit("10/minute")
async def create_new_loan(
    request: Request,
    loan_data: LoanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    user = get_user_by_id(db, loan_data.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    device = get_device_by_id(db, loan_data.device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado")
    if not device.is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El dispositivo no está disponible para préstamo",
        )
    loan_payload = loan_data.model_dump()
    loan_payload['loan_date'] = loan_data.loan_date or datetime.utcnow()
    loan_payload['status'] = loan_data.status or 'active'
    created_loan = create_loan(db, loan_payload)
    device.is_available = False
    db.commit()
    db.refresh(device)
    return created_loan


@router.patch(
    "/loans/{loan_id}/return",
    response_model=LoanResponse,
    summary="Devolver préstamo",
    description="Marca un préstamo como devuelto y vuelve a poner el dispositivo disponible. Requiere rol admin o support.",
    response_description="Préstamo devuelto",
)
async def return_existing_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_support),
):
    loan = get_loan_by_id(db, loan_id)
    if loan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Préstamo no encontrado")
    if loan.status == 'returned':
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El préstamo ya fue devuelto")
    device = get_device_by_id(db, loan.device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado")
    return_loan(db, loan, device)
    return loan


@router.get(
    "/users/{user_id}/loans",
    response_model=list[LoanDetailResponse],
    summary="Consultar préstamos de un usuario",
    description="Lista todos los préstamos asociados a un usuario con datos del dispositivo.",
    response_description="Historial de préstamos del usuario",
)
async def get_loans_by_user_id(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    loans = get_loans_by_user(db, user_id)
    result = []
    for loan in loans:
        result.append(
            LoanDetailResponse(
                id=loan.id,
                status=loan.status,
                loan_date=loan.loan_date,
                return_date=loan.return_date,
                user={
                    'id': loan.user.id,
                    'name': loan.user.name,
                    'email': loan.user.email,
                    'role': loan.user.role,
                    'is_active': loan.user.is_active,
                },
                device={
                    'id': loan.device.id,
                    'name': loan.device.name,
                    'serial_number': loan.device.serial_number,
                    'device_type': loan.device.device_type,
                    'brand': loan.device.brand,
                    'is_available': loan.device.is_available,
                },
            )
        )
    return result


@router.get(
    "/devices/{device_id}/loans",
    response_model=list[LoanDetailResponse],
    summary="Consultar historial de un dispositivo",
    description="Lista el historial de préstamos de un equipo concreto.",
    response_description="Historial del dispositivo",
)
async def get_loans_by_device_id(device_id: int, db: Session = Depends(get_db)):
    device = get_device_by_id(db, device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado")
    loans = get_loans_by_device(db, device_id)
    result = []
    for loan in loans:
        result.append(
            LoanDetailResponse(
                id=loan.id,
                status=loan.status,
                loan_date=loan.loan_date,
                return_date=loan.return_date,
                user={
                    'id': loan.user.id,
                    'name': loan.user.name,
                    'email': loan.user.email,
                    'role': loan.user.role,
                    'is_active': loan.user.is_active,
                },
                device={
                    'id': loan.device.id,
                    'name': loan.device.name,
                    'serial_number': loan.device.serial_number,
                    'device_type': loan.device.device_type,
                    'brand': loan.device.brand,
                    'is_available': loan.device.is_available,
                },
            )
        )
    return result
