from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class RepetitionCandidate:
    text: str
    pages: tuple[int, ...]
    occurrences: int
    reason: str
    confidence: float


class DocumentRepetitionDetector:
    """
    Conservative document-level repetition detector.

    Detects repeated lines across different pages.

    This class only identifies candidates.
    It does NOT remove anything.

    Lossless-by-default:
        - no text is deleted
        - unique content is preserved
        - repeated content becomes a candidate
        - page information is preserved
    """

    def detect(
        self,
        pages: list[str],
    ) -> list[RepetitionCandidate]:

        occurrences: dict[str, list[int]] = defaultdict(list)

        for page_number, page_text in enumerate(
            pages,
            start=1,
        ):
            seen_on_page: set[str] = set()

            for raw_line in page_text.splitlines():

                line = self._normalize_line(raw_line)

                if not line:
                    continue

                # Count a line only once per page.
                if line in seen_on_page:
                    continue

                seen_on_page.add(line)

                occurrences[line].append(
                    page_number
                )

        candidates: list[RepetitionCandidate] = []

        total_pages = len(pages)

        for text, page_numbers in occurrences.items():

            page_count = len(page_numbers)

            # A line must occur on at least 2 pages.
            if page_count < 2:
                continue

            confidence, reason = self._classify(
                text=text,
                page_count=page_count,
                total_pages=total_pages,
            )

            if confidence <= 0:
                continue

            candidates.append(
                RepetitionCandidate(
                    text=text,
                    pages=tuple(page_numbers),
                    occurrences=page_count,
                    reason=reason,
                    confidence=confidence,
                )
            )

        return sorted(
            candidates,
            key=lambda candidate: (
                -candidate.confidence,
                -candidate.occurrences,
                candidate.text,
            ),
        )

    @staticmethod
    def _normalize_line(line: str) -> str:
        """
        Normalize only whitespace.

        Semantic content is untouched.
        """

        return " ".join(line.split())

    @staticmethod
    def _classify(
        text: str,
        page_count: int,
        total_pages: int,
    ) -> tuple[float, str]:

        if total_pages == 0:
            return 0.0, ""

        page_ratio = page_count / total_pages

        word_count = len(text.split())

        # Very short repeated text across many pages
        # is a strong header/footer candidate.
        if (
            word_count <= 8
            and page_ratio >= 0.50
            and page_count >= 3
        ):
            return 0.90, "repeated_page_element"

        # Short repeated text across several pages.
        if (
            word_count <= 12
            and page_count >= 3
        ):
            return 0.75, "repeated_document_text"

        # Longer repeated content is still a candidate,
        # but confidence is lower because it may be
        # intentionally repeated.
        if page_count >= 2:
            return 0.55, "repeated_content"

        return 0.0, ""