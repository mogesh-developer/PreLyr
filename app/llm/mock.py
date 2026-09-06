from app.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """
    Deterministic provider used for tests and local development.
    """

    def __init__(self, response: str = "Mock LLM response"):
        self.response = response
        self.last_prompt = None

    def generate(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self.response