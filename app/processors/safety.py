import re


class SafetyValidator:
    """
    Determines whether two highly similar sentences contain
    critical differences that make them unsafe to deduplicate.
    """

    NUMBER_PATTERN = re.compile(
        r"\b\d+(?:\.\d+)?\b"
    )

    VERSION_PATTERN = re.compile(
        r"\b(?:python|node(?:\.js)?|postgres(?:ql)?|mysql|java)"
        r"[\s-]*\d+(?:\.\d+)*\b",
        re.IGNORECASE,
    )

    HTTP_STATUS_PATTERN = re.compile(
        r"\b(?:http\s*)?[1-5]\d{2}\b",
        re.IGNORECASE,
    )

    NEGATION_WORDS = {
        "not",
        "no",
        "never",
        "without",
        "isn't",
        "aren't",
        "wasn't",
        "weren't",
        "doesn't",
        "don't",
        "didn't",
        "failed",
        "failure",
        "invalid",
        "disabled",
        "rejected",
        "unavailable",
        "deleted",
    }

    OPPOSITE_PAIRS = {
        frozenset({"success", "failure"}),
        frozenset({"successful", "failed"}),
        frozenset({"succeeded", "failed"}),
        frozenset({"valid", "invalid"}),
        frozenset({"enabled", "disabled"}),
        frozenset({"accepted", "rejected"}),
        frozenset({"available", "unavailable"}),
        frozenset({"created", "deleted"}),
        frozenset({"started", "stopped"}),
        frozenset({"running", "stopped"}),
        frozenset({"healthy", "unhealthy"}),
        frozenset({"before", "after"}),
        frozenset({"reads", "writes"}),
    }

    def is_safe_to_deduplicate(
        self,
        sentence_a: str,
        sentence_b: str,
    ) -> bool:
        """
        Return True only when there is no detected critical difference.

        True  -> safe candidate for deduplication
        False -> preserve both sentences
        """

        if self._has_different_numbers(sentence_a, sentence_b):
            return False

        if self._has_different_versions(sentence_a, sentence_b):
            return False

        if self._has_different_http_statuses(sentence_a, sentence_b):
            return False

        if self._has_opposite_meaning(sentence_a, sentence_b):
            return False

        if self._has_negation_difference(sentence_a, sentence_b):
            return False

        return True

    def _extract_numbers(self, text: str) -> list[str]:
        return self.NUMBER_PATTERN.findall(text)

    def _has_different_numbers(
        self,
        sentence_a: str,
        sentence_b: str,
    ) -> bool:
        numbers_a = self._extract_numbers(sentence_a)
        numbers_b = self._extract_numbers(sentence_b)

        if not numbers_a and not numbers_b:
            return False

        return numbers_a != numbers_b

    def _extract_versions(self, text: str) -> list[str]:
        return [
            version.casefold()
            for version in self.VERSION_PATTERN.findall(text)
        ]

    def _has_different_versions(
        self,
        sentence_a: str,
        sentence_b: str,
    ) -> bool:
        versions_a = self._extract_versions(sentence_a)
        versions_b = self._extract_versions(sentence_b)

        if not versions_a and not versions_b:
            return False

        return versions_a != versions_b

    def _extract_http_statuses(self, text: str) -> list[str]:
        return self.HTTP_STATUS_PATTERN.findall(text)

    def _has_different_http_statuses(
        self,
        sentence_a: str,
        sentence_b: str,
    ) -> bool:
        statuses_a = self._extract_http_statuses(sentence_a)
        statuses_b = self._extract_http_statuses(sentence_b)

        if not statuses_a and not statuses_b:
            return False

        return statuses_a != statuses_b

    def _has_opposite_meaning(
        self,
        sentence_a: str,
        sentence_b: str,
    ) -> bool:
        words_a = set(
            re.findall(r"\b[\w']+\b", sentence_a.casefold())
        )

        words_b = set(
            re.findall(r"\b[\w']+\b", sentence_b.casefold())
        )

        for pair in self.OPPOSITE_PAIRS:
            if pair.issubset(words_a | words_b):
                if (
                    pair.intersection(words_a)
                    and pair.intersection(words_b)
                    and words_a != words_b
                ):
                    return True

        return False

    def _has_negation_difference(
        self,
        sentence_a: str,
        sentence_b: str,
    ) -> bool:
        words_a = set(
            re.findall(r"\b[\w']+\b", sentence_a.casefold())
        )

        words_b = set(
            re.findall(r"\b[\w']+\b", sentence_b.casefold())
        )

        negation_a = words_a.intersection(self.NEGATION_WORDS)
        negation_b = words_b.intersection(self.NEGATION_WORDS)

        return bool(negation_a) != bool(negation_b)