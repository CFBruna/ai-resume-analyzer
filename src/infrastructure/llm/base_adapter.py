from __future__ import annotations

import asyncio
import logging
from typing import Any, cast

import httpx

from src.domain.entities.resume import ResumeDocument
from src.domain.ports.llm_port import LLMPort

logger = logging.getLogger(__name__)


class OpenAICompatibleLLMAdapter(LLMPort):
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        provider: str,
        timeout_seconds: float = 120.0,
        max_retries: int = 3,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._provider = provider
        self._timeout = timeout_seconds
        self._max_retries = max(1, max_retries)

    async def summarize(self, resume: ResumeDocument) -> str:
        prompt = self._summarize_prompt(resume.content)
        return await self._complete(prompt)

    async def query(self, resumes: list[ResumeDocument], query: str) -> str:
        resumes_text = "\n\n---\n\n".join(
            f"[{r.filename}]\n{r.content}" for r in resumes
        )
        prompt = self._query_prompt(resumes_text, query)
        return await self._complete(prompt)

    async def _complete(self, prompt: str) -> str:
        timeout = httpx.Timeout(self._timeout)

        for attempt in range(1, self._max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
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
            except (
                httpx.TimeoutException,
                httpx.HTTPError,
                KeyError,
                IndexError,
                TypeError,
            ) as exc:
                logger.warning(
                    "llm_request_failed",
                    extra={
                        "provider": self._provider,
                        "attempt": attempt,
                        "max_retries": self._max_retries,
                        "error_type": type(exc).__name__,
                    },
                )
                if attempt >= self._max_retries:
                    logger.exception(
                        "llm_request_exhausted",
                        extra={
                            "provider": self._provider,
                            "max_retries": self._max_retries,
                        },
                    )
                    raise

                await asyncio.sleep(0.4 * (2 ** (attempt - 1)))

        raise RuntimeError("unreachable")

    def _summarize_prompt(self, content: str) -> str:
        raise NotImplementedError

    def _query_prompt(self, resumes: str, query: str) -> str:
        raise NotImplementedError
