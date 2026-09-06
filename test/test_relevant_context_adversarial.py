import pytest

from app.models.schemas import TaskType
from app.processors.relevant_context import RelevantContextProcessor


@pytest.fixture
def processor():
    return RelevantContextProcessor()


CASES = [
    {
        "name": "debugging_semantic_cause",
        "task": TaskType.DEBUGGING,
        "text": (
            "The API returns a 500 error. "
            "The connection configuration was changed during the database migration. "
            "The frontend uses React. "
            "The application is deployed on AWS."
        ),
        "must_keep": [
            "500 error",
            "connection configuration was changed during the database migration",
        ],
    },
    {
        "name": "debugging_technical_cause",
        "task": TaskType.DEBUGGING,
        "text": (
            "The service fails during startup. "
            "The database connection string points to the old hostname. "
            "The application uses Flask. "
            "The frontend uses React."
        ),
        "must_keep": [
            "service fails during startup",
            "database connection string points to the old hostname",
        ],
    },
    {
        "name": "explanation_semantic_reason",
        "task": TaskType.EXPLANATION,
        "text": (
            "Flask is used by the application. "
            "It was selected because the project needs a lightweight web framework. "
            "The frontend uses React. "
            "The database is PostgreSQL."
        ),
        "must_keep": [
            "selected because the project needs a lightweight web framework",
        ],
    },
    {
        "name": "comparison_without_explicit_keywords",
        "task": TaskType.COMPARISON,
        "text": (
            "Flask requires less setup for this application. "
            "FastAPI requires more configuration but provides native async support. "
            "Both frameworks support Python. "
            "The application uses PostgreSQL."
        ),
        "must_keep": [
            "Flask requires less setup",
            "FastAPI requires more configuration",
        ],
    },
    {
        "name": "generation_hidden_constraint",
        "task": TaskType.GENERATION,
        "text": (
            "The new API must support authentication. "
            "Authentication is required because the application handles private user data. "
            "The backend uses Flask. "
            "The database is PostgreSQL."
        ),
        "must_keep": [
            "must support authentication",
            "required because the application handles private user data",
        ],
    },
    {
        "name": "extraction_contextual_fact",
        "task": TaskType.EXTRACTION,
        "text": (
            "The project will be submitted at the end of September. "
            "The exact submission date is September 30. "
            "The report must include architecture and testing sections. "
            "The backend uses Flask."
        ),
        "must_keep": [
            "exact submission date is September 30",
            "report must include architecture and testing sections",
        ],
    },
]


@pytest.mark.parametrize(
    "case",
    CASES,
    ids=lambda case: case["name"],
)
def test_adversarial_relevance_preservation(processor, case):
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