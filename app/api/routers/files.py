import uuid as uuid_module
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.api.dependencies.auth import get_current_user
from app.application.use_cases.files.upload_file import UploadFile as UploadFileUseCase
from app.core.config.settings import get_settings
from app.domain.entities.user import User
from app.infrastructure.storage.local_storage import LocalStorage

router = APIRouter(prefix="/files", tags=["files"])

_ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/pdf",
}


class FileUploadResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    size_bytes: int
    url: str | None


@router.post(
    "/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED
)
async def upload_file(
    file: UploadFile,
    current_user: Annotated[User, Depends(get_current_user)],
):
    settings = get_settings()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if file.content_type not in _ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(_ALLOWED_MIME_TYPES))}",
        )

    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB} MB limit",
        )

    original_name = file.filename or "upload"
    ext = original_name.rsplit(".", 1)[-1] if "." in original_name else ""
    unique_name = f"{uuid_module.uuid4()}.{ext}" if ext else str(uuid_module.uuid4())

    storage = LocalStorage()
    use_case = UploadFileUseCase(storage=storage)
    result = await use_case.execute(
        uploader_id=current_user.id,
        filename=unique_name,
        content=content,
        content_type=file.content_type or "",
    )

    return FileUploadResponse(
        id=result.id,
        filename=result.filename,
        content_type=result.content_type,
        size_bytes=result.size_bytes,
        url=result.url,
    )
