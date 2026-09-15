from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.device_schema import DeviceSummaryResponse
from app.schemas.user_schema import UserResponseWithoutEmail

LoanStatus = Literal["active", "returned", "overdue"]


class LoanBase(BaseModel):
    user_id: int = Field(..., gt=0, description="Identificador del usuario")
    device_id: int = Field(..., gt=0, description="Identificador del dispositivo")
    loan_date: datetime = Field(default_factory=datetime.utcnow, description="Fecha del préstamo")
    return_date: Optional[datetime] = Field(None, description="Fecha de devolución si aplica")
    status: LoanStatus = Field(default="active", description="Estado del préstamo")


class LoanCreate(LoanBase):
    pass


class LoanUpdate(BaseModel):
    status: Optional[LoanStatus] = None
    return_date: Optional[datetime] = None


class LoanResponse(LoanBase):
    id: int = Field(..., description="Identificador del préstamo")

    model_config = ConfigDict(from_attributes=True)


class LoanDetailResponse(BaseModel):
    id: int
    status: str
    loan_date: datetime
    return_date: Optional[datetime] = None
    user: UserResponseWithoutEmail
    device: DeviceSummaryResponse

    model_config = ConfigDict(from_attributes=True)
