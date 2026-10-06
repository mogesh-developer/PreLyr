from __future__ import annotations

import re


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _has_malformed_punctuation(text: str) -> bool:
    """
    Detect obvious punctuation damage introduced by a transformation.
    """

    # Space before punctuation
    if re.search(r"\s+[,.!?;:]", text):
        return True

    # Repeated punctuation
    if re.search(r"[,.!?;:]{2,}", text):
        return True

    # Comma immediately after a sentence boundary
    if re.search(r"[.!?]\s*,", text):
        return True

    return False


def _has_lowercase_sentence_start(text: str) -> bool:
    """
    Detect sentences that incorrectly start with lowercase letters.

    Conservative:
    - Only checks alphabetic sentence starts.
    - Does not interfere with URLs, code, numbers, identifiers, etc.
    """

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        # Ignore opening quotes/brackets.
        sentence = re.sub(r'^[\'"\(\[\{]+', "", sentence)

        if not sentence:
            continue

        first_char = sentence[0]

        if first_char.isalpha() and first_char.islower():
            return True

    return False


def _has_clause_collision(text: str) -> bool:
    """
    Detect a small set of obvious clause collisions.

    Example:
        "The request failed the API was unavailable."

    This is intentionally conservative. It does NOT attempt
    full grammar checking.
    """

    patterns = [
        # Verb + subject without a valid connector.
        r"\b(failed|showed|reported|explained|indicated|confirmed|found)"
        r"\s+(the|a|an|this|that|it)\s+"
        r"(?:api|server|database|endpoint|request|service|system)\s+"
        r"(?:was|is|were|are|has|have|had)\b",

        # Noun phrase directly followed by another noun phrase
        # after a transformation.
        r"\b(api|server|database|endpoint|request|service|system)"
        r"\s+(the|a|an)\s+"
        r"(?:api|server|database|endpoint|request|service|system)\b",
    ]

    return any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in patterns
    )


def validate_structure(
    original: str,
    counterfactual: str,
) -> tuple[bool, str]:
    """
    Conservative structural validation.

    Returns:
        (True, reason)  -> structurally acceptable
        (False, reason) -> reject transformation

    The validator intentionally does not claim full semantic
    or grammatical equivalence.

    Uncertainty should result in KEEP.
    """

    if not original.strip():
        return False, "empty_original"

    if not counterfactual.strip():
        return False, "empty_counterfactual"

    original_normalized = _normalize(original)
    counterfactual_normalized = _normalize(counterfactual)

    if original_normalized == counterfactual_normalized:
        return False, "no_change"

    if _has_malformed_punctuation(counterfactual_normalized):
        return False, "malformed_punctuation"

    if _has_lowercase_sentence_start(counterfactual_normalized):
        return False, "lowercase_sentence_start"

    if _has_clause_collision(counterfactual_normalized):
        return False, "clause_collision"

    return True, "structure_ok"