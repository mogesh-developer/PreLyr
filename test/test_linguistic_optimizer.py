from app.nlp.linguistic_optimizer import LinguisticOptimizer


def test_optimizer_removes_candidate():
    optimizer = LinguisticOptimizer()

    text = "I am actually trying to fix this error."

    result = optimizer.optimize(text)

    assert result.optimized == (
        "I am trying to fix this error."
    )

    assert len(result.accepted) == 1
    assert result.original_tokens > result.optimized_tokens
    assert result.token_reduction > 0


def test_optimizer_noop_for_clean_input():
    optimizer = LinguisticOptimizer()

    text = "Explain how Flask routing works."

    result = optimizer.optimize(text)

    assert result.optimized == text
    assert result.accepted == []

    assert (
        result.original_tokens
        == result.optimized_tokens
    )

    assert result.token_reduction == 0


def test_optimizer_preserves_sensitive_information():
    optimizer = LinguisticOptimizer()

    text = (
        "The Flask backend is not currently "
        "running on port 8000."
    )

    result = optimizer.optimize(text)

    assert "Flask" in result.optimized
    assert "not" in result.optimized
    assert "8000" in result.optimized


def test_optimizer_never_increases_tokens():
    optimizer = LinguisticOptimizer()

    texts = [
        "I am actually trying to fix this error.",
        "The server is currently running.",
        "Basically, I need to fix the API.",
        "Explain how Flask routing works.",
    ]

    for text in texts:
        result = optimizer.optimize(text)

        assert (
            result.optimized_tokens
            <= result.original_tokens
        )


def test_token_reduction_is_calculated_correctly():
    optimizer = LinguisticOptimizer()

    text = (
        "I am actually trying to fix this error."
    )

    result = optimizer.optimize(text)

    expected_reduction = (
        result.original_tokens
        - result.optimized_tokens
    )

    assert result.token_reduction == expected_reduction


def test_noop_for_empty_input():
    optimizer = LinguisticOptimizer()

    result = optimizer.optimize("")

    assert result.optimized == ""
    assert result.original_tokens == 0
    assert result.optimized_tokens == 0
    assert result.token_reduction == 0
    assert result.accepted == []
    assert result.rejected == []

def test_optimizer_handles_multiple_candidates():
    optimizer = LinguisticOptimizer()

    text = (
        "I am actually basically trying "
        "to fix this error."
    )

    result = optimizer.optimize(text)

    assert result.optimized == (
        "I am trying to fix this error."
    )

    assert len(result.accepted) == 2
    assert result.optimized_tokens <= result.original_tokens


def test_optimizer_handles_repeated_candidate():
    optimizer = LinguisticOptimizer()

    text = (
        "Basically, I am trying to fix this. "
        "Basically, I need to test it."
    )

    result = optimizer.optimize(text)

    assert result.optimized == (
        "I am trying to fix this. "
        "I need to test it."
    )

    assert len(result.accepted) == 2


def test_optimizer_preserves_candidate_order():
    optimizer = LinguisticOptimizer()

    text = (
        "Actually, I am basically trying "
        "to fix this error."
    )

    result = optimizer.optimize(text)

    assert result.optimized == (
        "I am trying to fix this error."
    )

    accepted_texts = [
        candidate.text.lower()
        for candidate in result.accepted
    ]

    assert accepted_texts == [
        "actually",
        "basically",
    ]