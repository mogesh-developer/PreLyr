import os

import pytest
from google.genai.errors import APIError, ClientError

from app.core.engine import PreLyrEngine
from app.llm.gemini import GeminiProvider
from app.models.schemas import ProcessingOperation, TaskType


def _safe_generate(engine: PreLyrEngine, user_input: str) -> str:
    try:
        return engine.generate(user_input)
    except (ClientError, APIError) as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            pytest.skip(f"Gemini API quota exceeded: {e}")
        raise


@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY is not configured.",
)
def test_prelyr_with_real_gemini():
    provider = GeminiProvider()
    engine = PreLyrEngine(llm_provider=provider)

    user_input = "Explain what Flask is in simple terms."

    result = engine.process(user_input)

    assert ProcessingOperation.NO_OP in result.decision.operations

    answer = _safe_generate(engine, user_input)

    assert answer
    assert isinstance(answer, str)


@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY is not configured.",
)
def test_prelyr_structure_then_gemini():
    provider = GeminiProvider()
    engine = PreLyrEngine(llm_provider=provider)

    user_input = (
        "The backend currently uses Flask. "
        "The application requires a PostgreSQL database. "
        "Authentication is required for the API. "
        "The frontend communicates with the backend through REST APIs. "
        "The team may migrate to FastAPI in the future. "
        "The current deployment uses Docker. "
        "The application must support environment variables for configuration."
    )

    result = engine.process(user_input)

    assert ProcessingOperation.STRUCTURE in result.decision.operations

    assert result.context.optimized_text != user_input

    assert "Flask" in result.context.optimized_text
    assert "PostgreSQL" in result.context.optimized_text
    assert "FastAPI" in result.context.optimized_text
    assert "Docker" in result.context.optimized_text

    answer = _safe_generate(engine, user_input)

    assert answer
    assert isinstance(answer, str)


@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY is not configured.",
)
def test_prelyr_deduplicate_then_gemini():
    provider = GeminiProvider()
    engine = PreLyrEngine(llm_provider=provider)

    user_input = (
        "The backend uses Flask. "
        "The backend uses Flask. "
        "The database is PostgreSQL. "
        "The database is PostgreSQL. "
        "Authentication is required. "
        "Authentication is required. "
        "The frontend communicates through REST APIs. "
        "The frontend communicates through REST APIs."
    )

    result = engine.process(user_input)

    assert ProcessingOperation.DEDUPLICATE in result.decision.operations
    assert ProcessingOperation.STRUCTURE in result.decision.operations

    optimized = result.context.optimized_text

    assert optimized.count("The backend uses Flask.") == 1
    assert optimized.count("The database is PostgreSQL.") == 1
    assert optimized.count("Authentication is required.") == 1
    assert optimized.count(
        "The frontend communicates through REST APIs."
    ) == 1

    answer = _safe_generate(engine, user_input)

    assert answer
    assert isinstance(answer, str)

@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY is not configured.",
)
def test_prelyr_semantic_redundancy_then_gemini():
    provider = GeminiProvider()
    engine = PreLyrEngine(llm_provider=provider)

    user_input = (
        "The backend uses Flask. "
        "The application backend is built using Flask. "
        "The database is PostgreSQL. "
        "Authentication is required for the API."
    )

    result = engine.process(user_input)

    assert ProcessingOperation.DEDUPLICATE in result.decision.operations

    optimized = result.context.optimized_text

    assert "Flask" in optimized
    assert "PostgreSQL" in optimized
    assert "Authentication" in optimized

    answer = _safe_generate(engine, user_input)

    assert answer
    assert isinstance(answer, str)


@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY is not configured.",
)
def test_prelyr_relevant_context_then_gemini():
    provider = GeminiProvider()
    engine = PreLyrEngine(llm_provider=provider)

    user_input = (
        "The application started successfully. "
        "The frontend assets were loaded successfully. "
        "The server returned a 401 error when calling the API. "
        "Authentication failed because the provided token was invalid. "
        "The development server is running on port 8000. "
        "The database connection was established successfully. "
        "The API request requires valid authentication credentials."
    )

    result = engine.process(user_input)

    assert result.analysis.task_type == TaskType.DEBUGGING

    assert (
        ProcessingOperation.SELECT_RELEVANT_CONTEXT
        in result.decision.operations
    )

    optimized = result.context.optimized_text

    assert "401 error" in optimized
    assert "Authentication failed" in optimized
    assert "invalid" in optimized

    answer = _safe_generate(engine, user_input)

    assert answer
    assert isinstance(answer, str)
