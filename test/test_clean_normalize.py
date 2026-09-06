from app.processors.clean_normalize import CleanNormalizeProcessor


def test_normalizes_multiple_spaces():
    processor = CleanNormalizeProcessor()

    text = "Hello     world"

    result = processor.process(text)

    assert result == "Hello world"


def test_normalizes_tabs():
    processor = CleanNormalizeProcessor()

    text = "Hello\t\tworld"

    result = processor.process(text)

    assert result == "Hello world"


def test_removes_trailing_whitespace():
    processor = CleanNormalizeProcessor()

    text = "Hello world   \nSecond line   "

    result = processor.process(text)

    assert result == "Hello world\nSecond line"


def test_collapses_excessive_blank_lines():
    processor = CleanNormalizeProcessor()

    text = "First line\n\n\n\n\nSecond line"

    result = processor.process(text)

    assert result == "First line\n\nSecond line"


def test_normalizes_windows_line_endings():
    processor = CleanNormalizeProcessor()

    text = "First line\r\nSecond line\r\nThird line"

    result = processor.process(text)

    assert result == "First line\nSecond line\nThird line"


def test_preserves_numbers_and_versions():
    processor = CleanNormalizeProcessor()

    text = "Python 3.11   is running on port 8000."

    result = processor.process(text)

    assert result == "Python 3.11 is running on port 8000."


def test_preserves_http_status():
    processor = CleanNormalizeProcessor()

    text = "The API returned HTTP 500   error."

    result = processor.process(text)

    assert result == "The API returned HTTP 500 error."


def test_preserves_urls():
    processor = CleanNormalizeProcessor()

    text = "Visit https://example.com/api   for details."

    result = processor.process(text)

    assert result == "Visit https://example.com/api for details."


def test_empty_input():
    processor = CleanNormalizeProcessor()

    assert processor.process("") == ""


def test_already_clean_input():
    processor = CleanNormalizeProcessor()

    text = "Explain what Flask is."

    result = processor.process(text)

    assert result == text