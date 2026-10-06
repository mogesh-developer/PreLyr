from app.processors.document_repetition_optimizer import (
    DocumentRepetitionOptimizer,
)


def test_removes_high_confidence_repeated_page_element():

    pages = [
        """
        Desktop Welcome Guide

        Introduction to the application.
        """,
        """
        Desktop Welcome Guide

        Getting started.
        """,
        """
        Desktop Welcome Guide

        Working with PDFs.
        """,
    ]

    optimizer = DocumentRepetitionOptimizer()

    result = optimizer.optimize(pages)

    assert "Desktop Welcome Guide" not in (
        result.optimized
    )

    assert "Introduction to the application." in (
        result.optimized
    )

    assert "Getting started." in (
        result.optimized
    )

    assert "Working with PDFs." in (
        result.optimized
    )

    assert len(result.removed) == 1


def test_preserves_uncertain_repetition():

    pages = [
        """
        Python 3.11 is required.

        Introduction.
        """,
        """
        Python 3.11 is required.

        Configuration.
        """,
    ]

    optimizer = DocumentRepetitionOptimizer()

    result = optimizer.optimize(pages)

    assert (
        "Python 3.11 is required."
        in result.optimized
    )

    assert len(result.removed) == 0

    assert len(result.preserved) == 1


def test_unique_content_is_preserved():

    pages = [
        "Introduction",
        "Installation",
        "Configuration",
    ]

    optimizer = DocumentRepetitionOptimizer()

    result = optimizer.optimize(pages)

    assert result.optimized == (
        "Introduction\n\n"
        "Installation\n\n"
        "Configuration"
    )

    assert result.removed == []
    assert result.preserved == []