from __future__ import annotations

import re


# Words that can change the logical meaning of a sentence.
PROTECTED_NEGATIONS = {
    "not",
    "no",
    "never",
    "cannot",
    "can't",
    "won't",
    "wouldn't",
    "shouldn't",
    "isn't",
    "aren't",
    "wasn't",
    "weren't",
    "don't",
    "doesn't",
    "didn't",
    "without",
}

# Words that commonly express requirements or restrictions.
PROTECTED_CONSTRAINTS = {
    "only",
    "must",
    "required",
    "require",
    "at least",
    "at most",
    "exactly",
    "minimum",
    "maximum",
}

# Technical terms that should not disappear accidentally.
# This is intentionally small for V2 initial implementation.
PROTECTED_TECH_TERMS = {
    "python",
    "flask",
    "fastapi",
    "django",
    "postgresql",
    "mysql",
    "sqlite",
    "mongodb",
    "redis",
    "docker",
    "kubernetes",
    "api",
    "database",
    "backend",
    "frontend",
    "llm",
    "nlp",
    "prelyr",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _extract_numbers(text: str) -> set[str]:
    return set(re.findall(r"\b\d+(?:\.\d+)?\b", text))


def _contains_term(text: str, term: str) -> bool:
    pattern = rf"(?<!\w){re.escape(term)}(?!\w)"
    return re.search(pattern, text, re.IGNORECASE) is not None


def validate_removal(
    original: str,
    counterfactual: str,
) -> tuple[bool, str]:
    """
    Conservative safety validation.

    Returns:
        (True, reason)  -> safe
        (False, reason) -> reject
    """

    if not original.strip():
        return False, "empty_original"

    if not counterfactual.strip():
        return False, "empty_counterfactual"

    original_normalized = _normalize(original)
    counterfactual_normalized = _normalize(counterfactual)

    # Counterfactual must actually be different.
    if original_normalized == counterfactual_normalized:
        return False, "no_change"

    # We only accept actual shortening at this stage.
    if len(counterfactual_normalized) >= len(original_normalized):
        return False, "not_shorter"

    # ---------------------------------------------------------
    # 1. Number preservation
    # ---------------------------------------------------------

    original_numbers = _extract_numbers(original)
    counterfactual_numbers = _extract_numbers(counterfactual)

    if original_numbers != counterfactual_numbers:
        return False, "number_changed"

    # ---------------------------------------------------------
    # 2. Negation preservation
    # ---------------------------------------------------------

    for term in PROTECTED_NEGATIONS:
        original_has = _contains_term(original_normalized, term)
        counterfactual_has = _contains_term(
            counterfactual_normalized,
            term,
        )

        if original_has and not counterfactual_has:
            return False, f"negation_removed:{term}"

    # ---------------------------------------------------------
    # 3. Constraint preservation
    # ---------------------------------------------------------

    for term in PROTECTED_CONSTRAINTS:
        original_has = _contains_term(original_normalized, term)
        counterfactual_has = _contains_term(
            counterfactual_normalized,
            term,
        )

        if original_has and not counterfactual_has:
            return False, f"constraint_removed:{term}"

    # ---------------------------------------------------------
    # 4. Technical term preservation
    # ---------------------------------------------------------

    for term in PROTECTED_TECH_TERMS:
        original_has = _contains_term(original_normalized, term)
        counterfactual_has = _contains_term(
            counterfactual_normalized,
            term,
        )

        if original_has and not counterfactual_has:
            return False, f"technical_term_removed:{term}"

    return True, "safe"