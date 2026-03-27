from datetime import datetime

from pydantic import BaseModel


class ResumeSummary(BaseModel):
    filename: str
    source_type: str
    page_count: int
    summary: str


class SummaryResponse(BaseModel):
    request_id: str
    user_id: str
    timestamp: datetime
    mode: str = "summary"
    total_documents: int
    results: list[ResumeSummary]


class QueryResponse(BaseModel):
    request_id: str
    user_id: str
    timestamp: datetime
    mode: str = "query"
    query: str
    total_documents: int
    result: str


class ErrorResponse(BaseModel):
    detail: str
