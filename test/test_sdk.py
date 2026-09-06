from app import PreLyr
from app.models.schemas import ProcessingOperation
from app.llm.mock import MockLLMProvider

def test_sdk_can_optimize_input():
    prelyr = PreLyr()

    result = prelyr.optimize(
        "Flask is used. Flask is used."
    )

    assert result.context.optimized_text
    assert "Flask" in result.context.optimized_text


def test_sdk_exposes_processing_result():
    prelyr = PreLyr()

    result = prelyr.optimize(
        "Flask is used. Flask is used."
    )

    assert result.analysis is not None
    assert result.decision is not None
    assert result.context is not None


def test_sdk_uses_existing_engine_pipeline():
    prelyr = PreLyr()

    result = prelyr.optimize(
        "Flask is used. Flask is used."
    )

    assert ProcessingOperation.DEDUPLICATE in (
        result.context.operations_applied
    )


def test_sdk_preserves_clean_input():
    prelyr = PreLyr()

    text = "Explain what Flask is."

    result = prelyr.optimize(text)

    assert result.context.optimized_text == text


def test_sdk_generate_requires_provider():
    prelyr = PreLyr()

    try:
        prelyr.generate("Explain Flask.")
        assert False, "Expected ValueError"
    except ValueError as error:
        assert str(error) == "No LLM provider configured."



def test_sdk_generate_uses_provider():
    provider = MockLLMProvider(
        response="Flask is a Python web framework."
    )

    prelyr = PreLyr(
        llm_provider=provider
    )

    result = prelyr.generate(
        "Explain Flask."
    )

    assert result == "Flask is a Python web framework."


def test_sdk_sends_optimized_context_to_provider():
    provider = MockLLMProvider()

    prelyr = PreLyr(
        llm_provider=provider
    )

    text = "Flask is used. Flask is used."

    prelyr.generate(text)

    assert provider.last_prompt is not None
    assert "Optimized Context" in provider.last_prompt