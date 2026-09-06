import pytest

from app.core.engine import PreLyrEngine


@pytest.fixture
def engine():
    return PreLyrEngine()


def test_clean_input_preserves_context(engine):
    text = "Explain what Flask is."

    result = engine.process(text)

    print("\n--- Clean Input ---")
    print("Original:", result.context.original_text)
    print("Optimized:", result.context.optimized_text)
    print("Original tokens:", result.context.original_tokens)
    print("Optimized tokens:", result.context.optimized_tokens)
    print("Reduction:", result.context.token_reduction_percentage)

    assert result.context.optimized_text == text
    assert result.context.token_reduction_percentage == 0.0


def test_exact_redundancy_reduction(engine):
    text = (
        "Flask is used as the backend. "
        "PostgreSQL is used as the database. "
        "Flask is used as the backend. "
        "PostgreSQL is used as the database."
    )

    result = engine.process(text)

    print("\n--- Exact Redundancy ---")
    print("Original:", result.context.original_text)
    print("Optimized:", result.context.optimized_text)
    print("Original tokens:", result.context.original_tokens)
    print("Optimized tokens:", result.context.optimized_tokens)
    print("Reduction:", result.context.token_reduction_percentage)

    assert result.context.optimized_tokens < result.context.original_tokens
    assert "Flask" in result.context.optimized_text
    assert "PostgreSQL" in result.context.optimized_text


def test_semantic_redundancy_preserves_critical_information(engine):
    text = (
        "Flask is used as the backend. "
        "The backend application is built with Flask. "
        "PostgreSQL is used as the database. "
        "The database is PostgreSQL. "
        "The server runs on port 5000. "
        "The server runs on port 8000."
    )

    result = engine.process(text)

    print("\n--- Semantic Redundancy + Critical Information ---")
    print("Original:", result.context.original_text)
    print("Optimized:", result.context.optimized_text)
    print("Original tokens:", result.context.original_tokens)
    print("Optimized tokens:", result.context.optimized_tokens)
    print("Reduction:", result.context.token_reduction_percentage)

    optimized = result.context.optimized_text

    assert result.context.optimized_tokens <= result.context.original_tokens

    # Important technologies must remain.
    assert "Flask" in optimized
    assert "PostgreSQL" in optimized

    # Different port values must NOT be collapsed.
    assert "5000" in optimized
    assert "8000" in optimized


def test_large_redundant_input(engine):
    text = " ".join(
        [
            "Flask is used as the backend."
            for _ in range(10)
        ]
    )

    result = engine.process(text)

    print("\n--- Large Redundant Input ---")
    print("Original tokens:", result.context.original_tokens)
    print("Optimized tokens:", result.context.optimized_tokens)
    print("Reduction:", result.context.token_reduction_percentage)

    assert result.context.optimized_tokens < result.context.original_tokens
    assert result.context.token_reduction_percentage > 0