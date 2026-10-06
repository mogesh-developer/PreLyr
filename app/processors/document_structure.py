from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DocumentSection:
    title: str
    level: int
    content: list[str] = field(default_factory=list)
    children: list["DocumentSection"] = field(
        default_factory=list
    )


@dataclass
class StructuredDocument:
    sections: list[DocumentSection]


class DocumentStructureProcessor:
    """
    Conservative document structure detector.

    Converts extracted text into a basic hierarchical
    section structure.

    Uncertain text is preserved as content.
    """

    def process(
        self,
        pages: list[str],
    ) -> StructuredDocument:

        sections: list[DocumentSection] = []
        stack: list[DocumentSection] = []

        for page_text in pages:
            lines = page_text.splitlines()

            for raw_line in lines:
                line = raw_line.strip()

                if not line:
                    continue

                heading_level = self._detect_heading_level(
                    line
                )

                if heading_level is None:
                    if stack:
                        stack[-1].content.append(line)
                    elif sections and sections[-1].level == 0:
                        sections[-1].content.append(line)
                    else:
                        sections.append(
                            DocumentSection(
                                title="Document Content",
                                level=0,
                                content=[line],
                            )
                        )
                    continue

                section = DocumentSection(
                    title=line,
                    level=heading_level,
                )

                while (
                    stack
                    and stack[-1].level
                    >= heading_level
                ):
                    stack.pop()

                if stack:
                    stack[-1].children.append(section)
                else:
                    sections.append(section)

                stack.append(section)

        return StructuredDocument(
            sections=sections
        )

    def _detect_heading_level(
        self,
        line: str,
    ) -> int | None:

        if line.startswith("### "):
            return 3

        if line.startswith("## "):
            return 2

        if line.startswith("# "):
            return 1

        return None