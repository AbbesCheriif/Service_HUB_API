from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4

from app.domain.entities.base import BaseEntity


@dataclass
class Service(BaseEntity):
    provider_id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: str = ""
    price: float = 0.0
    duration_minutes: int = 60
    is_active: bool = True
    category: Optional[str] = None
    average_rating: float = 0.0
    total_reviews: int = 0
