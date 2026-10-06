from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Candidate:
    text: str
    start: int
    end: int
    reason: str
    action: str = "REMOVE"


SAFE_SINGLE_WORDS = {
    "actually": "discourse filler",
    "basically": "discourse filler",
    "really": "discourse filler",
}

SAFE_PHRASES = {
    "in order to": (
        "TRANSFORM",
        "verbose infinitive phrase",
    ),
    "due to the fact that": (
        "TRANSFORM",
        "verbose causal phrase",
    ),
    "at this point in time": (
        "TRANSFORM",
        "verbose temporal phrase",
    ),
}


def detect_candidates(text: str) -> list[Candidate]:
    candidates: list[Candidate] = []

    for phrase, (action, reason) in SAFE_PHRASES.items():
        pattern = re.compile(
            rf"\b{re.escape(phrase)}\b",
            re.IGNORECASE,
        )

        for match in pattern.finditer(text):
            candidates.append(
                Candidate(
                    text=match.group(),
                    start=match.start(),
                    end=match.end(),
                    reason=reason,
                    action=action,
                )
            )

    for word, reason in SAFE_SINGLE_WORDS.items():
        pattern = re.compile(
            rf"\b{re.escape(word)}\b",
            re.IGNORECASE,
        )

        for match in pattern.finditer(text):
            candidates.append(
                Candidate(
                    text=match.group(),
                    start=match.start(),
                    end=match.end(),
                    reason=reason,
                    action="REMOVE",
                )
            )

    return sorted(
        candidates,
        key=lambda candidate: (
            candidate.start,
            candidate.end,
        ),
    )