from dataclasses import dataclass, field
from typing import Optional

from app.domain.entities.base import BaseEntity
from app.domain.value_objects.email import Email
from app.domain.value_objects.role import Role


@dataclass
class User(BaseEntity):
    email: Email = field(default_factory=lambda: Email("placeholder@example.com"))
    full_name: str = ""
    hashed_password: str = ""
    role: Role = Role.CLIENT
    is_active: bool = True
    bio: Optional[str] = None
