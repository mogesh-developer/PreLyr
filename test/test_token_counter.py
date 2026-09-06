from app.core.token_counter import TokenCounter


def test_counts_tokens():
    counter = TokenCounter()

    result = counter.count(
        "The backend uses Flask and PostgreSQL."
    )

    assert result > 0


def test_empty_text_has_zero_tokens():
    counter = TokenCounter()

    assert counter.count("") == 0


def test_reduction_percentage():
    counter = TokenCounter()

    original = (
        "The backend uses Flask. "
        "The backend is built using Flask. "
        "The database uses PostgreSQL."
    )

    optimized = (
        "The backend uses Flask. "
        "The database uses PostgreSQL."
    )

    reduction = counter.reduction_percentage(
        original,
        optimized,
    )

    assert reduction > 0