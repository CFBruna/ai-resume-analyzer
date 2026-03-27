from src.domain.entities.resume import ResumeDocument, SourceType

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

    def test_analyze_returns_summary_when_no_query(
        self, client, mock_process_use_case, mock_summarize_use_case, mock_log_repo
    ):
        mock_process_use_case.execute.return_value = [
            ResumeDocument("cv.pdf", "content", SourceType.NATIVE_TEXT, 1)
        ]
        mock_summarize_use_case.execute.return_value = [
            {
                "filename": "cv.pdf",
                "source_type": "native_text",
                "page_count": 1,
                "summary": "Experienced Python developer.",
            }
        ]

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
        mock_log_repo.save.assert_called_once()

    def test_analyze_returns_query_result_when_query_provided(
        self, client, mock_process_use_case, mock_query_use_case, mock_log_repo
    ):
        mock_process_use_case.execute.return_value = [
            ResumeDocument("cv.pdf", "content", SourceType.NATIVE_TEXT, 1)
        ]
        mock_query_use_case.execute.return_value = (
            "cv.pdf — Strong Match. 5 years Python experience."
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
        mock_log_repo.save.assert_called_once()

    def test_returns_422_when_no_files_provided(self, client):
        response = client.post(
            "/api/v1/resumes/analyze",
            data=FORM_DATA,
            files=[],
        )
        assert response.status_code in (422, 400)

    def test_returns_415_for_unsupported_file_type(self, client, mock_process_use_case):
        mock_process_use_case.execute.return_value = [
            ResumeDocument("doc.docx", "content", SourceType.NATIVE_TEXT, 1)
        ]

        response = client.post(
            "/api/v1/resumes/analyze",
            data=FORM_DATA,
            files=[("files", ("doc.docx", b"fake", "application/vnd.openxmlformats"))],
        )
        assert response.status_code == 415

    def test_returns_413_when_file_exceeds_size_limit(self, client):
        oversized_content = b"x" * (5 * 1024 * 1024 + 1)

        response = client.post(
            "/api/v1/resumes/analyze",
            data=FORM_DATA,
            files=[("files", ("big.pdf", oversized_content, "application/pdf"))],
        )
        assert response.status_code == 413
