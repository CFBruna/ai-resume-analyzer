from fastapi import UploadFile

from src.domain.entities.resume import ResumeDocument
from src.domain.ports.ocr_port import OCRPort
from src.infrastructure.ocr.pdf_text_extractor import PDFTextExtractor

PDF_MIME = "application/pdf"
IMAGE_MIMES = {"image/jpeg", "image/png", "image/jpg"}


class ProcessDocumentsUseCase:
    def __init__(self, ocr_adapter: OCRPort) -> None:
        self._pdf_extractor = PDFTextExtractor()
        self._ocr_adapter = ocr_adapter

    async def execute(self, files: list[UploadFile]) -> list[ResumeDocument]:
        results: list[ResumeDocument] = []

        for file in files:
            content_type = file.content_type or ""
            file_bytes = await file.read()
            filename = file.filename or "unknown"

            if content_type == PDF_MIME:
                doc = self._pdf_extractor.extract(file_bytes, filename)
                if doc is None:
                    doc = await self._ocr_adapter.extract_from_pdf(file_bytes, filename)
            elif content_type in IMAGE_MIMES:
                doc = await self._ocr_adapter.extract_from_image(file_bytes, filename)
            else:
                continue

            if doc.content.strip():
                results.append(doc)

        return results
