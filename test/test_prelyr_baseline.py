import time

from app.core.engine import PreLyrEngine
from app.models.schemas import ProcessingOperation


CASES = [
    {
        "name": "Clean Input",
        "text": "Explain what Flask is.",
        "expected_operation": ProcessingOperation.NO_OP,
    },
    {
        "name": "Exact Redundancy",
        "text": (
            "Flask is a Python web framework. "
            "Flask is a Python web framework. "
            "Flask is easy to use."
        ),
        "expected_operation": ProcessingOperation.DEDUPLICATE,
    },
    {
        "name": "Semantic Redundancy",
        "text": (
            "The Flask API returns a 500 error. "
            "The Flask API is returning an HTTP 500 error. "
            "The database connection fails. "
            "The database connection is failing. "
            "The server uses port 5000."
        ),
        "expected_operation": ProcessingOperation.DEDUPLICATE,
    },
    {
        "name": "Heavy Redundancy",
        "text": (
            "The application uses Flask. "
            "The application uses Flask. "
            "The application uses Flask. "
            "The application uses Flask. "
            "The application uses Flask. "
            "The application uses Flask. "
            "The application uses Flask. "
            "The application uses Flask. "
            "The application uses Flask."
        ),
        "expected_operation": ProcessingOperation.DEDUPLICATE,
    },
    {
        "name": "Debugging Input",
        "text": (
            "The Flask API returns a 500 error. "
            "The database connection fails. "
            "The same error appears repeatedly."
        ),
        "expected_operation": ProcessingOperation.STRUCTURE,
    },
]


def run_benchmark():
    engine = PreLyrEngine()

    print()
    print("=" * 70)
    print("PRELYR V1 — BEFORE vs AFTER BENCHMARK")
    print("=" * 70)

    results = []

    for case in CASES:
        start = time.perf_counter()

        result = engine.process(case["text"])

        latency_ms = (time.perf_counter() - start) * 1000

        operations = result.context.operations_applied

        benchmark_result = {
            "name": case["name"],
            "original_tokens": result.context.original_tokens,
            "optimized_tokens": result.context.optimized_tokens,
            "reduction": result.context.token_reduction_percentage,
            "latency_ms": latency_ms,
            "operations": operations,
            "optimized_text": result.context.optimized_text,
        }

        results.append(benchmark_result)

        print()
        print(f"[{case['name']}]")
        print("-" * 70)
        print(
            f"Original tokens : "
            f"{result.context.original_tokens}"
        )
        print(
            f"Optimized tokens: "
            f"{result.context.optimized_tokens}"
        )
        print(
            f"Token reduction : "
            f"{result.context.token_reduction_percentage:.2f}%"
        )
        print(
            f"Latency         : "
            f"{latency_ms:.2f} ms"
        )
        print(
            f"Operations      : "
            f"{[operation.value for operation in operations]}"
        )
        print(
            f"Optimized text  : "
            f"{result.context.optimized_text}"
        )

    print()
    print("=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)

    total_original = sum(
        result["original_tokens"]
        for result in results
    )

    total_optimized = sum(
        result["optimized_tokens"]
        for result in results
    )

    total_reduction = (
        (total_original - total_optimized)
        / total_original
        * 100
        if total_original
        else 0
    )

    average_latency = (
        sum(result["latency_ms"] for result in results)
        / len(results)
    )

    print(f"Total original tokens : {total_original}")
    print(f"Total optimized tokens: {total_optimized}")
    print(f"Overall reduction     : {total_reduction:.2f}%")
    print(f"Average latency       : {average_latency:.2f} ms")
    print("=" * 70)
    print()


def test_v1_benchmark_runs():
    engine = PreLyrEngine()

    for case in CASES:
        result = engine.process(case["text"])

        assert result.context.original_text == case["text"]
        assert result.context.optimized_text

        assert result.context.original_tokens >= 0
        assert result.context.optimized_tokens >= 0

        assert -100 <= result.context.token_reduction_percentage <= 100

        assert case["expected_operation"] in (
            result.context.operations_applied
        )



def test_clean_input_has_no_unnecessary_reduction():
    engine = PreLyrEngine()

    text = "Explain what Flask is."

    result = engine.process(text)

    assert result.context.optimized_text == text
    assert result.context.token_reduction_percentage == 0
    assert result.context.operations_applied == [
        ProcessingOperation.NO_OP
    ]


def test_redundant_input_reduces_tokens():
    engine = PreLyrEngine()

    text = (
        "Flask is a Python web framework. "
        "Flask is a Python web framework. "
        "Flask is easy to use."
    )

    result = engine.process(text)

    assert (
        result.context.optimized_tokens
        < result.context.original_tokens
    )

    assert (
        ProcessingOperation.DEDUPLICATE
        in result.context.operations_applied
    )


def test_debugging_context_preserves_error_information():
    engine = PreLyrEngine()

    text = (
        "The Flask API returns a 500 error. "
        "The database connection fails. "
        "The same error appears repeatedly."
    )

    result = engine.process(text)

    optimized = result.context.optimized_text

    assert "500" in optimized
    assert "database" in optimized
    assert "fails" in optimized


if __name__ == "__main__":
    run_benchmark()