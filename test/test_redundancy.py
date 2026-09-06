from app.processors.redundancy import RedundancyProcessor


def test_redundancy_processor_removes_exact_duplicates():
    processor = RedundancyProcessor()

    text = (
        "Flask is the backend. "
        "Flask is the backend. "
        "PostgreSQL is the database."
    )

    result = processor.process(text)

    assert result.count("Flask is the backend.") == 1
    assert "PostgreSQL is the database." in result


def test_redundancy_processor_handles_semantic_duplicates():
    processor = RedundancyProcessor()

    text = (
        "Flask is used as the backend. "
        "The application backend is built using Flask."
    )

    result = processor.process(text)

    assert "Flask is used as the backend." in result
    assert result.count(".") == 1


def test_redundancy_processor_preserves_distinct_information():
    processor = RedundancyProcessor()

    text = (
        "Flask is used now. "
        "FastAPI may replace Flask in the future."
    )

    result = processor.process(text)

    assert "Flask is used now." in result
    assert "FastAPI may replace Flask in the future." in result