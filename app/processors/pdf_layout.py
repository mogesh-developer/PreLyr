from __future__ import annotations

from pathlib import Path

from pdfminer.high_level import extract_pages
from pdfminer.layout import (
    LTTextContainer,
    LTChar,
)


class PDFLayoutProcessor:
    """
    Extract PDF text together with basic layout/font information.

    Responsibility:
        PDF -> text blocks + font metadata

    This is an inspection layer.
    It does not decide whether text is useful or removable.
    """

    def process(self, file_path: str | Path) -> list[dict]:
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

        blocks: list[dict] = []

        for page_number, layout in enumerate(
            extract_pages(str(path)),
            start=1,
        ):
            for element in layout:

                if not isinstance(
                    element,
                    LTTextContainer,
                ):
                    continue

                text = element.get_text().strip()

                if not text:
                    continue

                font_sizes: list[float] = []
                font_names: list[str] = []

                for line in element:
                    for character in line:

                        if not isinstance(
                            character,
                            LTChar,
                        ):
                            continue

                        font_sizes.append(
                            character.size
                        )

                        font_names.append(
                            character.fontname
                        )

                blocks.append(
                    {
                        "page": page_number,
                        "text": text,
                        "x0": element.x0,
                        "y0": element.y0,
                        "x1": element.x1,
                        "y1": element.y1,
                        "font_size": (
                            max(font_sizes)
                            if font_sizes
                            else None
                        ),
                        "font_name": (
                            font_names[0]
                            if font_names
                            else None
                        ),
                    }
                )

        return blocks