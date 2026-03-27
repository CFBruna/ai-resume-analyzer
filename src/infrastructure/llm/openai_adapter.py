from src.infrastructure.llm.base_adapter import OpenAICompatibleLLMAdapter
from src.presentation.api.config import Settings


class OpenAIAdapter(OpenAICompatibleLLMAdapter):
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


SUMMARIZE_PROMPT = """You are an expert technical recruiter. Analyze the resume below and provide a structured summary in the same language as the resume content.

Include:
- Full name (if found)
- Key technical skills
- Years of experience (estimated)
- Most recent position
- Educational background
- Notable achievements

Resume content:
{content}

Provide a clear, concise summary."""


QUERY_PROMPT = """You are an expert technical recruiter. Analyze the resumes below and answer the recruiter's question with a detailed justification for each candidate.

Resumes:
{resumes}

Recruiter question: {query}

For each candidate, provide:
1. Candidate name (or filename if name not found)
2. Match assessment (Strong Match / Partial Match / No Match)
3. Justification based on specific evidence from the resume

Be objective and evidence-based."""
