from app.nlp.structural_validator import validate_structure


def test_accepts_valid_transformation():
    original = (
        "Basically, the API is ready."
    )

    counterfactual = (
        "The API is ready."
    )

    is_safe, reason = validate_structure(
        original,
        counterfactual,
    )

    assert is_safe is True
    assert reason == "structure_ok"


def test_rejects_lowercase_sentence_start():
    original = (
        "Basically, the server works."
    )

    counterfactual = (
        "the server works."
    )

    is_safe, reason = validate_structure(
        original,
        counterfactual,
    )

    assert is_safe is False
    assert reason == "lowercase_sentence_start"


def test_rejects_clause_collision():
    original = (
        "The request failed due to the fact that "
        "the API was unavailable."
    )

    counterfactual = (
        "The request failed the API was unavailable."
    )

    is_safe, reason = validate_structure(
        original,
        counterfactual,
    )

    assert is_safe is False
    assert reason == "clause_collision"


def test_rejects_malformed_punctuation():
    original = (
        "Basically, the API works."
    )

    counterfactual = (
        "The API works ,"
    )

    is_safe, reason = validate_structure(
        original,
        counterfactual,
    )

    assert is_safe is False
    assert reason == "malformed_punctuation"


def test_accepts_technical_text():
    original = (
        "Actually, Python is running."
    )

    counterfactual = (
        "Python is running."
    )

    is_safe, reason = validate_structure(
        original,
        counterfactual,
    )

    assert is_safe is True
    assert reason == "structure_ok"


def test_rejects_empty_counterfactual():
    is_safe, reason = validate_structure(
        "Basically, this works.",
        "",
    )

    assert is_safe is False
    assert reason == "empty_counterfactual"