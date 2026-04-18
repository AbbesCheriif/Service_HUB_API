from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from app.domain.entities.base import BaseEntity


@dataclass
class Booking(BaseEntity):
    client_id: UUID = field(default_factory=uuid4)
    service_id: UUID = field(default_factory=uuid4)
    provider_id: UUID = field(default_factory=uuid4)
    scheduled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "PENDING"
    notes: Optional[str] = None
    total_price: float = 0.0
