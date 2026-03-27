from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.presentation.api.app import app
from src.presentation.api.dependencies import (
    get_analyze_resumes_service,
    get_log_repository,
    get_process_documents_use_case,
    get_query_use_case,
    get_summarize_use_case,
)


@pytest.fixture
def mock_process_use_case() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_summarize_use_case() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_query_use_case() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_log_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_analyze_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def client(
    mock_process_use_case: AsyncMock,
    mock_summarize_use_case: AsyncMock,
    mock_query_use_case: AsyncMock,
    mock_log_repo: AsyncMock,
    mock_analyze_service: AsyncMock,
):
    app.dependency_overrides[get_process_documents_use_case] = lambda: (
        mock_process_use_case
    )
    app.dependency_overrides[get_summarize_use_case] = lambda: mock_summarize_use_case
    app.dependency_overrides[get_query_use_case] = lambda: mock_query_use_case
    app.dependency_overrides[get_log_repository] = lambda: mock_log_repo
    app.dependency_overrides[get_analyze_resumes_service] = lambda: mock_analyze_service
    yield TestClient(app)
    app.dependency_overrides.clear()
