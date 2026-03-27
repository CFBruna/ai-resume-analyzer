import pytest

from src.infrastructure.llm.llm_factory import get_llm_adapter
from src.infrastructure.llm.localai_adapter import LocalAIAdapter
from src.infrastructure.llm.openai_adapter import OpenAIAdapter
from src.presentation.api.config import Settings


def make_settings(provider: str) -> Settings:
    return Settings(
        MONGODB_URI="mongodb://localhost:27017",
        MONGODB_DATABASE="resume_analyzer",
        LLM_PROVIDER=provider,
        LLM_BASE_URL="http://llm:8080/v1",
        LLM_API_KEY="key",
        LLM_MODEL="model",
        LLM_TIMEOUT_SECONDS=1.0,
        LLM_MAX_RETRIES=2,
    )


class TestLLMFactory:
    def test_returns_localai_adapter(self) -> None:
        adapter = get_llm_adapter(make_settings("localai"))
        assert isinstance(adapter, LocalAIAdapter)

    def test_returns_openai_adapter(self) -> None:
        adapter = get_llm_adapter(make_settings("openai"))
        assert isinstance(adapter, OpenAIAdapter)

    def test_rejects_unknown_provider(self) -> None:
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            get_llm_adapter(make_settings("other"))
