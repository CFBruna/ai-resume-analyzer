from dataclasses import dataclass
from enum import StrEnum


class SourceType(StrEnum):
    NATIVE_TEXT = "native_text"
    OCR = "ocr"


@dataclass
class ResumeDocument:
    filename: str
    content: str
    source_type: SourceType
    page_count: int
