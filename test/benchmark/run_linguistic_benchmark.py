from __future__ import annotations

from collections import defaultdict

from app.nlp.linguistic_optimizer import LinguisticOptimizer

from .linguistic_cases import BENCHMARK_CASES


def run_benchmark() -> None:
    optimizer = LinguisticOptimizer()

    total = len(BENCHMARK_CASES)

    changed = 0
    noop = 0
    preservation_failures = 0
    behavior_failures = 0

    total_original_tokens = 0
    total_optimized_tokens = 0

    category_stats = defaultdict(
        lambda: {
            "total": 0,
            "passed": 0,
            "changed": 0,
            "tokens_before": 0,
            "tokens_after": 0,
        }
    )

    print("\n" + "=" * 75)
    print("PreLyr Counterfactual Linguistic Benchmark")
    print("=" * 75)

    for case in BENCHMARK_CASES:
        result = optimizer.optimize(case.text)

        category = category_stats[case.category]
        category["total"] += 1

        total_original_tokens += result.original_tokens
        total_optimized_tokens += result.optimized_tokens

        category["tokens_before"] += result.original_tokens
        category["tokens_after"] += result.optimized_tokens

        was_changed = result.optimized != result.original

        if was_changed:
            changed += 1
            category["changed"] += 1
        else:
            noop += 1

        behavior_ok = was_changed == case.expect_change

        preservation_ok = all(
            required.lower() in result.optimized.lower()
            for required in case.expected_contains
        )

        removal_ok = all(
            forbidden.lower() not in result.optimized.lower()
            for forbidden in case.expected_not_contains
        )

        if not preservation_ok or not removal_ok:
            preservation_failures += 1

        if not behavior_ok:
            behavior_failures += 1

        passed = (
            behavior_ok
            and preservation_ok
            and removal_ok
        )

        if passed:
            category["passed"] += 1

        status = "PASS" if passed else "FAIL"

        print(f"\n[{status}] {case.name}")
        print(f"Category : {case.category}")
        print(f"Original : {case.text}")
        print(f"Optimized: {result.optimized}")
        print(
            f"Tokens   : "
            f"{result.original_tokens} -> "
            f"{result.optimized_tokens}"
        )

    token_reduction = (
        total_original_tokens
        - total_optimized_tokens
    )

    if total_original_tokens:
        reduction_percentage = (
            token_reduction
            / total_original_tokens
        ) * 100
    else:
        reduction_percentage = 0.0

    print("\n" + "=" * 75)
    print("Overall Summary")
    print("=" * 75)

    print(f"Total cases              : {total}")
    print(f"Changed cases            : {changed}")
    print(f"NO_OP cases              : {noop}")
    print(f"Behavior failures        : {behavior_failures}")
    print(f"Preservation failures    : {preservation_failures}")
    print(
        f"Total tokens             : "
        f"{total_original_tokens} -> "
        f"{total_optimized_tokens}"
    )
    print(f"Token reduction          : {token_reduction}")
    print(
        f"Token reduction %        : "
        f"{reduction_percentage:.2f}%"
    )

    print("\n" + "=" * 75)
    print("Category Metrics")
    print("=" * 75)

    for category_name, stats in category_stats.items():
        category_total = stats["total"]

        accuracy = (
            stats["passed"] / category_total
        ) * 100

        category_reduction = (
            stats["tokens_before"]
            - stats["tokens_after"]
        )

        print(
            f"{category_name:<20} "
            f"{stats['passed']}/{category_total} "
            f"({accuracy:6.2f}%) | "
            f"tokens "
            f"{stats['tokens_before']} -> "
            f"{stats['tokens_after']} | "
            f"reduction {category_reduction}"
        )

    print("=" * 75)


if __name__ == "__main__":
    run_benchmark()