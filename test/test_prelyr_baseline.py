import time

import pytest

from app.core.engine import PreLyrEngine


@pytest.fixture(scope="module")
def engine():
    return PreLyrEngine()


CASES = [
    (
        "clean",
        "Explain what Flask is.",
    ),
    (
        "exact_redundancy",
        (
            "Flask is used as the backend. "
            "PostgreSQL is used as the database. "
            "Flask is used as the backend. "
            "PostgreSQL is used as the database."
        ),
    ),
    (
        "semantic_redundancy",
        (
            "Flask is used as the backend. "
            "The backend application is built with Flask. "
            "PostgreSQL is used as the database. "
            "The database is PostgreSQL. "
            "The server runs on port 5000. "
            "The server runs on port 8000."
        ),
    ),
    (
        "heavy_redundancy",
        " ".join(
            [
                "Flask is used as the backend."
                for _ in range(10)
            ]
        ),
    ),
    (
        "debugging",
        (
            "The Flask API returns a 500 error. "
            "The database connection fails. "
            "The same error appears repeatedly. "
            "The database connection fails."
        ),
    ),
]


def test_prelyr_baseline(engine):
    print("\n")
    print("=" * 80)
    print("PRELYR V1 BASELINE")
    print("=" * 80)

    for name, text in CASES:
        start = time.perf_counter()

        result = engine.process(text)

        latency = time.perf_counter() - start

        print(f"\n[{name}]")
        print(f"Operations : {result.decision.operations}")
        print(f"Original   : {result.context.original_tokens} tokens")
        print(f"Optimized  : {result.context.optimized_tokens} tokens")
        print(
            f"Reduction  : "
            f"{result.context.token_reduction_percentage:.2f}%"
        )
        print(f"Latency    : {latency * 1000:.2f} ms")
        print(f"Task       : {result.analysis.task_type}")
        print(f"Output     : {result.context.optimized_text}")

        assert result.context.optimized_text
        assert result.context.optimized_tokens <= result.context.original_tokens