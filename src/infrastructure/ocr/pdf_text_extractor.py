from io import BytesIO

import pdfplumber

from src.domain.entities.resume import ResumeDocument, SourceType


class PDFTextExtractor:
    MIN_CHARS_PER_PAGE = 50

    def extract(self, file_bytes: bytes, filename: str) -> ResumeDocument | None:
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            pages = pdf.pages
            page_count = len(pages)
            texts = [page.extract_text() or "" for page in pages]
            full_text = "\n".join(texts).strip()

        if len(full_text) < self.MIN_CHARS_PER_PAGE * page_count:
            return None

        return ResumeDocument(
            filename=filename,
            content=full_text,
            source_type=SourceType.NATIVE_TEXT,
            page_count=page_count,
        )
