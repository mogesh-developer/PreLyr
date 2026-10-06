from pathlib import Path

import pytest
from pypdf import PdfWriter

from app.processors.pdf_processor import (
    PDFProcessor,
)


def create_pdf(
    path: Path,
    pages: list[str],
) -> None:
    writer = PdfWriter()

    for text in pages:
        writer.add_blank_page(
            width=595,
            height=842,
        )

    with path.open("wb") as file:
        writer.write(file)


def test_pdf_processor_reads_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"

    create_pdf(
        pdf_path,
        ["Page one"],
    )

    processor = PDFProcessor()

    document = processor.process(pdf_path)

    assert document.file_name == "sample.pdf"
    assert document.page_count == 1
    assert len(document.pages) == 1
    assert document.pages[0].page_number == 1


def test_pdf_processor_preserves_page_count(tmp_path):
    pdf_path = tmp_path / "multi_page.pdf"

    create_pdf(
        pdf_path,
        [
            "Page one",
            "Page two",
            "Page three",
        ],
    )

    processor = PDFProcessor()

    document = processor.process(pdf_path)

    assert document.page_count == 3
    assert len(document.pages) == 3

    assert [
        page.page_number
        for page in document.pages
    ] == [1, 2, 3]


def test_pdf_processor_preserves_page_order(tmp_path):
    pdf_path = tmp_path / "ordered.pdf"

    create_pdf(
        pdf_path,
        [
            "First",
            "Second",
            "Third",
        ],
    )

    processor = PDFProcessor()

    document = processor.process(pdf_path)

    assert [
        page.page_number
        for page in document.pages
    ] == [1, 2, 3]


def test_pdf_processor_rejects_missing_file(tmp_path):
    pdf_path = tmp_path / "missing.pdf"

    processor = PDFProcessor()

    with pytest.raises(FileNotFoundError):
        processor.process(pdf_path)


def test_pdf_processor_rejects_non_pdf(tmp_path):
    file_path = tmp_path / "document.txt"
    file_path.write_text("hello")

    processor = PDFProcessor()

    with pytest.raises(ValueError):
        processor.process(file_path)


def test_pdf_processor_rejects_directory(tmp_path):
    directory = tmp_path / "documents"
    directory.mkdir()

    processor = PDFProcessor()

    with pytest.raises(ValueError):
        processor.process(directory)


def test_pdf_processor_rejects_invalid_pdf(tmp_path):
    pdf_path = tmp_path / "invalid.pdf"
    pdf_path.write_text("This is not a PDF.")

    processor = PDFProcessor()

    with pytest.raises(ValueError):
        processor.process(pdf_path)

def test_pdf_processor_extracts_text():
    pdf_path = Path("test/fixtures/sample.pdf")

    processor = PDFProcessor()

    document = processor.process(pdf_path)

    assert document.page_count > 0

    extracted_text = "\n".join(
        page.text
        for page in document.pages
    )

    assert extracted_text.strip()