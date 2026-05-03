from abc import ABC, abstractmethod


class StorageInterface(ABC):
    @abstractmethod
    async def save(self, filename: str, content: bytes, content_type: str) -> str: ...

    @abstractmethod
    async def delete(self, storage_path: str) -> None: ...

    @abstractmethod
    def get_url(self, storage_path: str) -> str: ...
