from semhash import SemHash


def test_semhash_basic():
    records = [
        "The backend uses Flask.",
        "The backend is built using Flask.",
        "The database uses PostgreSQL.",
    ]

    semhash = SemHash.from_records(records=records)

    result = semhash.self_deduplicate(threshold=0.85)

    print("\nSelected:")
    for item in result.selected:
        print(item)

    print("\nFiltered:")
    for item in result.filtered:
        print(item)

    print("\nSelected with duplicates:")
    for item in result.selected_with_duplicates:
        print(item)

    assert len(result.selected) > 0