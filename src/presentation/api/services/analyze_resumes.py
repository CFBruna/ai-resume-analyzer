from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

from fastapi import UploadFile

from src.application.use_cases.process_documents import ProcessDocumentsUseCase
from src.application.use_cases.query_resumes import QueryResumesUseCase
from src.application.use_cases.summarize_resumes import SummarizeResumesUseCase
from src.domain.entities.audit_log import AuditLog
from src.domain.entities.resume import ResumeDocument
from src.infrastructure.persistence.mongo_log_repository import MongoLogRepository
from src.presentation.api.schemas.response import (
    QueryResponse,
    ResumeSummary,
    SummaryResponse,
)

logger = logging.getLogger(__name__)


class AnalyzeResumesService:
    def __init__(
        self,
        *,
        process_use_case: ProcessDocumentsUseCase,
        summarize_use_case: SummarizeResumesUseCase,
        query_use_case: QueryResumesUseCase,
        log_repo: MongoLogRepository,
    ) -> None:
        self._process_use_case = process_use_case
        self._summarize_use_case = summarize_use_case
        self._query_use_case = query_use_case
        self._log_repo = log_repo

    async def execute(
        self,
        *,
        files: list[UploadFile],
        request_id: str,
        user_id: str,
        query: str | None,
    ) -> SummaryResponse | QueryResponse:
        logger.info(
            "resume_analysis_started",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "file_count": len(files),
                "has_query": query is not None,
            },
        )

        try:
            resumes = await self._process_use_case.execute(files)
            if not resumes:
                raise ValueError(
                    "No readable content could be extracted from the provided files."
                )

            timestamp = datetime.now(UTC)

            if query:
                return await self._run_query_flow(
                    request_id=request_id,
                    user_id=user_id,
                    query=query,
                    resumes=resumes,
                    timestamp=timestamp,
                )

            return await self._run_summary_flow(
                request_id=request_id,
                user_id=user_id,
                resumes=resumes,
                timestamp=timestamp,
            )
        except Exception:
            logger.exception(
                "resume_analysis_failed",
                extra={
                    "request_id": request_id,
                    "user_id": user_id,
                    "has_query": query is not None,
                },
            )
            raise

    async def _run_query_flow(
        self,
        *,
        request_id: str,
        user_id: str,
        query: str,
        resumes: list[ResumeDocument],
        timestamp: datetime,
    ) -> QueryResponse:
        result_text = await self._query_use_case.execute(resumes, query)
        result_payload: dict[str, Any] = {
            "mode": "query",
            "query": query,
            "total_documents": len(resumes),
            "result": result_text,
        }

        await self._log_repo.save(
            AuditLog(
                request_id=request_id,
                user_id=user_id,
                query=query,
                result=result_payload,
                timestamp=timestamp,
            )
        )

        logger.info(
            "resume_analysis_completed",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "mode": "query",
                "total_documents": len(resumes),
                "log": json.dumps(result_payload, ensure_ascii=False),
            },
        )

        return QueryResponse(
            request_id=request_id,
            user_id=user_id,
            timestamp=timestamp,
            query=query,
            total_documents=len(resumes),
            result=result_text,
        )

    async def _run_summary_flow(
        self,
        *,
        request_id: str,
        user_id: str,
        resumes: list[ResumeDocument],
        timestamp: datetime,
    ) -> SummaryResponse:
        summaries = await self._summarize_use_case.execute(resumes)
        result_payload: dict[str, Any] = {
            "mode": "summary",
            "total_documents": len(resumes),
            "results": summaries,
        }

        await self._log_repo.save(
            AuditLog(
                request_id=request_id,
                user_id=user_id,
                query=None,
                result=result_payload,
                timestamp=timestamp,
            )
        )

        logger.info(
            "resume_analysis_completed",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "mode": "summary",
                "total_documents": len(resumes),
                "log": json.dumps(result_payload, ensure_ascii=False),
            },
        )

        return SummaryResponse(
            request_id=request_id,
            user_id=user_id,
            timestamp=timestamp,
            total_documents=len(resumes),
            results=[ResumeSummary(**summary) for summary in summaries],
        )
