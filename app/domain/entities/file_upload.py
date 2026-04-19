from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4

from app.domain.entities.base import BaseEntity


@dataclass
class FileUpload(BaseEntity):
    uploader_id: UUID = field(default_factory=uuid4)
    filename: str = ""
    content_type: str = ""
    size_bytes: int = 0
    storage_path: str = ""
    url: Optional[str] = None
