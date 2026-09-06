from app.core.task_detector import TaskDetector
from app.models.schemas import TaskType


def test_detects_explanation():
    detector = TaskDetector()

    assert detector.detect("Explain what Flask is.") == TaskType.EXPLANATION


def test_detects_debugging():
    detector = TaskDetector()

    assert (
        detector.detect("Why am I getting a 401 error?")
        == TaskType.DEBUGGING
    )


def test_detects_summarization():
    detector = TaskDetector()

    assert (
        detector.detect("Summarize this document.")
        == TaskType.SUMMARIZATION
    )


def test_detects_extraction():
    detector = TaskDetector()

    assert (
        detector.detect("Extract the deadlines from this document.")
        == TaskType.EXTRACTION
    )


def test_detects_comparison():
    detector = TaskDetector()

    assert (
        detector.detect("Compare Flask vs FastAPI.")
        == TaskType.COMPARISON
    )


def test_detects_generation():
    detector = TaskDetector()

    assert (
        detector.detect("Write a Python function for this.")
        == TaskType.GENERATION
    )


def test_unknown_task():
    detector = TaskDetector()

    assert detector.detect("Flask PostgreSQL Docker.") == TaskType.UNKNOWN


def test_empty_input():
    detector = TaskDetector()

    assert detector.detect("") == TaskType.UNKNOWN