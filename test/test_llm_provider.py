from app.llm.mock import MockLLMProvider


def test_mock_provider_returns_response():
    provider = MockLLMProvider(
        response="Hello from mock LLM."
    )

    result = provider.generate("Explain Flask.")

    assert result == "Hello from mock LLM."


def test_mock_provider_receives_prompt():
    provider = MockLLMProvider()

    prompt = "Explain Flask."

    provider.generate(prompt)

    assert provider.last_prompt == prompt