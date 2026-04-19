from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from app.domain.entities.base import BaseEntity
from app.domain.value_objects.booking_status import BookingStatus


@dataclass
class Booking(BaseEntity):
    client_id: UUID = field(default_factory=uuid4)
    service_id: UUID = field(default_factory=uuid4)
    provider_id: UUID = field(default_factory=uuid4)
    scheduled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: BookingStatus = BookingStatus.PENDING
    notes: Optional[str] = None
    total_price: float = 0.0
