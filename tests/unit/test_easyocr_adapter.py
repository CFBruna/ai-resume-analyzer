from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image

from src.domain.entities.resume import SourceType
from src.infrastructure.ocr.easyocr_adapter import EasyOCRAdapter


@pytest.mark.asyncio
class TestEasyOCRAdapter:
    async def test_extract_from_image_uses_ocr(self) -> None:
        fake_reader = MagicMock()
        fake_reader.readtext.return_value = ["line 1", "line 2"]

        with patch("easyocr.Reader", return_value=fake_reader):
            adapter = EasyOCRAdapter()
            with patch.object(
                adapter, "_run_ocr", new=AsyncMock(return_value="ocr text")
            ):
                image = Image.new("RGB", (10, 10), color="white")
                with patch("PIL.Image.open", return_value=image):
                    result = await adapter.extract_from_image(
                        b"image-bytes", "resume.jpg"
                    )

        assert result.filename == "resume.jpg"
        assert result.content == "ocr text"
        assert result.source_type == SourceType.OCR
        assert result.page_count == 1

    async def test_run_ocr_joins_lines(self) -> None:
        fake_reader = MagicMock()
        fake_reader.readtext.return_value = ["foo", "bar"]

        with patch("easyocr.Reader", return_value=fake_reader):
            adapter = EasyOCRAdapter()
            with patch(
                "src.infrastructure.ocr.easyocr_adapter.run_in_threadpool",
                new=AsyncMock(return_value=["foo", "bar"]),
            ):
                image = Image.new("RGB", (10, 10), color="white")
                result = await adapter._run_ocr(image)

        assert result == "foo\nbar"
