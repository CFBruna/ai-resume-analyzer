from src.infrastructure.llm.localai_adapter import LocalAIAdapter
from src.infrastructure.llm.openai_adapter import OpenAIAdapter
from src.presentation.api.config import Settings


def get_llm_adapter(settings: Settings) -> LocalAIAdapter | OpenAIAdapter:
    provider = settings.LLM_PROVIDER.strip().lower()
    if provider == "localai":
        return LocalAIAdapter(settings=settings)
    if provider == "openai":
        return OpenAIAdapter(settings=settings)
    raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
