from dataclasses import dataclass, field
from typing import Optional

from app.domain.entities.base import BaseEntity


@dataclass
class User(BaseEntity):
    email: str = ""
    full_name: str = ""
    hashed_password: str = ""
    role: str = "CLIENT"
    is_active: bool = True
    bio: Optional[str] = None
