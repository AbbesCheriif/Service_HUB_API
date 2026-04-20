from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.domain.value_objects.booking_status import BookingStatus


class BookingCreateDTO(BaseModel):
    service_id: UUID
    scheduled_at: datetime
    notes: Optional[str] = None


class BookingReadDTO(BaseModel):
    id: UUID
    client_id: UUID
    service_id: UUID
    provider_id: UUID
    scheduled_at: datetime
    status: BookingStatus
    notes: Optional[str]
    total_price: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BookingUpdateDTO(BaseModel):
    status: Optional[BookingStatus] = None
    notes: Optional[str] = None
