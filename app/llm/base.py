from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Provider interface used by PreLyr to communicate with an LLM.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a response from the LLM.
        """
        raise NotImplementedError