from io import BytesIO

import easyocr
import numpy as np
import pdfplumber
from PIL import Image
from starlette.concurrency import run_in_threadpool

from src.domain.entities.resume import ResumeDocument, SourceType
from src.domain.ports.ocr_port import OCRPort


class EasyOCRAdapter(OCRPort):
    def __init__(self) -> None:
        self._reader = easyocr.Reader(["pt", "en"], gpu=False, verbose=False)

    async def extract_from_pdf(
        self, file_bytes: bytes, filename: str
    ) -> ResumeDocument:
        texts: list[str] = []
        page_count = 0

        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                img = page.to_image(resolution=200).original
                text = await self._run_ocr(img)
                texts.append(text)

        return ResumeDocument(
            filename=filename,
            content="\n".join(texts).strip(),
            source_type=SourceType.OCR,
            page_count=page_count,
        )

    async def extract_from_image(
        self, file_bytes: bytes, filename: str
    ) -> ResumeDocument:
        image = Image.open(BytesIO(file_bytes)).convert("RGB")
        text = await self._run_ocr(image)

        return ResumeDocument(
            filename=filename,
            content=text,
            source_type=SourceType.OCR,
            page_count=1,
        )

    async def _run_ocr(self, image: Image.Image) -> str:
        img_array = np.array(image)
        results = await run_in_threadpool(
            self._reader.readtext, img_array, detail=0, paragraph=True
        )
        return "\n".join(results)
