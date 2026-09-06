from app.models.schemas import AnalysisResult
from app.processors.semantic_deduplicator import SemanticDeduplicator
from app.core.task_detector import TaskDetector

class InputAnalyzer:

    def __init__(self):
        self.semantic_deduplicator = SemanticDeduplicator()
        self.task_detector = TaskDetector()

    def analyze(self, text: str) -> AnalysisResult:
        text = text.strip()

        sentences = [
            sentence.strip()
            for sentence in text.split(".")
            if sentence.strip()
        ]

        if not sentences:
            return AnalysisResult(
                input_text=text,
                input_length=len(text),
                sentence_count=0,
                duplicate_count=0,
                is_empty=True,
            )

        deduplicated_text = self.semantic_deduplicator.process(text)
        deduplicated_sentences = [
            s.strip()
            for s in deduplicated_text.split(".")
            if s.strip()
        ]

        duplicate_count = max(0, len(sentences) - len(deduplicated_sentences))

        return AnalysisResult(
            input_text=text,
            input_length=len(text),
            sentence_count=len(sentences),
            duplicate_count=duplicate_count,
            task_type=self.task_detector.detect(text),
            is_empty=not bool(text),
        )
