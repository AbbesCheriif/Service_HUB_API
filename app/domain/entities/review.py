from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4

from app.domain.entities.base import BaseEntity


@dataclass
class Review(BaseEntity):
    booking_id: UUID = field(default_factory=uuid4)
    client_id: UUID = field(default_factory=uuid4)
    service_id: UUID = field(default_factory=uuid4)
    rating: int = 5
    comment: Optional[str] = None
