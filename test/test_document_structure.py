from app.processors.document_structure import (
    DocumentStructureProcessor,
)


def test_detects_basic_heading_hierarchy():
    pages = [
        """
        # Project Requirements

        ## Backend

        Flask backend is required.

        ## Database

        PostgreSQL is required.

        ### Redis

        Redis is used for caching.
        """
    ]

    processor = DocumentStructureProcessor()

    document = processor.process(pages)

    assert len(document.sections) == 1

    root = document.sections[0]

    assert root.title == "# Project Requirements"
    assert root.level == 1

    assert len(root.children) == 2

    assert root.children[0].title == "## Backend"
    assert root.children[0].level == 2

    assert root.children[1].title == "## Database"
    assert root.children[1].level == 2

    assert len(root.children[1].children) == 1

    redis = root.children[1].children[0]

    assert redis.title == "### Redis"
    assert redis.level == 3


def test_preserves_content_under_section():
    pages = [
        """
        # Backend

        Flask backend is required.
        The API must expose a health endpoint.
        """
    ]

    processor = DocumentStructureProcessor()

    document = processor.process(pages)

    backend = document.sections[0]

    assert backend.content == [
        "Flask backend is required.",
        "The API must expose a health endpoint.",
    ]


def test_preserves_content_before_first_heading():
    pages = [
        """
        Introduction text.

        This document describes the project.

        # Requirements

        The backend is required.
        """
    ]

    processor = DocumentStructureProcessor()

    document = processor.process(pages)

    assert len(document.sections) == 2

    intro = document.sections[0]

    assert intro.title == "Document Content"
    assert intro.level == 0

    assert intro.content == [
        "Introduction text.",
        "This document describes the project.",
    ]


def test_preserves_page_order():
    pages = [
        """
        # First Section

        First page content.
        """,
        """
        # Second Section

        Second page content.
        """,
    ]

    processor = DocumentStructureProcessor()

    document = processor.process(pages)

    assert len(document.sections) == 2

    assert document.sections[0].title == "# First Section"
    assert document.sections[1].title == "# Second Section"


def test_empty_pages_are_ignored():
    pages = [
        "",
        "   ",
        """
        # Requirements

        Backend is required.
        """,
    ]

    processor = DocumentStructureProcessor()

    document = processor.process(pages)

    assert len(document.sections) == 1

    assert document.sections[0].title == "# Requirements"


def test_non_heading_lines_are_preserved():
    pages = [
        """
        This is normal text.
        It should not become a heading.

        Another paragraph.
        """
    ]

    processor = DocumentStructureProcessor()

    document = processor.process(pages)

    assert len(document.sections) == 1

    section = document.sections[0]

    assert section.title == "Document Content"
    assert section.level == 0

    assert section.content == [
        "This is normal text.",
        "It should not become a heading.",
        "Another paragraph.",
    ]


def test_heading_level_returns_to_parent():
    pages = [
        """
        # Project

        ## Backend

        Backend details.

        ### API

        API details.

        ## Database

        Database details.
        """
    ]

    processor = DocumentStructureProcessor()

    document = processor.process(pages)

    project = document.sections[0]

    assert project.title == "# Project"
    assert len(project.children) == 2

    backend = project.children[0]
    database = project.children[1]

    assert backend.title == "## Backend"
    assert database.title == "## Database"

    assert len(backend.children) == 1
    assert backend.children[0].title == "### API"

    assert database.children == []