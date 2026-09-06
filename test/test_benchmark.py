import time
from app.core.engine import PreLyrEngine
from app.models.schemas import ProcessingOperation


def test_prelyr_benchmark_cases():
    engine = PreLyrEngine()

    cases = [
        {
            "name": "clean_short",
            "text": "Explain what Flask is.",
            "expected_operation": ProcessingOperation.NO_OP,
        },
        {
            "name": "duplicate_content",
            "text": (
                "The backend uses Flask. "
                "The backend uses Flask. "
                "The database uses PostgreSQL."
            ),
            "expected_operation": ProcessingOperation.DEDUPLICATE,
        },
        {
            "name": "long_debugging",
            "text": (
                "The application started successfully. "
                "The frontend loaded successfully. "
                "The server returned a 401 error. "
                "Authentication failed because the token was invalid. "
                "The development server is running on port 8000. "
                "The database connection was successful."
            ),
            "expected_operation": ProcessingOperation.SELECT_RELEVANT_CONTEXT,
        },
    ]

    for case in cases:
        start = time.perf_counter()

        result = engine.process(case["text"])

        elapsed = time.perf_counter() - start

        print(f"\n{case['name']}: {elapsed:.2f}s")


        assert (
            case["expected_operation"]
            in result.decision.operations
        )

        assert result.context.original_tokens > 0
        assert result.context.optimized_tokens > 0

        assert (
            result.context.optimized_tokens
            <= result.context.original_tokens
        )