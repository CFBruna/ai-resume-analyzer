from unittest.mock import MagicMock, patch

from src.domain.entities.resume import SourceType
from src.infrastructure.ocr.pdf_text_extractor import PDFTextExtractor


class TestPDFTextExtractor:
    def test_returns_document_when_text_is_sufficient(self) -> None:
        extractor = PDFTextExtractor()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "A" * 200

        with patch("pdfplumber.open") as mock_open:
            mock_open.return_value.__enter__.return_value.pages = [mock_page]
            result = extractor.extract(b"fake-pdf", "resume.pdf")

        assert result is not None
        assert result.source_type == SourceType.NATIVE_TEXT
        assert result.filename == "resume.pdf"

    def test_returns_none_when_text_is_insufficient(self) -> None:
        extractor = PDFTextExtractor()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "short"

        with patch("pdfplumber.open") as mock_open:
            mock_open.return_value.__enter__.return_value.pages = [mock_page]
            result = extractor.extract(b"fake-pdf", "resume.pdf")

        assert result is None

    def test_returns_none_when_text_is_none(self) -> None:
        extractor = PDFTextExtractor()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = None

        with patch("pdfplumber.open") as mock_open:
            mock_open.return_value.__enter__.return_value.pages = [mock_page]
            result = extractor.extract(b"fake-pdf", "resume.pdf")

        assert result is None
