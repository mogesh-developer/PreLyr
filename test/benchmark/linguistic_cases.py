from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkCase:
    name: str
    category: str
    text: str
    expected_contains: tuple[str, ...] = ()
    expected_not_contains: tuple[str, ...] = ()
    expect_change: bool = False


BENCHMARK_CASES = [

    # ==========================================================
    # SAFE REMOVAL
    # ==========================================================

    BenchmarkCase(
        name="safe_actually",
        category="SAFE_REMOVAL",
        text="I am actually trying to fix this error.",
        expect_change=True,
    ),
    BenchmarkCase(
        name="safe_basically",
        category="SAFE_REMOVAL",
        text="Basically, I need to update the API.",
        expect_change=True,
    ),
    BenchmarkCase(
        name="safe_really",
        category="SAFE_REMOVAL",
        text="I really need to restart the server.",
        expect_change=True,
    ),
    BenchmarkCase(
        name="safe_multiple_fillers",
        category="SAFE_REMOVAL",
        text="Basically, I am actually trying to fix this.",
        expect_change=True,
    ),
    BenchmarkCase(
        name="safe_in_order_to",
        category="SAFE_REMOVAL",
        text="I use this method in order to test the API.",
        expect_change=True,
    ),
    BenchmarkCase(
        name="safe_verbose_causal",
        category="SAFE_REMOVAL",
        text="The request failed due to the fact that the API was unavailable.",
        expect_change=True,
    ),
    BenchmarkCase(
        name="safe_verbose_temporal",
        category="SAFE_REMOVAL",
        text="At this point in time, the server is running.",
        expect_change=True,
    ),
    BenchmarkCase(
        name="safe_repeated_basic",
        category="SAFE_REMOVAL",
        text="Basically, I need to test this. Basically, I need to deploy it.",
        expect_change=True,
    ),
    BenchmarkCase(
        name="safe_filler_middle",
        category="SAFE_REMOVAL",
        text="The application is actually using Flask.",
        expect_change=True,
    ),
    BenchmarkCase(
        name="safe_filler_end",
        category="SAFE_REMOVAL",
        text="The server is running really well.",
        expect_change=True,
    ),

    # ==========================================================
    # NO_OP
    # ==========================================================

    BenchmarkCase(
        name="noop_flask",
        category="NO_OP",
        text="Explain how Flask routing works.",
        expect_change=False,
    ),
    BenchmarkCase(
        name="noop_python",
        category="NO_OP",
        text="How do I create a virtual environment in Python?",
        expect_change=False,
    ),
    BenchmarkCase(
        name="noop_database",
        category="NO_OP",
        text="The application uses PostgreSQL for persistence.",
        expect_change=False,
    ),
    BenchmarkCase(
        name="noop_api",
        category="NO_OP",
        text="Explain how REST APIs work.",
        expect_change=False,
    ),
    BenchmarkCase(
        name="noop_clean_requirement",
        category="NO_OP",
        text="The backend must expose a health check endpoint.",
        expect_change=False,
    ),
    BenchmarkCase(
        name="noop_short",
        category="NO_OP",
        text="Fix the authentication bug.",
        expect_change=False,
    ),
    BenchmarkCase(
        name="noop_question",
        category="NO_OP",
        text="Why is the database connection failing?",
        expect_change=False,
    ),
    BenchmarkCase(
        name="noop_code_context",
        category="NO_OP",
        text="The Docker container exposes port 8000.",
        expect_change=False,
    ),
    BenchmarkCase(
        name="noop_architecture",
        category="NO_OP",
        text="The frontend communicates with the backend through an API.",
        expect_change=False,
    ),
    BenchmarkCase(
        name="noop_constraint",
        category="NO_OP",
        text="The service requires PostgreSQL and Redis.",
        expect_change=False,
    ),

    # ==========================================================
    # SENSITIVE / CONSTRAINT PRESERVATION
    # ==========================================================

    BenchmarkCase(
        name="sensitive_negation",
        category="SENSITIVE",
        text="The Flask backend is not running.",
        expected_contains=("not", "Flask"),
        expect_change=False,
    ),
    BenchmarkCase(
        name="sensitive_never",
        category="SENSITIVE",
        text="The service should never expose the database publicly.",
        expected_contains=("never", "database"),
        expect_change=False,
    ),
    BenchmarkCase(
        name="sensitive_only",
        category="SENSITIVE",
        text="Only administrators can access this endpoint.",
        expected_contains=("Only", "administrators"),
        expect_change=False,
    ),
    BenchmarkCase(
        name="sensitive_must",
        category="SENSITIVE",
        text="The API must use HTTPS.",
        expected_contains=("must", "HTTPS"),
        expect_change=False,
    ),
    BenchmarkCase(
        name="sensitive_required",
        category="SENSITIVE",
        text="Authentication is required for every request.",
        expected_contains=("required",),
        expect_change=False,
    ),
    BenchmarkCase(
        name="sensitive_minimum",
        category="SENSITIVE",
        text="The system requires a minimum of 3 replicas.",
        expected_contains=("minimum", "3"),
        expect_change=False,
    ),
    BenchmarkCase(
        name="sensitive_maximum",
        category="SENSITIVE",
        text="The request size must be at most 10 MB.",
        expected_contains=("at most", "10"),
        expect_change=False,
    ),
    BenchmarkCase(
        name="sensitive_exact",
        category="SENSITIVE",
        text="The system must return exactly 5 results.",
        expected_contains=("exactly", "5"),
        expect_change=False,
    ),
    BenchmarkCase(
        name="sensitive_number",
        category="SENSITIVE",
        text="The server is running on port 8000.",
        expected_contains=("8000",),
        expect_change=False,
    ),
    BenchmarkCase(
        name="sensitive_without",
        category="SENSITIVE",
        text="The application must work without Redis.",
        expected_contains=("without", "Redis"),
        expect_change=False,
    ),

    # ==========================================================
    # TECHNICAL / CODE CONTEXT
    # ==========================================================

    BenchmarkCase(
        name="technical_flask",
        category="TECHNICAL",
        text="The Flask backend connects to PostgreSQL.",
        expected_contains=("Flask", "PostgreSQL"),
        expect_change=False,
    ),
    BenchmarkCase(
        name="technical_fastapi",
        category="TECHNICAL",
        text="The FastAPI service exposes the REST API.",
        expected_contains=("FastAPI", "API"),
        expect_change=False,
    ),
    BenchmarkCase(
        name="technical_docker",
        category="TECHNICAL",
        text="The application runs inside Docker.",
        expected_contains=("Docker",),
        expect_change=False,
    ),
    BenchmarkCase(
        name="technical_kubernetes",
        category="TECHNICAL",
        text="Kubernetes manages the application containers.",
        expected_contains=("Kubernetes",),
        expect_change=False,
    ),
    BenchmarkCase(
        name="technical_redis",
        category="TECHNICAL",
        text="Redis stores temporary session data.",
        expected_contains=("Redis",),
        expect_change=False,
    ),
    BenchmarkCase(
        name="technical_mongodb",
        category="TECHNICAL",
        text="The service stores documents in MongoDB.",
        expected_contains=("MongoDB",),
        expect_change=False,
    ),
    BenchmarkCase(
        name="technical_python",
        category="TECHNICAL",
        text="The application is written in Python.",
        expected_contains=("Python",),
        expect_change=False,
    ),
    BenchmarkCase(
        name="technical_llm",
        category="TECHNICAL",
        text="The pipeline sends optimized context to an LLM.",
        expected_contains=("LLM",),
        expect_change=False,
    ),
    BenchmarkCase(
        name="technical_database",
        category="TECHNICAL",
        text="The backend requires a database connection.",
        expected_contains=("backend", "database"),
        expect_change=False,
    ),
    BenchmarkCase(
        name="technical_prelyr",
        category="TECHNICAL",
        text="PreLyr optimizes context before sending it to an LLM.",
        expected_contains=("PreLyr", "LLM"),
        expect_change=False,
    ),

    # ==========================================================
    # MULTI-CANDIDATE / REPETITION
    # ==========================================================

    BenchmarkCase(
        name="multi_two_fillers",
        category="MULTI_CANDIDATE",
        text="I am actually basically trying to fix this error.",
        expect_change=True,
    ),
    BenchmarkCase(
        name="multi_repeated",
        category="MULTI_CANDIDATE",
        text=(
            "Basically, I am trying to fix this. "
            "Basically, I need to test it."
        ),
        expect_change=True,
    ),
    BenchmarkCase(
        name="multi_three_fillers",
        category="MULTI_CANDIDATE",
        text=(
            "Basically, I am actually really trying "
            "to fix this error."
        ),
        expect_change=True,
    ),
    BenchmarkCase(
        name="multi_verbose_phrases",
        category="MULTI_CANDIDATE",
        text=(
            "I use this method in order to test the API "
            "due to the fact that the endpoint is unstable."
        ),
        expect_change=True,
    ),
    BenchmarkCase(
        name="multi_middle_candidates",
        category="MULTI_CANDIDATE",
        text=(
            "The backend is actually running and "
            "the frontend is basically working."
        ),
        expect_change=True,
    ),
    BenchmarkCase(
        name="multi_sentence_candidates",
        category="MULTI_CANDIDATE",
        text=(
            "Actually, the server works. "
            "Basically, the database works."
        ),
        expect_change=True,
    ),
    BenchmarkCase(
        name="multi_repeated_phrase",
        category="MULTI_CANDIDATE",
        text=(
            "I use this method in order to test it. "
            "I use this method in order to validate it."
        ),
        expect_change=True,
    ),
    BenchmarkCase(
        name="multi_mixed",
        category="MULTI_CANDIDATE",
        text=(
            "Basically, the API is actually "
            "ready in order to test."
        ),
        expect_change=True,
    ),
    BenchmarkCase(
        name="multi_repeated_filler",
        category="MULTI_CANDIDATE",
        text=(
            "Really, this is useful. "
            "Really, this is necessary."
        ),
        expect_change=True,
    ),
    BenchmarkCase(
        name="multi_complex",
        category="MULTI_CANDIDATE",
        text=(
            "Basically, I am actually trying to "
            "fix this in order to deploy it."
        ),
        expect_change=True,
    ),

    # ==========================================================
    # TRICKY / SHOULD REJECT
    # ==========================================================

    BenchmarkCase(
        name="tricky_negation",
        category="TRICKY_REJECT",
        text="The server is not actually running.",
        expected_contains=("not",),
        expect_change=True,
    ),
    BenchmarkCase(
        name="tricky_only",
        category="TRICKY_REJECT",
        text="Only administrators can actually access the API.",
        expected_contains=("Only", "administrators"),
        expect_change=True,
    ),
    BenchmarkCase(
        name="tricky_number",
        category="TRICKY_REJECT",
        text="The server is actually running on port 8000.",
        expected_contains=("8000",),
        expect_change=True,
    ),
    BenchmarkCase(
        name="tricky_technical",
        category="TRICKY_REJECT",
        text="The Flask backend is actually running.",
        expected_contains=("Flask", "backend"),
        expect_change=True,
    ),
    BenchmarkCase(
        name="tricky_constraint",
        category="TRICKY_REJECT",
        text="The API must actually use PostgreSQL.",
        expected_contains=("must", "PostgreSQL"),
        expect_change=True,
    ),
    BenchmarkCase(
        name="tricky_without",
        category="TRICKY_REJECT",
        text="The application actually works without Redis.",
        expected_contains=("without", "Redis"),
        expect_change=True,
    ),
    BenchmarkCase(
        name="tricky_exact",
        category="TRICKY_REJECT",
        text="The API actually returns exactly 5 results.",
        expected_contains=("exactly", "5"),
        expect_change=True,
    ),
    BenchmarkCase(
        name="tricky_minimum",
        category="TRICKY_REJECT",
        text="The system actually requires a minimum of 3 replicas.",
        expected_contains=("minimum", "3"),
        expect_change=True,
    ),
    BenchmarkCase(
        name="tricky_pronouns",
        category="TRICKY_REJECT",
        text="She is actually responsible for the deployment.",
        expected_contains=("She",),
        expect_change=True,
    ),
    BenchmarkCase(
        name="tricky_temporal",
        category="TRICKY_REJECT",
        text="The service is currently running in production.",
        expected_contains=("currently",),
        expect_change=False,
    ),
]