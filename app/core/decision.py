from app.models.schemas import (
    AnalysisResult,
    ProcessingDecision,
    ProcessingOperation,
    TaskType,
)


class DecisionEngine:

    def decide(self, analysis: AnalysisResult) -> ProcessingDecision:
        if analysis.is_empty:
            return ProcessingDecision(
                operations=[ProcessingOperation.NO_OP],
                reason="Input is empty.",
            )

        operations = []

        if analysis.duplicate_count > 0:
            operations.append(
                ProcessingOperation.DEDUPLICATE
            )

        if (
            analysis.input_length >= 200
            and analysis.task_type != TaskType.UNKNOWN
        ):
            operations.append(
                ProcessingOperation.SELECT_RELEVANT_CONTEXT
            )

        if analysis.input_length < 200 and analysis.sentence_count <= 2:
            if not operations:
                operations.append(
                    ProcessingOperation.NO_OP
                )

            return ProcessingDecision(
                operations=operations,
                reason=(
                    "Input is short and sufficiently concise."
                    if len(operations) == 1
                    else "Input is short but contains content requiring processing."
                ),
            )

        operations.append(
            ProcessingOperation.STRUCTURE
        )

        return ProcessingDecision(
            operations=operations,
            reason=(
                "Input may benefit from deduplication, "
                "relevant context selection, and structural processing."
                if ProcessingOperation.SELECT_RELEVANT_CONTEXT in operations
                else "Input is larger and may benefit from structural processing."
            ),
        )