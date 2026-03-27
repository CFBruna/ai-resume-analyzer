from unittest.mock import AsyncMock

import pytest

from src.application.use_cases.query_resumes import QueryResumesUseCase
from src.domain.entities.resume import ResumeDocument, SourceType


@pytest.mark.asyncio
class TestQueryResumesUseCase:
    async def test_delegates_query_to_llm(self) -> None:
        mock_llm = AsyncMock()
        mock_llm.query = AsyncMock(return_value="analysis")
        use_case = QueryResumesUseCase(llm=mock_llm)
        resumes = [ResumeDocument("a.pdf", "content", SourceType.NATIVE_TEXT, 1)]

        result = await use_case.execute(resumes, "best candidate?")

        assert result == "analysis"
        mock_llm.query.assert_awaited_once_with(resumes, "best candidate?")
