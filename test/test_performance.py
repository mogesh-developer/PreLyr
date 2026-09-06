import time

from app.core.engine import PreLyrEngine


def measure(engine: PreLyrEngine, text: str) -> float:
    start = time.perf_counter()
    engine.process(text)
    return time.perf_counter() - start


def test_cold_vs_warm_latency():
    text = (
        "Flask is used as the backend. "
        "Flask is the backend framework. "
        "PostgreSQL is used as the database. "
        "The application stores user data in PostgreSQL."
    )

    # Cold: new engine → model may need to load
    cold_engine = PreLyrEngine()

    cold_start = time.perf_counter()
    cold_engine.process(text)
    cold_latency = time.perf_counter() - cold_start

    # Warm: same engine → model should already be loaded
    warm_times = [
        measure(cold_engine, text)
        for _ in range(5)
    ]

    average_warm_latency = sum(warm_times) / len(warm_times)

    print(f"\nCold latency: {cold_latency:.4f}s")
    print(f"Warm latencies: {[round(x, 4) for x in warm_times]}")
    print(f"Average warm latency: {average_warm_latency:.4f}s")

    assert cold_latency > 0
    assert average_warm_latency > 0