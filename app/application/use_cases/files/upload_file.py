from uuid import UUID

from app.application.interfaces.storage_interface import StorageInterface
from app.domain.entities.file_upload import FileUpload


class UploadFile:
    def __init__(self, storage: StorageInterface) -> None:
        self._storage = storage

    async def execute(
        self,
        uploader_id: UUID,
        filename: str,
        content: bytes,
        content_type: str,
    ) -> FileUpload:
        storage_path = await self._storage.save(filename, content, content_type)
        url = self._storage.get_url(storage_path)

        return FileUpload(
            uploader_id=uploader_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(content),
            storage_path=storage_path,
            url=url,
        )
