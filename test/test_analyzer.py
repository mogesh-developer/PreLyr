from app.core.analyzer import InputAnalyzer
from app.models.schemas import TaskType

def test_analyzer_with_clean_input():
    analyzer = InputAnalyzer()

    result = analyzer.analyze("Explain what Flask is.")

    assert result.input_text == "Explain what Flask is."
    assert result.is_empty is False
    assert result.sentence_count == 1


def test_analyzer_with_empty_input():
    analyzer = InputAnalyzer()

    result = analyzer.analyze("")

    assert result.is_empty is True
    assert result.input_length == 0


def test_analyzer_with_multiple_sentences():
    analyzer = InputAnalyzer()

    result = analyzer.analyze(
        "Flask is a Python framework. It is lightweight."
    )

    assert result.sentence_count == 2

def test_detects_duplicate_sentences():
    analyzer = InputAnalyzer()

    text = (
        "Flask is used. "
        "Flask is used. "
        "PostgreSQL is used."
    )

    result = analyzer.analyze(text)

    assert result.duplicate_count == 1

def test_no_duplicates():
    analyzer = InputAnalyzer()

    text = (
        "Flask is used. "
        "PostgreSQL is used. "
        "Authentication is required."
    )

    result = analyzer.analyze(text)

    assert result.duplicate_count == 0

def test_analyzer_detects_task_type():
    analyzer = InputAnalyzer()

    result = analyzer.analyze(
        "Why am I getting a 401 error?"
    )

    assert result.task_type == TaskType.DEBUGGING

def test_analyzer_detects_explanation_task():
    analyzer = InputAnalyzer()

    result = analyzer.analyze(
        "Explain what Flask is."
    )

    assert result.task_type == TaskType.EXPLANATION