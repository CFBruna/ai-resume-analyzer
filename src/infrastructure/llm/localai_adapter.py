from src.infrastructure.llm.base_adapter import OpenAICompatibleLLMAdapter
from src.infrastructure.llm.prompts import QUERY_PROMPT, SUMMARIZE_PROMPT
from src.presentation.api.config import Settings


class LocalAIAdapter(OpenAICompatibleLLMAdapter):
    def __init__(self, settings: Settings) -> None:
        super().__init__(
            base_url=settings.LLM_BASE_URL,
            api_key=settings.LLM_API_KEY,
            model=settings.LLM_MODEL,
            provider=settings.LLM_PROVIDER,
            timeout_seconds=settings.LLM_TIMEOUT_SECONDS,
            max_retries=settings.LLM_MAX_RETRIES,
        )

    def _summarize_prompt(self, content: str) -> str:
        return SUMMARIZE_PROMPT.format(content=content)

    def _query_prompt(self, resumes: str, query: str) -> str:
        return QUERY_PROMPT.format(resumes=resumes, query=query)
