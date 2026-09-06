import time

from app.processors.semantic_deduplicator import SemanticDeduplicator


def test_model2vec_cold_vs_warm_latency():
    processor = SemanticDeduplicator()

    text = (
        "The backend uses Flask. "
        "The backend is built using Flask. "
        "The database uses PostgreSQL."
    )

    # Cold start
    start = time.perf_counter()
    processor.process(text)
    cold_time = time.perf_counter() - start

    # Warm runs
    warm_times = []

    for _ in range(3):
        start = time.perf_counter()
        processor.process(text)
        warm_times.append(time.perf_counter() - start)

    average_warm_time = sum(warm_times) / len(warm_times)

    print(f"\nCold start: {cold_time:.4f}s")

    for index, elapsed in enumerate(warm_times, start=1):
        print(f"Warm run {index}: {elapsed:.4f}s")

    print(f"Average warm: {average_warm_time:.4f}s")

    assert cold_time > 0
    assert average_warm_time > 0