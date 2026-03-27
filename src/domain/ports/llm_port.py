from abc import ABC, abstractmethod

from src.domain.entities.resume import ResumeDocument


class LLMPort(ABC):
    @abstractmethod
    async def summarize(self, resume: ResumeDocument) -> str: ...

    @abstractmethod
    async def query(self, resumes: list[ResumeDocument], query: str) -> str: ...
