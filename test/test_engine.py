from app.core.engine import PreLyrEngine
from app.models.schemas import ProcessingOperation


def test_clean_input_passes_through():
    engine = PreLyrEngine()

    result = engine.process("Explain what Flask is.")

    assert result.analysis.is_empty is False
    assert result.decision.operations == [ProcessingOperation.NO_OP]
    assert result.context.original_text == "Explain what Flask is."
    assert result.context.optimized_text == "Explain what Flask is."


def test_long_input_gets_structure_decision():
    engine = PreLyrEngine()

    text = " ".join(
        ["This is a project requirement."] * 20
    )

    result = engine.process(text)

    assert ProcessingOperation.STRUCTURE in result.decision.operations
    assert result.context.original_text == text

def test_structure_decision_applies_structure_processor():
    engine = PreLyrEngine()

    text = (
        "Flask is a framework. "
        "It uses Python. "
        "It can build APIs. "
        "It is lightweight. "
        "It is easy to start with."
    )

    result = engine.process(text)

    assert ProcessingOperation.STRUCTURE in result.decision.operations
    assert result.context.optimized_text != text
    assert "- Flask is a framework." in result.context.optimized_text
    assert "- It uses Python." in result.context.optimized_text

def test_deduplication_is_applied():
    engine = PreLyrEngine()

    text = (
        "Flask is used as the backend. "
        "Flask is used as the backend. "
        "PostgreSQL is the database. "
        "PostgreSQL is the database."
    )

    result = engine.process(text)

    assert ProcessingOperation.DEDUPLICATE in result.decision.operations
    assert result.context.optimized_text.count(
        "Flask is used as the backend."
    ) == 1
    assert result.context.optimized_text.count(
        "PostgreSQL is the database."
    ) == 1

def test_deduplication_preserves_unique_information():
    engine = PreLyrEngine()

    text = (
        "Flask is used now. "
        "FastAPI may be used later. "
        "PostgreSQL is required."
    )

    result = engine.process(text)

    assert "Flask is used now." in result.context.optimized_text
    assert "FastAPI may be used later." in result.context.optimized_text
    assert "PostgreSQL is required." in result.context.optimized_text

def test_optimization_reduces_redundant_input_size():
    engine = PreLyrEngine()

    text = (
        "Flask is used as the backend. "
        "Flask is used as the backend. "
        "Flask is used as the backend. "
        "PostgreSQL is the database. "
        "PostgreSQL is the database."
    )

    result = engine.process(text)

    assert result.context.optimized_length < result.context.original_length

def test_no_op_preserves_input_size():
    engine = PreLyrEngine()

    text = "Explain what Flask is."

    result = engine.process(text)

    assert result.context.original_length == result.context.optimized_length

def test_semantic_redundancy_is_applied():
    engine = PreLyrEngine()

    text = (
        "Flask is used as the backend. "
        "The application backend is built using Flask. "
        "PostgreSQL is the database."
    )

    result = engine.process(text)

    assert ProcessingOperation.DEDUPLICATE in result.decision.operations
    assert "Flask is used as the backend." in result.context.optimized_text
    assert result.context.optimized_text.count(".") == 2
    assert "PostgreSQL is the database." in result.context.optimized_text

def test_engine_selects_relevant_context():
    engine = PreLyrEngine()

    text = (
        "The application started successfully. "
        "The server returned a 401 error. "
        "Authentication failed for the request. "
        "The development server is running on port 8000. "
        "The frontend build completed successfully. "
        "The database connection was established."
    )

    result = engine.process(text)

    assert (
        ProcessingOperation.SELECT_RELEVANT_CONTEXT
        in result.decision.operations
    )

    assert "401 error" in result.context.optimized_text
    assert "Authentication failed" in result.context.optimized_text

def test_engine_calculates_token_metrics():
    engine = PreLyrEngine()

    text = (
        "The backend uses Flask. "
        "The backend is built using Flask. "
        "The database uses PostgreSQL. "
        "Authentication is required for the API."
    )

    result = engine.process(text)

    assert result.context.original_tokens > 0
    assert result.context.optimized_tokens > 0

    assert (
        result.context.optimized_tokens
        <= result.context.original_tokens
    )

    assert (
        result.context.token_reduction_percentage >= 0
    )

