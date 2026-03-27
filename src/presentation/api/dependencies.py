from functools import lru_cache
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient

from src.application.use_cases.process_documents import ProcessDocumentsUseCase
from src.application.use_cases.query_resumes import QueryResumesUseCase
from src.application.use_cases.summarize_resumes import SummarizeResumesUseCase
from src.infrastructure.llm.llm_factory import get_llm_adapter
from src.infrastructure.ocr.easyocr_adapter import EasyOCRAdapter
from src.infrastructure.persistence.mongo_log_repository import MongoLogRepository
from src.presentation.api.config import get_settings
from src.presentation.api.services.analyze_resumes import AnalyzeResumesService


@lru_cache
def get_ocr_adapter() -> EasyOCRAdapter:
    return EasyOCRAdapter()


def get_db() -> Any:
    settings = get_settings()
    client: Any = AsyncIOMotorClient(settings.MONGODB_URI)
    return client[settings.MONGODB_DATABASE]


def get_process_documents_use_case() -> ProcessDocumentsUseCase:
    return ProcessDocumentsUseCase(ocr_adapter=get_ocr_adapter())


def get_summarize_use_case() -> SummarizeResumesUseCase:
    settings = get_settings()
    llm = get_llm_adapter(settings)
    return SummarizeResumesUseCase(llm=llm)


def get_query_use_case() -> QueryResumesUseCase:
    settings = get_settings()
    llm = get_llm_adapter(settings)
    return QueryResumesUseCase(llm=llm)


def get_log_repository() -> MongoLogRepository:
    return MongoLogRepository(db=get_db())


def get_analyze_resumes_service() -> AnalyzeResumesService:
    return AnalyzeResumesService(
        process_use_case=get_process_documents_use_case(),
        summarize_use_case=get_summarize_use_case(),
        query_use_case=get_query_use_case(),
        log_repo=get_log_repository(),
    )
