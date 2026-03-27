from src.domain.entities.resume import ResumeDocument
from src.domain.ports.llm_port import LLMPort


class SummarizeResumesUseCase:
    def __init__(self, llm: LLMPort) -> None:
        self._llm = llm

    async def execute(self, resumes: list[ResumeDocument]) -> list[dict]:
        summaries: list[dict] = []

        for resume in resumes:
            summary = await self._llm.summarize(resume)
            summaries.append(
                {
                    "filename": resume.filename,
                    "source_type": resume.source_type.value,
                    "page_count": resume.page_count,
                    "summary": summary,
                }
            )

        return summaries
