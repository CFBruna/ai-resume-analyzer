from abc import ABC, abstractmethod

from src.domain.entities.audit_log import AuditLog


class LogRepositoryPort(ABC):
    @abstractmethod
    async def save(self, log: AuditLog) -> None: ...

    @abstractmethod
    async def find_by_request_id(self, request_id: str) -> AuditLog | None: ...
