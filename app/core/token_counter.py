import tiktoken


class TokenCounter:

    def __init__(self, encoding_name: str = "cl100k_base"):
        self.encoding = tiktoken.get_encoding(encoding_name)

    def count(self, text: str) -> int:
        if not text:
            return 0

        return len(self.encoding.encode(text))

    def reduction_percentage(
        self,
        original_text: str,
        optimized_text: str,
    ) -> float:
        original_tokens = self.count(original_text)
        optimized_tokens = self.count(optimized_text)

        if original_tokens == 0:
            return 0.0

        reduction = original_tokens - optimized_tokens

        return (reduction / original_tokens) * 100