from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    request_id: str = Field(
        description="Unique identifier for this request (UUID recommended)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    user_id: str = Field(
        description="Identifier of the user making the request",
        examples=["recruiter@company.com"],
    )
    query: str | None = Field(
        default=None,
        description=(
            "Optional recruitment query. If omitted, returns individual summaries. "
            "Example: 'Which candidate is best suited for a Senior Python Engineer role?'"
        ),
        examples=[
            "Which candidate has the most experience with Python and cloud infrastructure?"
        ],
    )
