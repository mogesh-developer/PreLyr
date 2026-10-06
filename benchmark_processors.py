from time import perf_counter

from app.core.engine import PreLyrEngine


text = """Basically, I am building a Flask backend for my application.

Basically, I am building a Flask backend for my application.

The backend needs a PostgreSQL database and a REST API.

The backend needs a PostgreSQL database and a REST API.

I want to understand how Flask handles routes and database requests.

I want to understand how Flask handles routes and database requests."""


engine = PreLyrEngine()


for i in range(5):

    start = perf_counter()

    result = engine.process(text)

    elapsed = (
        perf_counter() - start
    ) * 1000

    print(
        f"Run {i + 1}: "
        f"{elapsed:.2f} ms | "
        f"{result.context.original_tokens} -> "
        f"{result.context.optimized_tokens} tokens"
    )