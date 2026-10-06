from pathlib import Path

from app.processors.pdf_heading_detector import (
    PDFHeadingDetector,
)
from app.processors.pdf_layout import PDFLayoutProcessor


def test_pdf_heading_detector_finds_large_headings():
    pdf_path = Path("test/fixtures/sample.pdf")

    layout_processor = PDFLayoutProcessor()
    blocks = layout_processor.process(pdf_path)

    detector = PDFHeadingDetector()

    headings = detector.detect(blocks)

    assert isinstance(headings, list)

    assert any(
        heading.text == "Get started"
        for heading in headings
    )