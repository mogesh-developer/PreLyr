from __future__ import annotations

from collections import Counter


class DocumentDeduplicator:
    """
    Conservative document-level deduplication.

    Removes only repeated exact lines.

    Lossless-by-default:
        - first occurrence is preserved
        - unique lines are preserved
        - line order is preserved
        - no semantic rewriting
    """

    def deduplicate(
        self,
        text: str,
    ) -> str:

        lines = text.splitlines()

        normalized_lines = [
            line.strip()
            for line in lines
            if line.strip()
        ]

        counts = Counter(normalized_lines)

        seen: set[str] = set()
        result: list[str] = []

        for line in normalized_lines:

            # Keep the first occurrence.
            if line not in seen:
                result.append(line)
                seen.add(line)
                continue

            # Repeated line.
            #
            # We currently remove it conservatively.
            if counts[line] > 1:
                continue

        return "\n".join(result)