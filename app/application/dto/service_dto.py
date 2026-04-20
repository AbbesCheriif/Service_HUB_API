from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ServiceCreateDTO(BaseModel):
    title: str
    description: str
    price: float = Field(gt=0)
    duration_minutes: int = Field(default=60, gt=0)
    category: Optional[str] = None


class ServiceReadDTO(BaseModel):
    id: UUID
    provider_id: UUID
    title: str
    description: str
    price: float
    duration_minutes: int
    is_active: bool
    category: Optional[str]
    average_rating: float
    total_reviews: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ServiceUpdateDTO(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    duration_minutes: Optional[int] = Field(default=None, gt=0)
    is_active: Optional[bool] = None
    category: Optional[str] = None
