from datetime import UTC, datetime

import pytest

from src.domain.entities.audit_log import AuditLog
from src.infrastructure.persistence.mongo_log_repository import MongoLogRepository


class FakeCollection:
    def __init__(self) -> None:
        self.inserted: list[dict] = []
        self.docs: dict[str, dict] = {}

    async def insert_one(self, payload: dict) -> None:
        self.inserted.append(payload)
        self.docs[payload["request_id"]] = payload

    async def find_one(self, query: dict) -> dict | None:
        return self.docs.get(query["request_id"])


class FakeDB:
    def __init__(self) -> None:
        self.collection = FakeCollection()

    def __getitem__(self, name: str) -> FakeCollection:
        assert name == "audit_logs"
        return self.collection


@pytest.mark.asyncio
class TestMongoLogRepository:
    async def test_save_persists_audit_log(self) -> None:
        db = FakeDB()
        repo = MongoLogRepository(db)
        log = AuditLog(
            request_id="req-1",
            user_id="user@example.com",
            query=None,
            result={"mode": "summary"},
            timestamp=datetime.now(UTC),
        )

        await repo.save(log)

        assert db.collection.inserted[0]["request_id"] == "req-1"

    async def test_find_by_request_id_returns_log(self) -> None:
        db = FakeDB()
        repo = MongoLogRepository(db)
        timestamp = datetime.now(UTC)
        db.collection.docs["req-1"] = {
            "request_id": "req-1",
            "user_id": "user@example.com",
            "query": "question",
            "result": {"mode": "query"},
            "timestamp": timestamp,
        }

        result = await repo.find_by_request_id("req-1")

        assert result is not None
        assert result.request_id == "req-1"
        assert result.timestamp == timestamp
