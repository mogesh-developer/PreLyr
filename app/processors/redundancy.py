from app.processors.deduplicator import Deduplicator
from app.processors.semantic_deduplicator import SemanticDeduplicator


class RedundancyProcessor:

    def __init__(
        self,
        semantic_threshold: float = 0.85,
    ):
        self.exact_deduplicator = Deduplicator()
        self.semantic_deduplicator = SemanticDeduplicator(
            threshold=semantic_threshold
        )

    def process(self, text: str) -> str:
        sentences = [
            sentence.strip()
            for sentence in text.split(".")
            if sentence.strip()
        ]

        normalized = [sentence.casefold() for sentence in sentences]

        has_exact_duplicates = (
            len(normalized) != len(set(normalized))
        )

        exact_result = self.exact_deduplicator.process(text)

        if has_exact_duplicates:
            return exact_result

        return self.semantic_deduplicator.process(text)