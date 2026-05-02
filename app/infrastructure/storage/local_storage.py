from pathlib import Path

from app.application.interfaces.storage_interface import StorageInterface

_UPLOAD_DIR = Path("uploads")


class LocalStorage(StorageInterface):
    def __init__(self, base_dir: Path = _UPLOAD_DIR) -> None:
        self._base_dir = base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, filename: str, content: bytes, content_type: str) -> str:
        dest = self._base_dir / filename
        dest.write_bytes(content)
        return str(dest)

    async def delete(self, storage_path: str) -> None:
        path = Path(storage_path)
        if path.exists():
            path.unlink()

    def get_url(self, storage_path: str) -> str:
        return f"/static/{Path(storage_path).name}"
