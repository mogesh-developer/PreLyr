from pathlib import Path

from app.processors.pdf_layout import PDFLayoutProcessor


def test_pdf_layout_processor_reads_pdf():
    pdf_path = Path("test/fixtures/sample.pdf")

    processor = PDFLayoutProcessor()

    blocks = processor.process(pdf_path)

    assert isinstance(blocks, list)