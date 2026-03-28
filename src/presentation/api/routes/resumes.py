from typing import Annotated, Any
from uuid import UUID

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

OPENAPI_EXAMPLES: dict[str, dict[str, Any]] = {
    "summary_mode": {
        "summary": "Summarize multiple resumes",
        "value": {
            "request_id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "recruiter@company.com",
            "query": None,
            "files": ["resume_a.pdf", "resume_b.png"],
        },
    },
    "query_mode": {
        "summary": "Compare candidates for a role",
        "value": {
            "request_id": "550e8400-e29b-41d4-a716-446655440001",
            "user_id": "recruiter@company.com",
            "query": "Which candidate is a better fit for a Senior Python Engineer role with AWS and MongoDB experience?",
            "files": ["resume_a.pdf", "resume_b.png"],
        },
    },
}

OPENAPI_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": "Successful analysis in summary or query mode.",
        "content": {
            "application/json": {
                "examples": {
                    "summary_response": {
                        "summary": "Summary mode response",
                        "value": {
                            "request_id": "550e8400-e29b-41d4-a716-446655440000",
                            "user_id": "recruiter@company.com",
                            "timestamp": "2026-03-27T20:06:58.504043Z",
                            "mode": "summary",
                            "total_documents": 2,
                            "results": [
                                {
                                    "filename": "resume_a.pdf",
                                    "source_type": "native_text",
                                    "page_count": 2,
                                    "summary": "Experienced Python developer with cloud background.",
                                }
                            ],
                        },
                    },
                    "query_response": {
                        "summary": "Query mode response",
                        "value": {
                            "request_id": "550e8400-e29b-41d4-a716-446655440001",
                            "user_id": "recruiter@company.com",
                            "timestamp": "2026-03-27T20:07:24.456703Z",
                            "mode": "query",
                            "query": "Which candidate is a better fit for a Senior Python Engineer role with AWS and MongoDB experience?",
                            "total_documents": 2,
                            "result": "Candidate A is the stronger match because...",
                        },
                    },
                }
            }
        },
    }
}

OPENAPI_REQUEST_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["files", "request_id", "user_id"],
    "properties": {
        "files": {
            "type": "array",
            "items": {"type": "string", "format": "binary"},
            "description": "One or more resume files (PDF, JPEG, PNG). Max 10 files, 5MB each.",
        },
        "request_id": {
            "type": "string",
            "description": "Unique request identifier (UUID)",
        },
        "user_id": {
            "type": "string",
            "description": "Requester identifier",
        },
        "query": {
            "type": ["string", "null"],
            "description": (
                "Optional recruitment question. Leave empty to switch the endpoint to summary mode; "
                "fill it to receive a comparative analysis across the uploaded resumes."
            ),
        },
    },
}


@router.post(
    "/analyze",
    response_model=SummaryResponse | QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze resumes — summarize or query",
    description=(
        "Upload multiple PDF or image files (max 10 files, 5MB each). "
        "Use summary mode by omitting `query` to receive one summary per document. "
        "Use query mode by providing `query` to get a comparative analysis with evidence-based justification."
    ),
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "schema": OPENAPI_REQUEST_SCHEMA,
                    "examples": OPENAPI_EXAMPLES,
                }
            }
        }
    },
    responses=OPENAPI_RESPONSES,
)
async def analyze_resumes(
    files: Annotated[
        list[UploadFile],
        File(
            description="One or more resume files (PDF, JPEG, PNG). Max 10 files, 5MB each."
        ),
    ],
    request_id: Annotated[UUID, Form(description="Unique request identifier (UUID)")],
    user_id: Annotated[str, Form(description="Requester identifier")],
    service: Annotated[AnalyzeResumesService, Depends(get_analyze_resumes_service)],
    query: Annotated[
        str | None,
        Form(
            description=(
                "Optional recruitment question. Leave empty to switch the endpoint to summary mode; "
                "fill it to receive a comparative analysis across the uploaded resumes."
            )
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
            request_id=str(request_id),
            user_id=user_id,
            query=query,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
