from src.domain.entities.resume import ResumeDocument
from src.domain.ports.llm_port import LLMPort


class QueryResumesUseCase:
    def __init__(self, llm: LLMPort) -> None:
        self._llm = llm

    async def execute(self, resumes: list[ResumeDocument], query: str) -> str:
        return await self._llm.query(resumes, query)
