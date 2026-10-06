from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class HeadingCandidate:
    page: int
    text: str
    font_size: float
    font_name: str | None
    score: float


class PDFHeadingDetector:
    """
    Conservative heading candidate detector.

    Uses layout/font signals from pdfminer output.

    A candidate is not automatically treated as a heading.
    """

    def detect(
        self,
        blocks: list[dict],
    ) -> list[HeadingCandidate]:

        if not blocks:
            return []

        font_sizes = [
            block["font_size"]
            for block in blocks
            if block.get("font_size") is not None
        ]

        if not font_sizes:
            return []

        median_font_size = self._median(font_sizes)

        candidates: list[HeadingCandidate] = []

        for block in blocks:
            text = block["text"].strip()
            font_size = block.get("font_size")
            font_name = block.get("font_name")

            if not text or font_size is None:
                continue

            score = self._score(
                text=text,
                font_size=font_size,
                font_name=font_name,
                median_font_size=median_font_size,
            )

            if score >= 0.60:
                candidates.append(
                    HeadingCandidate(
                        page=block["page"],
                        text=text,
                        font_size=font_size,
                        font_name=font_name,
                        score=score,
                    )
                )

        return candidates

    def _score(
        self,
        text: str,
        font_size: float,
        font_name: str | None,
        median_font_size: float,
    ) -> float:

        score = 0.0

        # Larger than normal text is a strong signal.
        if font_size >= median_font_size * 1.8:
            score += 0.50
        elif font_size >= median_font_size * 1.4:
            score += 0.30

        # Bold / semibold is another signal.
        if font_name:
            font_lower = font_name.lower()

            if "bold" in font_lower:
                score += 0.25
            elif "semibold" in font_lower:
                score += 0.20

        # Headings are usually reasonably short.
        word_count = len(text.split())

        if 1 <= word_count <= 12:
            score += 0.15

        # Very long text is unlikely to be a heading.
        if len(text) > 120:
            score -= 0.20

        # URLs / obvious UI noise should not become headings.
        if self._looks_like_noise(text):
            score -= 0.40

        return max(0.0, min(score, 1.0))

    @staticmethod
    def _median(values: list[float]) -> float:
        values = sorted(values)

        middle = len(values) // 2

        if len(values) % 2:
            return values[middle]

        return (
            values[middle - 1] + values[middle]
        ) / 2

    @staticmethod
    def _looks_like_noise(text: str) -> bool:

        if text.startswith("http://"):
            return True

        if text.startswith("https://"):
            return True

        if re.search(r"\.(pdf|jpg|png|jpeg)$", text.lower()):
            return True

        return False