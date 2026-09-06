from app.core.engine import PreLyrEngine


class PreLyr:
    """
    Public developer-facing interface for PreLyr.

    Users should interact with this class instead of
    directly accessing the internal PreLyrEngine.
    """

    def __init__(self, llm_provider=None):
        self._engine = PreLyrEngine(
            llm_provider=llm_provider
        )

    def optimize(self, text: str):
        """
        Analyze and optimize user input.

        Returns:
            PreLyrResult
        """
        return self._engine.process(text)

    def generate(self, text: str) -> str:
        """
        Optimize the input and send it to the configured LLM provider.

        Raises:
            ValueError: If no LLM provider is configured.
        """
        return self._engine.generate(text)