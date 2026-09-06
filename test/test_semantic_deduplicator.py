from app.processors.semantic_deduplicator import SemanticDeduplicator


def test_semantically_redundant_sentences_are_reduced():
    processor = SemanticDeduplicator()

    text = (
        "Flask is used as the backend. "
        "The application backend is built using Flask."
    )

    result = processor.process(text)

    assert "Flask is used as the backend." in result
    assert result.count(".") == 1


def test_distinct_information_is_preserved():
    processor = SemanticDeduplicator()

    text = (
        "Flask is used now. "
        "FastAPI may be used later."
    )

    result = processor.process(text)

    assert "Flask is used now." in result
    assert "FastAPI may be used later." in result

def test_threshold_can_be_configured():
    processor = SemanticDeduplicator(threshold=0.95)

    assert processor.threshold == 0.95


def test_similar_but_distinct_information_is_preserved():
    processor = SemanticDeduplicator(threshold=0.85)

    text = (
        "Flask is used as the backend. "
        "FastAPI may replace Flask in the future."
    )

    result = processor.process(text)

    assert "Flask is used as the backend." in result
    assert "FastAPI may replace Flask in the future." in result