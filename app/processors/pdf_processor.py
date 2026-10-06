from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class PDFPage:
    page_number: int
    text: str


@dataclass(frozen=True)
class PDFDocument:
    file_name: str
    page_count: int
    pages: list[PDFPage]


class PDFProcessor:
    """
    Lightweight PDF text extractor for PreLyr.

    Responsibility:
        PDF -> structured page-level text

    This processor does not:
        - optimize text
        - summarize content
        - perform OCR
        - call an LLM
    """

    def process(self, file_path: str | Path) -> PDFDocument:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Path is not a file: {path}"
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Expected a PDF file, got: {path.suffix}"
            )

        try:
            reader = PdfReader(str(path))
        except Exception as exc:
            raise ValueError(
                f"Unable to read PDF: {path.name}"
            ) from exc

        pages: list[PDFPage] = []

        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            pages.append(
                PDFPage(
                    page_number=index,
                    text=text,
                )
            )

        return PDFDocument(
            file_name=path.name,
            page_count=len(pages),
            pages=pages,
        )