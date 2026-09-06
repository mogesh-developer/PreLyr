from app.processors.structure import StructureProcessor


def test_structure_processor():
    processor = StructureProcessor()

    text = "Flask is a framework. It uses Python. It can build APIs."

    result = processor.process(text)

    assert "- Flask is a framework." in result
    assert "- It uses Python." in result
    assert "- It can build APIs." in result


def test_structure_processor_preserves_information():
    processor = StructureProcessor()

    text = "Flask is used. FastAPI may be used later."

    result = processor.process(text)

    assert "Flask is used." in result
    assert "FastAPI may be used later." in result