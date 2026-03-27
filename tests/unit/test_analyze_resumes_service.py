from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import UploadFile

from src.domain.entities.resume import ResumeDocument, SourceType
from src.presentation.api.services.analyze_resumes import AnalyzeResumesService


def make_upload_file(
    filename: str, content_type: str, content: bytes = b"data"
) -> UploadFile:
    mock = MagicMock(spec=UploadFile)
    mock.filename = filename
    mock.content_type = content_type
    mock.read = AsyncMock(return_value=content)
    mock.seek = AsyncMock()
    return mock


@pytest.mark.asyncio
class TestAnalyzeResumesService:
    async def test_summary_flow_persists_audit_log(self) -> None:
        process_use_case = AsyncMock()
        process_use_case.execute = AsyncMock(
            return_value=[
                ResumeDocument("cv.pdf", "content", SourceType.NATIVE_TEXT, 1)
            ]
        )
        summarize_use_case = AsyncMock()
        summarize_use_case.execute = AsyncMock(
            return_value=[
                {
                    "filename": "cv.pdf",
                    "source_type": "native_text",
                    "page_count": 1,
                    "summary": "summary",
                }
            ]
        )
        query_use_case = AsyncMock()
        log_repo = AsyncMock()
        log_repo.save = AsyncMock()

        service = AnalyzeResumesService(
            process_use_case=process_use_case,
            summarize_use_case=summarize_use_case,
            query_use_case=query_use_case,
            log_repo=log_repo,
        )

        result = await service.execute(
            files=[make_upload_file("cv.pdf", "application/pdf")],
            request_id="req-1",
            user_id="user@example.com",
            query=None,
        )

        assert result.mode == "summary"
        log_repo.save.assert_awaited_once()

    async def test_query_flow_persists_audit_log(self) -> None:
        process_use_case = AsyncMock()
        process_use_case.execute = AsyncMock(
            return_value=[
                ResumeDocument("cv.pdf", "content", SourceType.NATIVE_TEXT, 1)
            ]
        )
        summarize_use_case = AsyncMock()
        query_use_case = AsyncMock()
        query_use_case.execute = AsyncMock(return_value="analysis")
        log_repo = AsyncMock()
        log_repo.save = AsyncMock()

        service = AnalyzeResumesService(
            process_use_case=process_use_case,
            summarize_use_case=summarize_use_case,
            query_use_case=query_use_case,
            log_repo=log_repo,
        )

        result = await service.execute(
            files=[make_upload_file("cv.pdf", "application/pdf")],
            request_id="req-1",
            user_id="user@example.com",
            query="best candidate?",
        )

        assert result.mode == "query"
        log_repo.save.assert_awaited_once()
