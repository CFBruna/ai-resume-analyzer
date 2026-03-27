from motor.motor_asyncio import AsyncIOMotorDatabase

from src.domain.entities.audit_log import AuditLog
from src.domain.ports.log_repository_port import LogRepositoryPort


class MongoLogRepository(LogRepositoryPort):
    COLLECTION = "audit_logs"

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db[self.COLLECTION]

    async def save(self, log: AuditLog) -> None:
        await self._collection.insert_one(
            {
                "request_id": log.request_id,
                "user_id": log.user_id,
                "query": log.query,
                "result": log.result,
                "timestamp": log.timestamp,
            }
        )

    async def find_by_request_id(self, request_id: str) -> AuditLog | None:
        doc = await self._collection.find_one({"request_id": request_id})
        if not doc:
            return None
        return AuditLog(
            request_id=doc["request_id"],
            user_id=doc["user_id"],
            query=doc["query"],
            result=doc["result"],
            timestamp=doc["timestamp"],
        )
