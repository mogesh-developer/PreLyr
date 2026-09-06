import re

from app.models.schemas import TaskType


class TaskDetector:

    def detect(self, text: str) -> TaskType:
        text = text.strip().casefold()

        if not text:
            return TaskType.UNKNOWN

        if self._matches(
            text,
            [
                r"\bwhy am i getting\b",
                r"\bwhy is .* not working\b",
                r"\bnot working\b",
                r"\berror\b",
                r"\bexception\b",
                r"\bfailed\b",
                r"\bfailing\b",
                r"\bbug\b",
            ],
        ):
            return TaskType.DEBUGGING

        if self._matches(
            text,
            [
                r"\bsummarize\b",
                r"\bsummarise\b",
                r"\bsummary\b",
                r"\bkey points\b",
            ],
        ):
            return TaskType.SUMMARIZATION

        if self._matches(
            text,
            [
                r"\bextract\b",
                r"\bfind the\b.*\bfrom\b",
                r"\blist the\b",
            ],
        ):
            return TaskType.EXTRACTION

        if self._matches(
            text,
            [
                r"\bcompare\b",
                r"\bcomparison\b",
                r"\bdifference between\b",
                r"\bvs\.?\b",
                r"\bversus\b",
            ],
        ):
            return TaskType.COMPARISON

        if self._matches(
            text,
            [
                r"\bexplain\b",
                r"\bwhat is\b",
                r"\bwhat are\b",
                r"\bhow does\b",
                r"\bhow do\b",
            ],
        ):
            return TaskType.EXPLANATION

        if self._matches(
            text,
            [
                r"\bwrite\b",
                r"\bgenerate\b",
                r"\bcreate\b",
                r"\bdraft\b",
                r"\bmake\b",
            ],
        ):
            return TaskType.GENERATION

        return TaskType.UNKNOWN

    def _matches(self, text: str, patterns: list[str]) -> bool:
        return any(re.search(pattern, text) for pattern in patterns)