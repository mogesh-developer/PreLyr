import os
import time

from app.core.engine import PreLyrEngine
from app.llm.glm import GLMProvider


CASES = [
    (
        "Clean Input",
        "Explain what Flask is.",
    ),
    (
        "Exact Redundancy",
        (
            "Flask is a Python web framework. "
            "Flask is a Python web framework. "
            "Flask is easy to use."
        ),
    ),
    (
        "Semantic Redundancy",
        (
            "The Flask API returns a 500 error. "
            "The Flask API is returning an HTTP 500 error. "
            "The database connection fails. "
            "The database connection is failing. "
            "The server uses port 5000."
        ),
    ),
    (
        "Heavy Redundancy",
        (
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
    ),
    (
        "Debugging Input",
        (
            "The Flask API returns a 500 error. "
            "The database connection fails. "
            "The same error appears repeatedly."
        ),
    ),
]


def format_seconds(milliseconds: float) -> str:
    seconds = milliseconds / 1000

    if seconds < 1:
        return f"{milliseconds:.2f} ms"

    return f"{seconds:.2f} s"


def run_direct(provider: GLMProvider, text: str):
    start = time.perf_counter()

    response = provider.generate(
        f"""
Answer the user's request accurately.

User request:
{text}
"""
    )

    latency_ms = (
        time.perf_counter() - start
    ) * 1000

    return response, latency_ms


def run_prelyr(engine: PreLyrEngine, text: str):
    total_start = time.perf_counter()

    # -----------------------------
    # PreLyr processing
    # -----------------------------
    preprocessing_start = time.perf_counter()

    result = engine.process(text)

    preprocessing_ms = (
        time.perf_counter() - preprocessing_start
    ) * 1000

    # -----------------------------
    # Optimized prompt
    # -----------------------------
    optimized_prompt = f"""
You are receiving context prepared by PreLyr.

Use the following context to answer the user's request.

--- Optimized Context ---
{result.context.optimized_text}
--- End Context ---

Answer the user's request accurately.
"""

    # -----------------------------
    # LLM
    # -----------------------------
    llm_start = time.perf_counter()

    response = engine.llm_provider.generate(
        optimized_prompt
    )

    llm_latency_ms = (
        time.perf_counter() - llm_start
    ) * 1000

    # -----------------------------
    # Total
    # -----------------------------
    total_latency_ms = (
        time.perf_counter() - total_start
    ) * 1000

    return {
        "response": response,
        "preprocessing_ms": preprocessing_ms,
        "llm_latency_ms": llm_latency_ms,
        "total_latency_ms": total_latency_ms,
        "original_tokens": result.context.original_tokens,
        "optimized_tokens": result.context.optimized_tokens,
        "token_reduction": (
            result.context.token_reduction_percentage
        ),
        "operations": [
            operation.value
            for operation in result.context.operations_applied
        ],
    }


def print_case_result(
    name: str,
    direct_latency: float,
    prelyr_result: dict,
):
    total_latency = prelyr_result["total_latency_ms"]

    time_difference = (
        direct_latency - total_latency
    )

    if direct_latency > 0:
        time_change_percentage = (
            time_difference / direct_latency
        ) * 100
    else:
        time_change_percentage = 0.0

    print()
    print(f"[{name}]")
    print("-" * 70)

    print(
        f"Original tokens       : "
        f"{prelyr_result['original_tokens']}"
    )

    print(
        f"Optimized tokens      : "
        f"{prelyr_result['optimized_tokens']}"
    )

    print(
        f"Token reduction       : "
        f"{prelyr_result['token_reduction']:.2f}%"
    )

    print()

    print(
        f"Direct LLM latency    : "
        f"{format_seconds(direct_latency)}"
    )

    print(
        f"PreLyr processing     : "
        f"{format_seconds(prelyr_result['preprocessing_ms'])}"
    )

    print(
        f"PreLyr LLM latency    : "
        f"{format_seconds(prelyr_result['llm_latency_ms'])}"
    )

    print(
        f"PreLyr total latency  : "
        f"{format_seconds(total_latency)}"
    )

    print()

    if time_difference > 0:
        print(
            f"Time saved            : "
            f"{format_seconds(time_difference)}"
        )
    elif time_difference < 0:
        print(
            f"Additional time       : "
            f"{format_seconds(abs(time_difference))}"
        )
    else:
        print(
            "Time difference       : "
            "0.00 ms"
        )

    print(
        f"Time change           : "
        f"{time_change_percentage:.2f}%"
    )

    print(
        f"Operations            : "
        f"{', '.join(prelyr_result['operations'])}"
    )


def main():
    if not os.getenv("GLM_API_KEY"):
        raise RuntimeError(
            "GLM_API_KEY is not configured."
        )

    provider = GLMProvider()
    engine = PreLyrEngine(
        llm_provider=provider
    )

    results = []

    print()
    print("=" * 70)
    print(
        "PRELYR V1 — GLM-4.5-FLASH "
        "REAL LLM BENCHMARK"
    )
    print("=" * 70)

    print()
    print(
        "Comparing:"
    )
    print(
        "  Direct LLM"
    )
    print(
        "      VS"
    )
    print(
        "  PreLyr → LLM"
    )

    # =========================================================
    # CASES
    # =========================================================

    for name, text in CASES:

        print()
        print(f"[{name}]")
        print("-" * 70)

        # -----------------------------------------------------
        # Direct LLM
        # -----------------------------------------------------

        try:
            print("Running Direct LLM...")

            direct_response, direct_latency = run_direct(
                provider,
                text,
            )

            print(
                f"Direct completed in "
                f"{format_seconds(direct_latency)}"
            )

        except Exception as exc:
            print(
                "Direct LLM FAILED:"
            )
            print(
                f"{type(exc).__name__}: {exc}"
            )

            results.append(
                {
                    "name": name,
                    "status": "FAILED",
                    "error": (
                        f"Direct LLM: {exc}"
                    ),
                }
            )

            continue

        # -----------------------------------------------------
        # PreLyr → LLM
        # -----------------------------------------------------

        try:
            print("Running PreLyr → LLM...")

            prelyr_result = run_prelyr(
                engine,
                text,
            )

            print(
                f"PreLyr completed in "
                f"{format_seconds(prelyr_result['total_latency_ms'])}"
            )

        except Exception as exc:
            print(
                "PreLyr → LLM FAILED:"
            )
            print(
                f"{type(exc).__name__}: {exc}"
            )

            results.append(
                {
                    "name": name,
                    "status": "FAILED",
                    "error": (
                        f"PreLyr → LLM: {exc}"
                    ),
                }
            )

            continue

        # -----------------------------------------------------
        # Print result
        # -----------------------------------------------------

        print_case_result(
            name,
            direct_latency,
            prelyr_result,
        )

        # -----------------------------------------------------
        # Store benchmark result
        # -----------------------------------------------------

        total_latency = (
            prelyr_result["total_latency_ms"]
        )

        time_difference = (
            direct_latency - total_latency
        )

        if direct_latency > 0:
            time_change_percentage = (
                time_difference
                / direct_latency
            ) * 100
        else:
            time_change_percentage = 0.0

        results.append(
            {
                "name": name,
                "status": "PASSED",
                "direct_ms": direct_latency,
                "prelyr_ms": total_latency,
                "preprocessing_ms": (
                    prelyr_result[
                        "preprocessing_ms"
                    ]
                ),
                "original_tokens": (
                    prelyr_result[
                        "original_tokens"
                    ]
                ),
                "optimized_tokens": (
                    prelyr_result[
                        "optimized_tokens"
                    ]
                ),
                "token_reduction": (
                    prelyr_result[
                        "token_reduction"
                    ]
                ),
                "time_difference_ms": (
                    time_difference
                ),
                "time_change_percentage": (
                    time_change_percentage
                ),
                "operations": (
                    prelyr_result[
                        "operations"
                    ]
                ),
            }
        )

        # -----------------------------------------------------
        # Responses
        # -----------------------------------------------------

        print()
        print("Direct response:")
        print(
            direct_response[:300]
        )

        print()
        print("PreLyr response:")
        print(
            prelyr_result[
                "response"
            ][:300]
        )

    # =========================================================
    # SUMMARY
    # =========================================================

    print()
    print("=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)

    print()

    print(
        f"{'Case':<24}"
        f"{'Direct':>12}"
        f"{'PreLyr':>12}"
        f"{'Saved':>12}"
        f"{'Change':>10}"
    )

    print("-" * 70)

    passed_results = []

    for result in results:

        if result["status"] != "PASSED":
            print(
                f"{result['name']:<24}"
                f"{'FAILED':>12}"
            )
            continue

        passed_results.append(result)

        direct = format_seconds(
            result["direct_ms"]
        )

        prelyr = format_seconds(
            result["prelyr_ms"]
        )

        difference = result[
            "time_difference_ms"
        ]

        if difference >= 0:
            saved = format_seconds(
                difference
            )
        else:
            saved = (
                "+"
                + format_seconds(
                    abs(difference)
                )
            )

        change = (
            f"{result['time_change_percentage']:.2f}%"
        )

        print(
            f"{result['name']:<24}"
            f"{direct:>12}"
            f"{prelyr:>12}"
            f"{saved:>12}"
            f"{change:>10}"
        )

    # =========================================================
    # Overall statistics
    # =========================================================

    print()
    print("-" * 70)

    if passed_results:

        total_direct = sum(
            result["direct_ms"]
            for result in passed_results
        )

        total_prelyr = sum(
            result["prelyr_ms"]
            for result in passed_results
        )

        total_difference = (
            total_direct - total_prelyr
        )

        if total_direct > 0:
            overall_change = (
                total_difference
                / total_direct
            ) * 100
        else:
            overall_change = 0.0

        average_token_reduction = (
            sum(
                result["token_reduction"]
                for result in passed_results
            )
            / len(passed_results)
        )

        print(
            f"Total Direct LLM time : "
            f"{format_seconds(total_direct)}"
        )

        print(
            f"Total PreLyr time     : "
            f"{format_seconds(total_prelyr)}"
        )

        if total_difference >= 0:
            print(
                f"Total time saved      : "
                f"{format_seconds(total_difference)}"
            )
        else:
            print(
                f"Total additional time : "
                f"{format_seconds(abs(total_difference))}"
            )

        print(
            f"Overall time change   : "
            f"{overall_change:.2f}%"
        )

        print(
            f"Average token reduction: "
            f"{average_token_reduction:.2f}%"
        )

    # =========================================================
    # Failed cases
    # =========================================================

    failed_results = [
        result
        for result in results
        if result["status"] == "FAILED"
    ]

    print()

    print(
        f"Passed cases          : "
        f"{len(passed_results)}"
    )

    print(
        f"Failed cases          : "
        f"{len(failed_results)}"
    )

    print()
    print("=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()