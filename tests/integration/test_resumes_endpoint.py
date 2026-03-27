from src.presentation.api.schemas.response import (
    QueryResponse,
    ResumeSummary,
    SummaryResponse,
)

FAKE_PDF = b"%PDF-1.4 fake content"
FORM_DATA = {
    "request_id": "test-request-001",
    "user_id": "recruiter@company.com",
}


class TestResumesEndpoint:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_analyze_returns_summary_when_no_query(self, client, mock_analyze_service):
        mock_analyze_service.execute.return_value = SummaryResponse(
            request_id="test-request-001",
            user_id="recruiter@company.com",
            timestamp="2026-03-27T00:00:00Z",
            total_documents=1,
            results=[
                ResumeSummary(
                    filename="cv.pdf",
                    source_type="native_text",
                    page_count=1,
                    summary="Experienced Python developer.",
                )
            ],
        )

        response = client.post(
            "/api/v1/resumes/analyze",
            data=FORM_DATA,
            files=[("files", ("cv.pdf", FAKE_PDF, "application/pdf"))],
        )

        assert response.status_code == 200
        body = response.json()
        assert body["mode"] == "summary"
        assert body["total_documents"] == 1
        assert len(body["results"]) == 1
        mock_analyze_service.execute.assert_awaited_once()

    def test_analyze_returns_query_result_when_query_provided(
        self, client, mock_analyze_service
    ):
        mock_analyze_service.execute.return_value = QueryResponse(
            request_id="test-request-001",
            user_id="recruiter@company.com",
            timestamp="2026-03-27T00:00:00Z",
            query="Who has the most Python experience?",
            total_documents=1,
            result="cv.pdf — Strong Match. 5 years Python experience.",
        )

        response = client.post(
            "/api/v1/resumes/analyze",
            data={**FORM_DATA, "query": "Who has the most Python experience?"},
            files=[("files", ("cv.pdf", FAKE_PDF, "application/pdf"))],
        )

        assert response.status_code == 200
        body = response.json()
        assert body["mode"] == "query"
        assert "result" in body
        mock_analyze_service.execute.assert_awaited_once()

    def test_returns_422_when_no_files_provided(self, client):
        response = client.post(
            "/api/v1/resumes/analyze",
            data=FORM_DATA,
            files=[],
        )
        assert response.status_code in (422, 400)

    def test_returns_415_for_unsupported_file_type(self, client, mock_analyze_service):
        response = client.post(
            "/api/v1/resumes/analyze",
            data=FORM_DATA,
            files=[("files", ("doc.docx", b"fake", "application/vnd.openxmlformats"))],
        )
        assert response.status_code == 415
        mock_analyze_service.execute.assert_not_called()

    def test_returns_413_when_file_exceeds_size_limit(
        self, client, mock_analyze_service
    ):
        oversized_content = b"x" * (5 * 1024 * 1024 + 1)

        response = client.post(
            "/api/v1/resumes/analyze",
            data=FORM_DATA,
            files=[("files", ("big.pdf", oversized_content, "application/pdf"))],
        )
        assert response.status_code == 413
        mock_analyze_service.execute.assert_not_called()
