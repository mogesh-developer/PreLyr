from __future__ import annotations

from dataclasses import dataclass

from app.processors.document_repetition import (
    DocumentRepetitionDetector,
    RepetitionCandidate,
)


@dataclass(frozen=True)
class DocumentOptimizationResult:
    original: str
    optimized: str

    removed: list[RepetitionCandidate]
    preserved: list[RepetitionCandidate]


class DocumentRepetitionOptimizer:
    """
    Conservative document-level repetition optimizer.

    Detection and removal are separate.

    A repeated line is removed only when the detector
    gives it high enough confidence that it is likely
    a repeated document-level element.

    Uncertain candidates are preserved.
    """

    def __init__(
        self,
        detector: DocumentRepetitionDetector | None = None,
    ) -> None:

        self.detector = (
            detector
            or DocumentRepetitionDetector()
        )

    def optimize(
        self,
        pages: list[str],
    ) -> DocumentOptimizationResult:

        candidates = self.detector.detect(pages)

        removable: list[RepetitionCandidate] = []
        preserved: list[RepetitionCandidate] = []

        for candidate in candidates:

            if self._is_safe_to_remove(candidate):
                removable.append(candidate)
            else:
                preserved.append(candidate)

        optimized_pages = self._remove_candidates(
            pages,
            removable,
        )

        original = self._combine_pages(pages)

        optimized = self._combine_pages(
            optimized_pages
        )

        return DocumentOptimizationResult(
            original=original,
            optimized=optimized,
            removed=removable,
            preserved=preserved,
        )

    @staticmethod
    def _is_safe_to_remove(
        candidate: RepetitionCandidate,
    ) -> bool:

        return (
            candidate.reason
            == "repeated_page_element"
            and candidate.confidence >= 0.90
        )

    @staticmethod
    def _remove_candidates(
        pages: list[str],
        candidates: list[RepetitionCandidate],
    ) -> list[str]:

        removable_text = {
            candidate.text
            for candidate in candidates
        }

        optimized_pages: list[str] = []

        for page in pages:

            lines = page.splitlines()

            kept_lines: list[str] = []

            for line in lines:

                normalized = " ".join(
                    line.split()
                )

                if (
                    normalized
                    and normalized in removable_text
                ):
                    continue

                kept_lines.append(line)

            optimized_pages.append(
                "\n".join(kept_lines)
            )

        return optimized_pages

    @staticmethod
    def _combine_pages(
        pages: list[str],
    ) -> str:

        return "\n\n".join(
            page.strip()
            for page in pages
            if page.strip()
        )