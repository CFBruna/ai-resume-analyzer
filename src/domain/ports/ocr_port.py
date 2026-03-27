from abc import ABC, abstractmethod

from src.domain.entities.resume import ResumeDocument


class OCRPort(ABC):
    @abstractmethod
    async def extract_from_pdf(
        self, file_bytes: bytes, filename: str
    ) -> ResumeDocument: ...

    @abstractmethod
    async def extract_from_image(
        self, file_bytes: bytes, filename: str
    ) -> ResumeDocument: ...
