from app.models.schemas import (
    AnalysisResult,
    OptimizedContext,
    ProcessingDecision,
    ProcessingOperation,
)


def test_analysis_result():
    result = AnalysisResult(
        input_text="Explain what Flask is.",
        input_length=22,
        sentence_count=1,
    )

    assert result.is_empty is False
    assert result.sentence_count == 1


def test_no_op_decision():
    decision = ProcessingDecision(
        operations=[ProcessingOperation.NO_OP],
        reason="Input is already clean and concise.",
    )

    assert ProcessingOperation.NO_OP in decision.operations


def test_optimized_context():
    context = OptimizedContext(
        original_text="Hello",
        optimized_text="Hello",
        operations_applied=[ProcessingOperation.NO_OP],
    )

    assert context.original_text == context.optimized_text