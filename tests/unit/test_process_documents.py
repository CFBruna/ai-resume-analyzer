from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import UploadFile

from src.application.use_cases.process_documents import ProcessDocumentsUseCase
from src.domain.entities.resume import ResumeDocument, SourceType


def make_upload_file(
    filename: str, content_type: str, content: bytes = b"data"
) -> UploadFile:
    mock = MagicMock(spec=UploadFile)
    mock.filename = filename
    mock.content_type = content_type
    mock.read = AsyncMock(return_value=content)
    return mock


@pytest.mark.asyncio
class TestProcessDocumentsUseCase:
    async def test_uses_native_text_when_available(self) -> None:
        mock_ocr = AsyncMock()
        use_case = ProcessDocumentsUseCase(ocr_adapter=mock_ocr)
        native_doc = ResumeDocument("cv.pdf", "content", SourceType.NATIVE_TEXT, 1)

        with patch.object(use_case._pdf_extractor, "extract", return_value=native_doc):
            files = [make_upload_file("cv.pdf", "application/pdf")]
            result = await use_case.execute(files)

        assert len(result) == 1
        assert result[0].source_type == SourceType.NATIVE_TEXT
        mock_ocr.extract_from_pdf.assert_not_called()

    async def test_falls_back_to_ocr_when_native_extraction_fails(self) -> None:
        ocr_doc = ResumeDocument("cv.pdf", "ocr content", SourceType.OCR, 1)
        mock_ocr = AsyncMock()
        mock_ocr.extract_from_pdf = AsyncMock(return_value=ocr_doc)
        use_case = ProcessDocumentsUseCase(ocr_adapter=mock_ocr)

        with patch.object(use_case._pdf_extractor, "extract", return_value=None):
            files = [make_upload_file("cv.pdf", "application/pdf")]
            result = await use_case.execute(files)

        assert len(result) == 1
        assert result[0].source_type == SourceType.OCR

    async def test_processes_image_files(self) -> None:
        img_doc = ResumeDocument("cv.jpg", "image content", SourceType.OCR, 1)
        mock_ocr = AsyncMock()
        mock_ocr.extract_from_image = AsyncMock(return_value=img_doc)
        use_case = ProcessDocumentsUseCase(ocr_adapter=mock_ocr)

        files = [make_upload_file("cv.jpg", "image/jpeg")]
        result = await use_case.execute(files)

        assert len(result) == 1
        mock_ocr.extract_from_image.assert_called_once()

    async def test_skips_unsupported_mime_type(self) -> None:
        mock_ocr = AsyncMock()
        use_case = ProcessDocumentsUseCase(ocr_adapter=mock_ocr)

        files = [make_upload_file("doc.docx", "application/vnd.openxmlformats")]
        result = await use_case.execute(files)

        assert result == []
