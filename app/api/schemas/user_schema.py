from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.value_objects.role import Role


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: Role
    is_active: bool
    bio: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
