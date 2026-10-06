from app.nlp.safety_validator import validate_removal


def test_safe_removal():
    original = "I am actually fixing the error."
    counterfactual = "I am fixing the error."

    is_safe, reason = validate_removal(
        original,
        counterfactual,
    )

    assert is_safe is True
    assert reason == "safe"


def test_reject_negation_removal():
    original = "The server is not running."
    counterfactual = "The server is running."

    is_safe, reason = validate_removal(
        original,
        counterfactual,
    )

    assert is_safe is False
    assert "negation_removed" in reason


def test_reject_constraint_removal():
    original = "The user can only access the admin dashboard."
    counterfactual = "The user can access the admin dashboard."

    is_safe, reason = validate_removal(
        original,
        counterfactual,
    )

    assert is_safe is False
    assert "constraint_removed" in reason


def test_reject_number_change():
    original = "The server supports 100 users."
    counterfactual = "The server supports users."

    is_safe, reason = validate_removal(
        original,
        counterfactual,
    )

    assert is_safe is False
    assert reason == "number_changed"


def test_reject_technical_term_removal():
    original = "The Flask backend handles authentication."
    counterfactual = "The backend handles authentication."

    is_safe, reason = validate_removal(
        original,
        counterfactual,
    )

    assert is_safe is False
    assert "technical_term_removed" in reason