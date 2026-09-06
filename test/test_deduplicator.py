from app.processors.deduplicator import Deduplicator
from app.processors.semantic_deduplicator import SemanticDeduplicator


def test_exact_duplicate_sentences_are_removed():
    processor = Deduplicator()

    text = (
        "Flask is used as the backend. "
        "Flask is used as the backend. "
        "The database is PostgreSQL. "
        "The database is PostgreSQL. "
        "Authentication is required."
    )

    result = processor.process(text)

    assert result.count("Flask is used as the backend.") == 1
    assert result.count("The database is PostgreSQL.") == 1
    assert result.count("Authentication is required.") == 1


def test_unique_information_is_preserved():
    processor = Deduplicator()

    text = (
        "Flask is used now. "
        "FastAPI may be used later."
    )

    result = processor.process(text)

    assert "Flask is used now." in result
    assert "FastAPI may be used later." in result


def test_duplicate_detection_is_case_insensitive():
    processor = Deduplicator()

    text = (
        "Flask is the backend. "
        "flask is the backend. "
        "PostgreSQL is used."
    )

    result = processor.process(text)

    assert result.count("Flask is the backend.") == 1
    assert result.count("flask is the backend.") == 0
    assert "PostgreSQL is used." in result


def test_order_is_preserved():
    processor = Deduplicator()

    text = (
        "Authentication is required. "
        "Flask is used. "
        "Database is PostgreSQL. "
        "Flask is used."
    )

    result = processor.process(text)

    assert result.index("Authentication") < result.index("Flask")
    assert result.index("Flask") < result.index("Database")

def test_model_is_not_loaded_during_initialization():
    processor = SemanticDeduplicator()

    assert processor.model is None

def test_model_is_loaded_when_processing():
    processor = SemanticDeduplicator()

    assert processor.model is None

    processor.process(
        "Flask is used as the backend. "
        "The application backend is built using Flask."
    )

    assert processor.model is not None

def test_single_sentence_does_not_load_model():
    processor = SemanticDeduplicator()

    result = processor.process("Flask is used as the backend.")

    assert result == "Flask is used as the backend."
    assert processor.model is None