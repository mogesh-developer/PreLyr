from model2vec import StaticModel
from sklearn.metrics.pairwise import cosine_similarity

from app.processors.safety import SafetyValidator


class SemanticDeduplicator:
    def __init__(
        self,
        model_name: str = "minishlab/potion-base-8M",
        threshold: float = 0.85,
    ):
        self.model_name = model_name
        self.threshold = threshold
        self.model = None
        self.safety_validator = SafetyValidator()

    def _load_model(self):
        if self.model is None:
            self.model = StaticModel.from_pretrained(
                self.model_name
            )

    def process(self, text: str) -> str:
        sentences = [
            sentence.strip()
            for sentence in text.split(".")
            if sentence.strip()
        ]

        if len(sentences) <= 1:
            return text

        self._load_model()

        embeddings = self.model.encode(sentences)

        kept_sentences = [sentences[0]]
        kept_embeddings = [embeddings[0]]

        for index in range(1, len(sentences)):
            current_sentence = sentences[index]
            current_embedding = embeddings[index]

            similarities = cosine_similarity(
                [current_embedding],
                kept_embeddings,
            )[0]

            is_duplicate = False

            for kept_index, similarity in enumerate(similarities):
                if similarity < self.threshold:
                    continue

                kept_sentence = kept_sentences[kept_index]

                if self.safety_validator.is_safe_to_deduplicate(
                    kept_sentence,
                    current_sentence,
                ):
                    is_duplicate = True
                    break

            if is_duplicate:
                continue

            kept_sentences.append(current_sentence)
            kept_embeddings.append(current_embedding)

        return " ".join(
            sentence if sentence.endswith(".") else f"{sentence}."
            for sentence in kept_sentences
        )