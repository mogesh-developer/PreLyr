from pathlib import Path
from time import perf_counter

from app.processors.document_processor import (
    DocumentProcessor,
)


PDF_PATH = Path("test/fixtures/sample.pdf")


def main() -> None:
    processor = DocumentProcessor()

    start = perf_counter()

    result = processor.process(
        PDF_PATH,
        task="Understand this document",
    )

    elapsed = perf_counter() - start

    print("\n========== PreLyr Document Benchmark ==========")

    print(f"File                 : {result.file_name}")
    print(f"Pages                : {result.pages_processed}")

    print(
        f"Original tokens      : "
        f"{result.original_tokens}"
    )

    print(
        f"Optimized tokens     : "
        f"{result.optimized_tokens}"
    )

    print(
        f"Token reduction      : "
        f"{result.original_tokens - result.optimized_tokens}"
    )

    print(
        f"Reduction percentage : "
        f"{result.reduction_percentage:.2f}%"
    )

    print(
        f"Processing steps     : "
        f"{' → '.join(result.processing_steps)}"
    )

    print(
        f"Processing time      : "
        f"{elapsed:.4f} seconds"
    )

    print("===============================================\n")


if __name__ == "__main__":
    main()