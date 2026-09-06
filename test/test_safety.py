from app.processors.safety import SafetyValidator


def test_same_sentence_is_safe():
    validator = SafetyValidator()

    assert validator.is_safe_to_deduplicate(
        "The backend uses Flask.",
        "The backend uses Flask.",
    )


def test_paraphrase_without_critical_difference_is_safe():
    validator = SafetyValidator()

    assert validator.is_safe_to_deduplicate(
        "The backend uses Flask.",
        "The backend is built using Flask.",
    )


def test_different_ports_are_unsafe():
    validator = SafetyValidator()

    assert not validator.is_safe_to_deduplicate(
        "The server runs on port 8000.",
        "The server runs on port 9000.",
    )


def test_different_versions_are_unsafe():
    validator = SafetyValidator()

    assert not validator.is_safe_to_deduplicate(
        "The application requires Python 3.11.",
        "The application requires Python 3.12.",
    )


def test_different_http_statuses_are_unsafe():
    validator = SafetyValidator()

    assert not validator.is_safe_to_deduplicate(
        "The server returned a 401 error.",
        "The server returned a 500 error.",
    )


def test_success_failure_is_unsafe():
    validator = SafetyValidator()

    assert not validator.is_safe_to_deduplicate(
        "The database connection succeeded.",
        "The database connection failed.",
    )


def test_valid_invalid_is_unsafe():
    validator = SafetyValidator()

    assert not validator.is_safe_to_deduplicate(
        "The authentication token is valid.",
        "The authentication token is invalid.",
    )


def test_enabled_disabled_is_unsafe():
    validator = SafetyValidator()

    assert not validator.is_safe_to_deduplicate(
        "The feature is enabled.",
        "The feature is disabled.",
    )


def test_different_retry_limits_are_unsafe():
    validator = SafetyValidator()

    assert not validator.is_safe_to_deduplicate(
        "The retry limit is 3 attempts.",
        "The retry limit is 5 attempts.",
    )


def test_different_sizes_are_unsafe():
    validator = SafetyValidator()

    assert not validator.is_safe_to_deduplicate(
        "The maximum request size is 10 MB.",
        "The maximum request size is 20 MB.",
    )


def test_different_timeouts_are_unsafe():
    validator = SafetyValidator()

    assert not validator.is_safe_to_deduplicate(
        "The request timeout is 30 seconds.",
        "The request timeout is 60 seconds.",
    )


def test_unrelated_sentences_without_critical_difference_are_safe():
    validator = SafetyValidator()

    assert validator.is_safe_to_deduplicate(
        "The backend uses Flask.",
        "The backend is built with Flask.",
    )