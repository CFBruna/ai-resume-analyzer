from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from src.application.use_cases.process_documents import ProcessDocumentsUseCase
from src.application.use_cases.query_resumes import QueryResumesUseCase
from src.application.use_cases.summarize_resumes import SummarizeResumesUseCase
from src.domain.entities.audit_log import AuditLog
from src.infrastructure.persistence.mongo_log_repository import MongoLogRepository
from src.presentation.api.dependencies import (
    get_log_repository,
    get_process_documents_use_case,
    get_query_use_case,
    get_summarize_use_case,
)
from src.presentation.api.schemas.response import (
    QueryResponse,
    ResumeSummary,
    SummaryResponse,
)

router = APIRouter(prefix="/api/v1/resumes", tags=["resumes"])

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
}

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024


@router.post(
    "/analyze",
    response_model=SummaryResponse | QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze resumes — summarize or query",
    description=(
        "Upload multiple PDF or image files (max 10 files, 5MB each). "
        "If `query` is provided, returns a comparative analysis. "
        "If `query` is omitted, returns individual summaries for each document."
    ),
)
async def analyze_resumes(
    files: Annotated[
        list[UploadFile],
        File(
            description="One or more resume files (PDF, JPEG, PNG). Max 10 files, 5MB each."
        ),
    ],
    request_id: Annotated[str, Form(description="Unique request identifier (UUID)")],
    user_id: Annotated[str, Form(description="Requester identifier")],
    query: Annotated[
        str | None,
        Form(
            description="Optional recruitment query. Omit to receive individual summaries."
        ),
    ] = None,
    *,
    process_use_case: Annotated[
        ProcessDocumentsUseCase, Depends(get_process_documents_use_case)
    ],
    summarize_use_case: Annotated[
        SummarizeResumesUseCase, Depends(get_summarize_use_case)
    ],
    query_use_case: Annotated[QueryResumesUseCase, Depends(get_query_use_case)],
    log_repo: Annotated[MongoLogRepository, Depends(get_log_repository)],
) -> SummaryResponse | QueryResponse:
    if not files:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one file is required.",
        )

    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Maximum of 10 files per request.",
        )

    for file in files:
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type: {file.content_type}. Allowed: PDF, JPEG, PNG.",
            )

        file_bytes = await file.read()
        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=f"{file.filename} exceeds the 5MB size limit.",
            )
        await file.seek(0)

    resumes = await process_use_case.execute(files)

    if not resumes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No readable content could be extracted from the provided files.",
        )

    timestamp = datetime.now(UTC)

    if query:
        result_text = await query_use_case.execute(resumes, query)

        result_payload: dict = {
            "mode": "query",
            "query": query,
            "total_documents": len(resumes),
            "result": result_text,
        }

        await log_repo.save(
            AuditLog(
                request_id=request_id,
                user_id=user_id,
                query=query,
                result=result_payload,
                timestamp=timestamp,
            )
        )

        return QueryResponse(
            request_id=request_id,
            user_id=user_id,
            timestamp=timestamp,
            query=query,
            total_documents=len(resumes),
            result=result_text,
        )

    summaries = await summarize_use_case.execute(resumes)

    result_payload = {
        "mode": "summary",
        "total_documents": len(resumes),
        "results": summaries,
    }

    await log_repo.save(
        AuditLog(
            request_id=request_id,
            user_id=user_id,
            query=None,
            result=result_payload,
            timestamp=timestamp,
        )
    )

    return SummaryResponse(
        request_id=request_id,
        user_id=user_id,
        timestamp=timestamp,
        total_documents=len(resumes),
        results=[ResumeSummary(**s) for s in summaries],
    )
