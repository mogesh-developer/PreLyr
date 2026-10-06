from __future__ import annotations

from dataclasses import dataclass

from app.core.token_counter import TokenCounter

from .candidate_detector import Candidate, detect_candidates
from .counterfactual import remove_candidate
from .safety_validator import validate_removal
from .structural_validator import validate_structure



@dataclass
class OptimizationResult:
    original: str
    optimized: str

    original_tokens: int
    optimized_tokens: int
    token_reduction: int
    reduction_percentage: float

    accepted: list[Candidate]
    rejected: list[Candidate]


class LinguisticOptimizer:
    """
    Conservative counterfactual linguistic optimizer.

    Each candidate is independently tested by creating a
    counterfactual version and validating the result.

    Information preservation has priority over token reduction.
    """

    def __init__(self) -> None:
        self.token_counter = TokenCounter()

    def optimize(self, text: str) -> OptimizationResult:
        original = text

        original_tokens = self.token_counter.count(original)

        candidates = detect_candidates(original)

        if not candidates:
            return self._build_result(
                original=original,
                optimized=original,
                original_tokens=original_tokens,
                accepted=[],
                rejected=[],
            )

        current = original

        accepted: list[Candidate] = []
        rejected: list[Candidate] = []

        # Work from right → left so deleting a later candidate
        # does not invalidate positions of earlier candidates.
        for candidate in sorted(
            candidates,
            key=lambda item: item.start,
            reverse=True,
        ):
            current_candidate = self._resolve_candidate(
                current,
                candidate,
            )

            if current_candidate is None:
                rejected.append(candidate)
                continue

            counterfactual = remove_candidate(
                current,
                current_candidate,
            )

           # Safety validation
            is_safe, _reason = validate_removal(
                current,
                counterfactual,
            )

            if not is_safe:
                rejected.append(candidate)
                continue

            # Structural / linguistic validation
            structure_ok, _structure_reason = validate_structure(
                current,
                counterfactual,
            )

            if not structure_ok:
                rejected.append(candidate)
                continue

            # Token gate
            current_tokens = self.token_counter.count(current)
            counterfactual_tokens = self.token_counter.count(
                counterfactual
            )

            # Never accept an optimization that increases
            # token count.
            if counterfactual_tokens > current_tokens:
                rejected.append(candidate)
                continue

            current = counterfactual
            accepted.append(candidate)

        accepted.reverse()
        rejected.reverse()

        return self._build_result(
            original=original,
            optimized=current,
            original_tokens=original_tokens,
            accepted=accepted,
            rejected=rejected,
        )

    def _resolve_candidate(
        self,
        current: str,
        candidate: Candidate,
    ) -> Candidate | None:
        """
        Resolve the candidate against the current text.

        Uses the candidate's original position first.
        Falls back to searching the right occurrence.

        This prevents repeated candidate phrases from
        accidentally deleting the wrong occurrence.
        """

        candidate_length = len(candidate.text)

        # First try the original position.
        if (
            candidate.start >= 0
            and candidate.end <= len(current)
            and current[
                candidate.start:candidate.end
            ].lower()
            == candidate.text.lower()
        ):
            return Candidate(
                text=current[
                    candidate.start:candidate.end
                ],
                start=candidate.start,
                end=candidate.end,
                reason=candidate.reason,
                action=candidate.action,
            )

        # Fallback: find the right-most matching occurrence.
        position = current.lower().rfind(
            candidate.text.lower()
        )

        if position == -1:
            return None

        return Candidate(
            text=current[
                position:position + candidate_length
            ],
            start=position,
            end=position + candidate_length,
            reason=candidate.reason,
            action=candidate.action,
        )

    def _build_result(
        self,
        original: str,
        optimized: str,
        original_tokens: int,
        accepted: list[Candidate],
        rejected: list[Candidate],
    ) -> OptimizationResult:

        optimized_tokens = self.token_counter.count(
            optimized
        )

        token_reduction = (
            original_tokens - optimized_tokens
        )

        if original_tokens == 0:
            reduction_percentage = 0.0
        else:
            reduction_percentage = (
                token_reduction / original_tokens
            ) * 100

        return OptimizationResult(
            original=original,
            optimized=optimized,
            original_tokens=original_tokens,
            optimized_tokens=optimized_tokens,
            token_reduction=token_reduction,
            reduction_percentage=reduction_percentage,
            accepted=accepted,
            rejected=rejected,
        )