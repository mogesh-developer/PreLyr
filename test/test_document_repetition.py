from app.processors.document_repetition import (
    DocumentRepetitionDetector,
)


def test_detects_repeated_text_across_pages():

    pages = [
        """
        Desktop Welcome Guide

        Introduction to the application.
        """,
        """
        Desktop Welcome Guide

        Getting started with the application.
        """,
        """
        Desktop Welcome Guide

        Working with PDF files.
        """,
    ]

    detector = DocumentRepetitionDetector()

    candidates = detector.detect(pages)

    assert candidates

    candidate = next(
        candidate
        for candidate in candidates
        if candidate.text
        == "Desktop Welcome Guide"
    )

    assert candidate.pages == (1, 2, 3)

    assert candidate.occurrences == 3

    assert candidate.reason == (
        "repeated_page_element"
    )

    assert candidate.confidence == 0.90


def test_does_not_flag_unique_text():

    pages = [
        "Introduction",
        "Getting Started",
        "Conclusion",
    ]

    detector = DocumentRepetitionDetector()

    candidates = detector.detect(pages)

    assert candidates == []


def test_same_line_repeated_inside_one_page_is_not_counted_twice():

    pages = [
        """
        Desktop Welcome Guide
        Desktop Welcome Guide
        Introduction
        """,
        """
        Desktop Welcome Guide
        """,
    ]

    detector = DocumentRepetitionDetector()

    candidates = detector.detect(pages)

    candidate = next(
        candidate
        for candidate in candidates
        if candidate.text
        == "Desktop Welcome Guide"
    )

    assert candidate.occurrences == 2

    assert candidate.pages == (1, 2)


def test_whitespace_is_normalized():

    pages = [
        "Desktop   Welcome   Guide",
        "Desktop Welcome Guide",
    ]

    detector = DocumentRepetitionDetector()

    candidates = detector.detect(pages)

    assert len(candidates) == 1

    assert candidates[0].text == (
        "Desktop Welcome Guide"
    )