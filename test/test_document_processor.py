from pathlib import Path

from app.processors.document_processor import (
    DocumentProcessor,
)


def test_document_processor_processes_pdf():
    pdf_path = Path(
        "test/fixtures/sample.pdf"
    )

    processor = DocumentProcessor()

    result = processor.process(
        pdf_path,
        task="Understand this document",
    )

    assert result.file_name == "sample.pdf"

    assert result.pages_processed > 0

    assert result.original_text

    assert result.optimized_text

    assert result.original_tokens >= 0

    assert result.optimized_tokens >= 0

    assert (
        result.optimized_tokens
        <= result.original_tokens
    )

    assert 0.0 <= (
        result.reduction_percentage
    ) <= 100.0

    assert (
        "PDF_TEXT_EXTRACTION"
        in result.processing_steps
    )