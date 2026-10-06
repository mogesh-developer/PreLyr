from __future__ import annotations

import re

from .candidate_detector import Candidate


PHRASE_TRANSFORMATIONS = {
    "in order to": "to",
    "due to the fact that": "because",
    "at this point in time": "currently",
}


def transform_candidate(
    text: str,
    candidate: Candidate,
) -> str:
    """
    Create a context-aware counterfactual transformation.

    Supported transformations:
        "in order to" -> "to"
        "due to the fact that" -> "because"
        "at this point in time" -> "currently"

    Filler candidates are removed conservatively.
    """

    before = text[:candidate.start]
    after = text[candidate.end:]

    candidate_text = candidate.text.lower()

    if candidate.action == "TRANSFORM":
        replacement = PHRASE_TRANSFORMATIONS.get(
            candidate_text
        )

        if replacement is not None:
            replacement = _contextualize_replacement(
                before,
                replacement,
            )

            result = (
                before
                + replacement
                + after
            )

            return _normalize_whitespace(result)

    # Default: remove candidate.
    result = before + after

    # Candidate followed by punctuation:
    # "Basically, I..." -> "I..."
    result = re.sub(
        r"^\s*([,:;])\s*",
        " ",
        result,
    )

    # Candidate after sentence boundary:
    # "...this. Basically, I..." -> "...this. I..."
    result = re.sub(
        r"([.!?])\s*,\s*",
        r"\1 ",
        result,
    )

    # If the removed candidate was at the beginning of a
    # sentence, preserve the capitalization of the sentence.
    #
    # Example:
    #   "Actually, the server works."
    #       ->
    #   "The server works."
    #
    # This keeps the structural validator strict instead of
    # weakening it to accept malformed counterfactuals.
    result = _capitalize_affected_sentence(
        result,
        before,
    )

    return _normalize_whitespace(result)


def remove_candidate(
    text: str,
    candidate: Candidate,
) -> str:
    """
    Backward-compatible wrapper.

    The function name is retained because the optimizer
    already uses it, but the implementation now supports
    both removal and transformation.
    """

    return transform_candidate(
        text,
        candidate,
    )


def _contextualize_replacement(
    before: str,
    replacement: str,
) -> str:
    """
    Preserve sentence-start capitalization for replacements.

    Example:
        "At this point in time, the server..."
            ↓
        "Currently, the server..."
    """

    stripped_before = before.rstrip()

    if not stripped_before:
        return replacement.capitalize()

    if stripped_before.endswith(
        (".", "!", "?")
    ):
        return replacement.capitalize()

    return replacement


def _capitalize_affected_sentence(
    text: str,
    before: str,
) -> str:
    """
    Preserve capitalization when a sentence-start candidate
    is removed.

    Only the sentence affected by the removal is modified.
    """

    stripped_before = before.rstrip()

    # Candidate was not at the beginning of a sentence.
    if stripped_before and not stripped_before.endswith(
        (".", "!", "?")
    ):
        return text

    # Find the sentence boundary immediately before the
    # removed candidate.
    boundary = max(
        (
            stripped_before.rfind("."),
            stripped_before.rfind("!"),
            stripped_before.rfind("?"),
        )
    )

    sentence_start = boundary + 1

    # The counterfactual may contain whitespace or opening
    # punctuation before the first alphabetic character.
    match = re.search(
        r"[A-Za-z]",
        text[sentence_start:],
    )

    if not match:
        return text

    index = sentence_start + match.start()

    return (
        text[:index]
        + text[index].upper()
        + text[index + 1:]
    )


def _normalize_whitespace(text: str) -> str:
    """
    Normalize consecutive whitespace into a single space and strip whitespace.
    """
    return re.sub(r"\s+", " ", text).strip()