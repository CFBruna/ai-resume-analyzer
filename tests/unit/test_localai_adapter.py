from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.domain.entities.resume import ResumeDocument, SourceType
from src.infrastructure.llm.localai_adapter import LocalAIAdapter
from src.presentation.api.config import Settings


@pytest.mark.asyncio
class TestLocalAIAdapter:
    async def test_summarize_calls_chat_completions(self) -> None:
        settings = Settings(
            MONGODB_URI="mongodb://localhost:27017",
            MONGODB_DATABASE="resume_analyzer",
            LLM_BASE_URL="http://localai:8080/v1",
            LLM_API_KEY="localai-key",
            LLM_MODEL="phi-4-mini",
        )
        adapter = LocalAIAdapter(settings)
        resume = ResumeDocument("cv.pdf", "content", SourceType.NATIVE_TEXT, 1)

        response = MagicMock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "choices": [{"message": {"content": "summary text"}}]
        }

        client = AsyncMock()
        client.__aenter__.return_value = client
        client.post.return_value = response

        with patch("httpx.AsyncClient", return_value=client):
            result = await adapter.summarize(resume)

        assert result == "summary text"
        client.post.assert_called_once()

    async def test_query_builds_prompt_with_multiple_resumes(self) -> None:
        settings = Settings(
            MONGODB_URI="mongodb://localhost:27017",
            MONGODB_DATABASE="resume_analyzer",
            LLM_BASE_URL="http://localai:8080/v1",
            LLM_API_KEY="localai-key",
            LLM_MODEL="phi-4-mini",
        )
        adapter = LocalAIAdapter(settings)
        resumes = [
            ResumeDocument("a.pdf", "alpha", SourceType.NATIVE_TEXT, 1),
            ResumeDocument("b.pdf", "beta", SourceType.OCR, 2),
        ]

        response = MagicMock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"choices": [{"message": {"content": "analysis"}}]}

        client = AsyncMock()
        client.__aenter__.return_value = client
        client.post.return_value = response

        with patch("httpx.AsyncClient", return_value=client):
            result = await adapter.query(resumes, "best candidate?")

        assert result == "analysis"
        assert client.post.call_count == 1
