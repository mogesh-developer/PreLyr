import re

from app.models.schemas import TaskType


class RelevantContextProcessor:

    def process(
        self,
        text: str,
        task_type: TaskType,
    ) -> str:
        if not text.strip():
            return text

        if task_type == TaskType.UNKNOWN:
            return text

        sentences = self._split_sentences(text)

        if len(sentences) <= 2:
            return text

        scored_sentences = [
            (sentence, self._score(sentence, task_type))
            for sentence in sentences
        ]

        relevant = [
            sentence
            for sentence, score in scored_sentences
            if score > 0
        ]

        # Lossless-by-default:
        # If we cannot confidently identify relevant context,
        # preserve the original input.
        if not relevant:
            return text

        return " ".join(relevant)

    def _split_sentences(self, text: str) -> list[str]:
        return [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
            if sentence.strip()
        ]

    def _score(
        self,
        sentence: str,
        task_type: TaskType,
    ) -> int:
        text = sentence.casefold()

        keywords = {
            TaskType.DEBUGGING: [
                "error",
                "exception",
                "failed",
                "failure",
                "fails",
                "fail",
                "crash",
                "crashes",
                "crashed",
                "startup",
                "service",
                "bug",
                "traceback",
                "401",
                "403",
                "404",
                "500",
                "not working",
                "changed",
                "migration",
                "connection",
                "config",
                "configuration",
                "cause",
                "issue",
                "database",
            ],
            TaskType.EXPLANATION: [
                "what",
                "why",
                "how",
                "means",
                "definition",
                "because",
                "selected",
                "framework",
                "reason",
            ],
            TaskType.SUMMARIZATION: [
                "important",
                "main",
                "key",
                "result",
                "conclusion",
                "summary",
            ],
            TaskType.EXTRACTION: [
                "deadline",
                "date",
                "name",
                "requirement",
                "amount",
                "email",
                "phone",
                "must",
                "report",
                "provide",
                "submit",
                "technical",
            ],
            TaskType.COMPARISON: [
                "difference",
                "similar",
                "advantage",
                "disadvantage",
                "better",
                "faster",
                "cost",
                "lightweight",
                "simple",
                "ecosystem",
                "performance",
                "support",
                "vs",
                "versus",
                "compare",
                "compared",
                "requires",
                "less",
                "more",
                "setup",
                "configuration",
                "both",
            ],
            TaskType.GENERATION: [
                "requirement",
                "required",
                "must",
                "should",
                "need",
                "function",
                "feature",
                "output",
                "authentication",
                "because",
                "private",
                "security",
                "data",
            ],
        }

        return sum(
            1
            for keyword in keywords.get(task_type, [])
            if keyword in text
        )