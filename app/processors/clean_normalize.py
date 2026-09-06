import re


class CleanNormalizeProcessor:
    """
    Safely cleans and normalizes textual input without changing
    its semantic or technical meaning.
    """

    def process(self, text: str) -> str:
        if not text:
            return text

        cleaned = self._normalize_line_endings(text)
        cleaned = self._remove_trailing_whitespace(cleaned)
        cleaned = self._collapse_excessive_blank_lines(cleaned)
        cleaned = self._normalize_spaces(cleaned)

        return cleaned.strip()

    def _normalize_line_endings(self, text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n")

    def _remove_trailing_whitespace(self, text: str) -> str:
        return "\n".join(
            line.rstrip()
            for line in text.split("\n")
        )

    def _collapse_excessive_blank_lines(self, text: str) -> str:
        return re.sub(r"\n{3,}", "\n\n", text)

    def _normalize_spaces(self, text: str) -> str:
        lines = []

        for line in text.split("\n"):
            if not line.strip():
                lines.append("")
                continue

            line = re.sub(r"[ \t]+", " ", line)
            lines.append(line)

        return "\n".join(lines)