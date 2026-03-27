from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class AuditLog:
    request_id: str
    user_id: str
    query: str | None
    result: dict
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
