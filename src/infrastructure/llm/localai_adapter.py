from typing import Any, cast

import httpx

from src.domain.entities.resume import ResumeDocument
from src.domain.ports.llm_port import LLMPort
from src.presentation.api.config import Settings

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


class LocalAIAdapter(LLMPort):
    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.LLM_BASE_URL
        self._api_key = settings.LLM_API_KEY
        self._model = settings.LLM_MODEL

    async def summarize(self, resume: ResumeDocument) -> str:
        prompt = SUMMARIZE_PROMPT.format(content=resume.content)
        return await self._complete(prompt)

    async def query(self, resumes: list[ResumeDocument], query: str) -> str:
        resumes_text = "\n\n---\n\n".join(
            f"[{r.filename}]\n{r.content}" for r in resumes
        )
        prompt = QUERY_PROMPT.format(resumes=resumes_text, query=query)
        return await self._complete(prompt)

    async def _complete(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self._base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self._model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 1500,
                },
            )
            response.raise_for_status()
            data = cast(dict[str, Any], response.json())
            choices = cast(list[dict[str, Any]], data["choices"])
            message = cast(dict[str, Any], choices[0]["message"])
            content = cast(str, message["content"])
            return content.strip()
