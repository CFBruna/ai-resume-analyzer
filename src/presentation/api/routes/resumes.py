from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from src.presentation.api.dependencies import (
    get_analyze_resumes_service,
)
from src.presentation.api.schemas.response import QueryResponse, SummaryResponse
from src.presentation.api.services.analyze_resumes import AnalyzeResumesService

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
    service: Annotated[AnalyzeResumesService, Depends(get_analyze_resumes_service)],
    query: Annotated[
        str | None,
        Form(
            description="Optional recruitment query. Omit to receive individual summaries."
        ),
    ] = None,
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

    try:
        return await service.execute(
            files=files,
            request_id=request_id,
            user_id=user_id,
            query=query,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
