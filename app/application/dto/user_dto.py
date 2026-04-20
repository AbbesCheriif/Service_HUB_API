from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.domain.value_objects.role import Role


class UserCreateDTO(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: Role = Role.CLIENT


class UserReadDTO(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: Role
    is_active: bool
    bio: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateDTO(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    is_active: Optional[bool] = None
