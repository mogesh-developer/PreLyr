from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.core.token_counter import TokenCounter
from app.processors.pdf_processor import PDFProcessor
from app.processors.document_repetition_optimizer import (
    DocumentRepetitionOptimizer,
)


@dataclass(frozen=True)
class DocumentProcessingResult:
    file_name: str
    original_text: str
    optimized_text: str

    original_tokens: int
    optimized_tokens: int
    reduction_percentage: float

    pages_processed: int
    processing_steps: list[str]


class DocumentProcessor:
    """
    Lightweight document input-preparation layer.

    Document
        ↓
    Extract
        ↓
    Basic cleanup
        ↓
    Document repetition optimization
        ↓
    Token measurement
        ↓
    Optimized context
    """

    def __init__(
        self,
        pdf_processor: PDFProcessor | None = None,
        repetition_optimizer: (
            DocumentRepetitionOptimizer | None
        ) = None,
        token_counter: TokenCounter | None = None,
    ) -> None:

        self.pdf_processor = (
            pdf_processor or PDFProcessor()
        )

        self.repetition_optimizer = (
            repetition_optimizer
            or DocumentRepetitionOptimizer()
        )

        self.token_counter = (
            token_counter or TokenCounter()
        )

    def process(
        self,
        file_path: str | Path,
        task: str | None = None,
    ) -> DocumentProcessingResult:

        document = self.pdf_processor.process(
            file_path
        )

        original_pages = [
            page.text
            for page in document.pages
        ]

        original_text = self._combine_pages(
            original_pages
        )

        cleaned_pages = [
            self._clean_text(page)
            for page in original_pages
        ]

        cleaned_text = self._combine_pages(
            cleaned_pages
        )

        processing_steps = [
            "PDF_TEXT_EXTRACTION"
        ]

        if cleaned_text != original_text:
            processing_steps.append(
                "BASIC_CLEANUP"
            )

        # --------------------------------------------
        # Document-level repetition optimization
        # --------------------------------------------

        repetition_result = (
            self.repetition_optimizer.optimize(
                cleaned_pages
            )
        )

        optimized_text = (
            repetition_result.optimized
        )

        if repetition_result.removed:
            processing_steps.append(
                "DOCUMENT_DEDUPLICATION"
            )
        else:
            processing_steps.append(
                "NO_OP"
            )

        original_tokens = self.token_counter.count(
            original_text
        )

        optimized_tokens = self.token_counter.count(
            optimized_text
        )

        reduction_percentage = (
            self.token_counter.reduction_percentage(
                original_text,
                optimized_text,
            )
        )

        return DocumentProcessingResult(
            file_name=document.file_name,
            original_text=original_text,
            optimized_text=optimized_text,
            original_tokens=original_tokens,
            optimized_tokens=optimized_tokens,
            reduction_percentage=reduction_percentage,
            pages_processed=document.page_count,
            processing_steps=processing_steps,
        )

    @staticmethod
    def _combine_pages(
        pages: list[str],
    ) -> str:

        return "\n\n".join(
            page.strip()
            for page in pages
            if page.strip()
        )

    @staticmethod
    def _clean_text(
        text: str,
    ) -> str:

        lines = [
            line.strip()
            for line in text.splitlines()
        ]

        cleaned_lines: list[str] = []

        previous_blank = False

        for line in lines:

            if not line:

                if not previous_blank:
                    cleaned_lines.append("")

                previous_blank = True
                continue

            cleaned_lines.append(line)
            previous_blank = False

        return "\n".join(
            cleaned_lines
        ).strip()