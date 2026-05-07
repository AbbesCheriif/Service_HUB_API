from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ServiceCreateRequest(BaseModel):
    title: str
    description: str
    price: float = Field(gt=0)
    duration_minutes: int = Field(default=60, gt=0)
    category: str | None = None


class ServiceUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    duration_minutes: int | None = Field(default=None, gt=0)
    is_active: bool | None = None
    category: str | None = None


class ServiceResponse(BaseModel):
    id: UUID
    provider_id: UUID
    title: str
    description: str
    price: float
    duration_minutes: int
    is_active: bool
    category: str | None
    average_rating: float
    total_reviews: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
