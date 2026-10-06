from app.nlp.candidate_detector import detect_candidates


def test_detects_safe_candidate():
    text = "I am actually trying to fix this error."

    candidates = detect_candidates(text)

    assert any(
        candidate.text.lower() == "actually"
        for candidate in candidates
    )


def test_does_not_remove_sensitive_words():
    text = "The user can only access the admin dashboard."

    candidates = detect_candidates(text)

    assert not any(
        candidate.text.lower() == "only"
        for candidate in candidates
    )