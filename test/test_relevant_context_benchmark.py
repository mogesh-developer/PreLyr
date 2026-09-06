import pytest

from app.models.schemas import TaskType
from app.processors.relevant_context import RelevantContextProcessor


@pytest.fixture
def processor():
    return RelevantContextProcessor()


CASES = [
    {
        "name": "debugging",
        "task": TaskType.DEBUGGING,
        "text": (
            "The application uses Flask as the backend. "
            "The frontend is built with React. "
            "The API returns a 500 error. "
            "The database connection failed. "
            "The server runs on port 8000. "
            "The application was deployed yesterday."
        ),
        "must_keep": [
            "500 error",
            "database connection failed",
        ],
    },
    {
        "name": "explanation",
        "task": TaskType.EXPLANATION,
        "text": (
            "Flask is used as the backend framework. "
            "The application has a PostgreSQL database. "
            "Flask is popular because it is lightweight. "
            "The frontend uses React. "
            "The deployment runs on AWS."
        ),
        "must_keep": [
            "Flask is popular because it is lightweight",
        ],
    },
    {
        "name": "extraction",
        "task": TaskType.EXTRACTION,
        "text": (
            "The project is called PreLyr. "
            "The submission deadline is September 30. "
            "The team must provide a technical report. "
            "The backend uses Flask. "
            "The contact email is team@example.com."
        ),
        "must_keep": [
            "submission deadline",
            "technical report",
            "contact email",
        ],
    },
    {
        "name": "comparison",
        "task": TaskType.COMPARISON,
        "text": (
            "Flask is lightweight and simple. "
            "FastAPI provides better async support. "
            "Flask has a large ecosystem. "
            "FastAPI can provide better performance. "
            "The application is deployed on Linux."
        ),
        "must_keep": [
            "lightweight and simple",
            "better async support",
            "large ecosystem",
            "better performance",
        ],
    },
    {
        "name": "generation",
        "task": TaskType.GENERATION,
        "text": (
            "The application uses Flask. "
            "The new API must support authentication. "
            "The system should provide structured JSON output. "
            "PostgreSQL stores application data. "
            "The new feature needs error handling."
        ),
        "must_keep": [
            "must support authentication",
            "structured JSON output",
            "needs error handling",
        ],
    },
]


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
def test_relevant_context_preserves_task_critical_information(
    processor,
    case,
):
    result = processor.process(
        case["text"],
        case["task"],
    )

    print(f"\n--- {case['name']} ---")
    print("Task:", case["task"])
    print("Original:", case["text"])
    print("Selected:", result)

    for required in case["must_keep"]:
        assert required.casefold() in result.casefold()


def test_unknown_task_preserves_all_context(processor):
    text = (
        "Flask is used as the backend. "
        "PostgreSQL stores application data. "
        "The server runs on port 8000."
    )

    result = processor.process(text, TaskType.UNKNOWN)

    assert result == text


def test_short_input_is_not_filtered(processor):
    text = (
        "The API returns a 500 error. "
        "The database connection failed."
    )

    result = processor.process(text, TaskType.DEBUGGING)

    assert result == text