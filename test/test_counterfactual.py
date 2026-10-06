from app.nlp.candidate_detector import Candidate
from app.nlp.counterfactual import transform_candidate


def test_in_order_to_transformation():
    text = (
        "I use this method in order to test the API."
    )

    phrase = "in order to"
    start = text.index(phrase)

    candidate = Candidate(
        text=phrase,
        start=start,
        end=start + len(phrase),
        reason="verbose infinitive phrase",
        action="TRANSFORM",
    )

    result = transform_candidate(
        text,
        candidate,
    )

    assert result == (
        "I use this method to test the API."
    )


def test_due_to_fact_transformation():
    text = (
        "The request failed due to the fact that "
        "the API was unavailable."
    )

    phrase = "due to the fact that"
    start = text.index(phrase)

    candidate = Candidate(
        text=phrase,
        start=start,
        end=start + len(phrase),
        reason="verbose causal phrase",
        action="TRANSFORM",
    )

    result = transform_candidate(
        text,
        candidate,
    )

    assert result == (
        "The request failed because the API was unavailable."
    )


def test_temporal_transformation():
    text = (
        "At this point in time, the server is running."
    )

    phrase = "At this point in time"
    start = text.index(phrase)

    candidate = Candidate(
        text=phrase,
        start=start,
        end=start + len(phrase),
        reason="verbose temporal phrase",
        action="TRANSFORM",
    )

    result = transform_candidate(
        text,
        candidate,
    )

    assert result == (
        "Currently, the server is running."
    )


def test_sentence_start_filler_preserves_capitalization():
    text = "Actually, the server works."

    filler = "Actually"
    start = text.index(filler)

    candidate = Candidate(
        text=filler,
        start=start,
        end=start + len(filler),
        reason="discourse filler",
        action="REMOVE",
    )

    result = transform_candidate(
        text,
        candidate,
    )

    assert result == "The server works."


def test_repeated_sentence_start_filler_preserves_capitalization():
    text = (
        "Actually, the server works. "
        "Basically, the database works."
    )

    filler = "Basically"
    start = text.index(filler)

    candidate = Candidate(
        text=filler,
        start=start,
        end=start + len(filler),
        reason="discourse filler",
        action="REMOVE",
    )

    result = transform_candidate(
        text,
        candidate,
    )

    assert result == (
        "Actually, the server works. "
        "The database works."
    )