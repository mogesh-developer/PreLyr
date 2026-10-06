from pathlib import Path

from app.processors.pdf_layout import PDFLayoutProcessor


pdf_path = Path("test/fixtures/sample.pdf")

processor = PDFLayoutProcessor()

blocks = processor.process(pdf_path)

for block in blocks:
    print("=" * 80)
    print(f"PAGE      : {block['page']}")
    print(f"TEXT      : {block['text']}")
    print(f"FONT SIZE : {block['font_size']}")
    print(f"FONT      : {block['font_name']}")
    print(
        f"POSITION  : "
        f"({block['x0']:.2f}, {block['y0']:.2f}) -> "
        f"({block['x1']:.2f}, {block['y1']:.2f})"
    )