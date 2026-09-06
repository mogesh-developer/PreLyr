import re
from app.models.schemas import ProcessingOperation

class StructureProcessor:
    def process(self, text: str) -> str:
        sentences = [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
            if sentence.strip()
        ]

        if not sentences:
            return text

        return "\n".join(
            f"- {sentence.rstrip('.!?')}{self._ending_punctuation(sentence)}"
            for sentence in sentences
        )

    def _ending_punctuation(self, sentence: str) -> str:
        if sentence.endswith((".", "!", "?")):
            return sentence[-1]
        return "."