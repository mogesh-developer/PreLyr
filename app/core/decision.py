from app.core.analyzer import InputAnalyzer
from app.models.schemas import (
    AnalysisResult,
    ProcessingDecision,
    ProcessingOperation,
    TaskType,
)
from app.nlp.candidate_detector import detect_candidates


class DecisionEngine:

    def decide(
        self,
        analysis: AnalysisResult,
    ) -> ProcessingDecision:

        if analysis.is_empty:
            return ProcessingDecision(
                operations=[
                    ProcessingOperation.NO_OP
                ],
                reason="Input is empty.",
            )

        operations = []

        # --------------------------------------------------
        # Existing V1 processing decisions
        # --------------------------------------------------

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

        if self._needs_cleaning(
            analysis.input_text
        ):
            operations.append(
                ProcessingOperation.CLEAN
            )
            operations.append(
                ProcessingOperation.NORMALIZE
            )

        # --------------------------------------------------
        # V2 linguistic optimization decision
        #
        # Candidate detection is lightweight.
        # Actual optimization is still validated by
        # LinguisticOptimizer.
        # --------------------------------------------------

        linguistic_candidates = detect_candidates(
            analysis.input_text
        )

        if linguistic_candidates:
            operations.append(
                ProcessingOperation.LINGUISTIC_OPTIMIZATION
            )

        # --------------------------------------------------
        # Short input
        # --------------------------------------------------

        if (
            analysis.input_length < 200
            and analysis.sentence_count <= 2
        ):
            if not operations:
                operations.append(
                    ProcessingOperation.NO_OP
                )

                return ProcessingDecision(
                    operations=operations,
                    reason=(
                        "Input is short and "
                        "sufficiently concise."
                    ),
                )

            return ProcessingDecision(
                operations=operations,
                reason=(
                    "Input is short but contains "
                    "content requiring processing."
                ),
            )

        # --------------------------------------------------
        # Longer input
        # --------------------------------------------------

        if (
            ProcessingOperation.STRUCTURE
            not in operations
        ):
            operations.append(
                ProcessingOperation.STRUCTURE
            )

        return ProcessingDecision(
            operations=operations,
            reason=(
                "Input may benefit from selective "
                "context processing."
            ),
        )

    def _needs_cleaning(
        self,
        text: str,
    ) -> bool:

        if not text:
            return False

        if text != text.strip():
            return True

        if "\r\n" in text or "\r" in text:
            return True

        if any(
            line.rstrip() != line
            for line in text.split("\n")
        ):
            return True

        if "\t" in text:
            return True

        if "  " in text:
            return True

        if "\n\n\n" in text:
            return True

        return False