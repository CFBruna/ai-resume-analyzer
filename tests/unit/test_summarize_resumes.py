from unittest.mock import AsyncMock

import pytest

from src.application.use_cases.summarize_resumes import SummarizeResumesUseCase
from src.domain.entities.resume import ResumeDocument, SourceType


@pytest.mark.asyncio
class TestSummarizeResumesUseCase:
    async def test_returns_summaries_for_each_resume(self) -> None:
        mock_llm = AsyncMock()
        mock_llm.summarize = AsyncMock(side_effect=["sum 1", "sum 2"])
        use_case = SummarizeResumesUseCase(llm=mock_llm)
        resumes = [
            ResumeDocument("a.pdf", "content 1", SourceType.NATIVE_TEXT, 1),
            ResumeDocument("b.pdf", "content 2", SourceType.OCR, 2),
        ]

        result = await use_case.execute(resumes)

        assert result == [
            {
                "filename": "a.pdf",
                "source_type": "native_text",
                "page_count": 1,
                "summary": "sum 1",
            },
            {
                "filename": "b.pdf",
                "source_type": "ocr",
                "page_count": 2,
                "summary": "sum 2",
            },
        ]
