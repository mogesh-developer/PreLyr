class Deduplicator:

    def process(self, text: str) -> str:
        sentences = [
            sentence.strip()
            for sentence in text.split(".")
            if sentence.strip()
        ]

        seen = set()
        unique_sentences = []

        for sentence in sentences:
            normalized = sentence.casefold()

            if normalized in seen:
                continue

            seen.add(normalized)
            unique_sentences.append(sentence)

        if not unique_sentences:
            return text

        return " ".join(
            sentence if sentence.endswith(".") else f"{sentence}."
            for sentence in unique_sentences
        )