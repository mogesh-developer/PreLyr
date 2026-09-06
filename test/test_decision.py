from app.core.decision import DecisionEngine
from app.models.schemas import (
    AnalysisResult,
    ProcessingOperation,
    TaskType,
)


def test_short_explanation_uses_no_op():
    analysis = AnalysisResult(
        input_text="Explain what Flask is.",
        input_length=21,
        sentence_count=1,
        task_type=TaskType.EXPLANATION,
    )

    decision = DecisionEngine().decide(analysis)

    assert decision.operations == [ProcessingOperation.NO_OP]


def test_short_comparison_uses_no_op():
    analysis = AnalysisResult(
        input_text="Compare Flask and FastAPI.",
        input_length=27,
        sentence_count=1,
        task_type=TaskType.COMPARISON,
    )

    decision = DecisionEngine().decide(analysis)

    assert decision.operations == [ProcessingOperation.NO_OP]


def test_long_debugging_input_uses_structure():
    analysis = AnalysisResult(
        input_text="large debugging input",
        input_length=500,
        sentence_count=10,
        task_type=TaskType.DEBUGGING,
    )

    decision = DecisionEngine().decide(analysis)

    assert ProcessingOperation.STRUCTURE in decision.operations