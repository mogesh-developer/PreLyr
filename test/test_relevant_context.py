from app.models.schemas import TaskType
from app.processors.relevant_context import RelevantContextProcessor


def test_debugging_context_selects_relevant_sentences():
    processor = RelevantContextProcessor()

    text = (
        "The application started successfully. "
        "The server returned a 401 error. "
        "Authentication failed for the request. "
        "The development server is running on port 8000."
    )

    result = processor.process(
        text,
        TaskType.DEBUGGING,
    )

    assert "401 error" in result
    assert "Authentication failed" in result
    assert "started successfully" not in result


def test_unknown_task_preserves_original_text():
    processor = RelevantContextProcessor()

    text = (
        "The backend uses Flask. "
        "The database is PostgreSQL. "
        "Authentication is required."
    )

    result = processor.process(
        text,
        TaskType.UNKNOWN,
    )

    assert result == text


def test_short_input_is_preserved():
    processor = RelevantContextProcessor()

    text = "Why am I getting a 401 error?"

    result = processor.process(
        text,
        TaskType.DEBUGGING,
    )

    assert result == text


def test_no_relevant_context_preserves_original():
    processor = RelevantContextProcessor()

    text = (
        "The weather is pleasant today. "
        "The office opens at nine. "
        "The team has a meeting tomorrow."
    )

    result = processor.process(
        text,
        TaskType.DEBUGGING,
    )

    assert result == text