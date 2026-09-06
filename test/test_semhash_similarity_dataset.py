import time

from semhash import SemHash

from test.test_similarity_dataset import DATASET


THRESHOLDS = [
    0.70,
    0.75,
    0.80,
    0.85,
    0.90,
    0.92,
    0.94,
    0.96,
]


def build_records():
    """
    Convert the existing pair dataset into SemHash records.

    Expected DATASET format:
        [
            (sentence_a, sentence_b, is_duplicate),
            ...
        ]
    """

    records = []

    for pair_index, item in enumerate(DATASET):
        sentence_a = item["a"]
        sentence_b = item["b"]
        is_duplicate = item["duplicate"]
        records.append(
            {
                "pair_id": pair_index,
                "text": sentence_a,
                "label": is_duplicate,
                "side": "A",
            }
        )

        records.append(
            {
                "pair_id": pair_index,
                "text": sentence_b,
                "label": is_duplicate,
                "side": "B",
            }
        )

    return records


def evaluate_threshold(records, threshold):
    """
    Run SemHash self-deduplication and evaluate pair-level decisions.

    A pair is considered predicted duplicate if SemHash places
    one sentence as a duplicate of the other.
    """

    semhash = SemHash.from_records(
        records=records,
        columns=["text"],
    )

    start = time.perf_counter()

    result = semhash.self_deduplicate(
        threshold=threshold,
    )

    elapsed = time.perf_counter() - start

    predicted_duplicates = set()

    for item in result.filtered:
        duplicate_pair_id = item.record["pair_id"]
        predicted_duplicates.add(duplicate_pair_id)

    tp = 0
    fp = 0
    fn = 0
    tn = 0

    critical_false_positives = []

    for pair_index, item in enumerate(DATASET):
        actual_duplicate = item["duplicate"]

        predicted_duplicate = pair_index in predicted_duplicates

        if actual_duplicate and predicted_duplicate:
            tp += 1

        elif actual_duplicate and not predicted_duplicate:
            fn += 1

        elif not actual_duplicate and predicted_duplicate:
            fp += 1

            critical_false_positives.append(
                {
                    "pair_index": pair_index,
                    "sentence_a": item["a"],
                    "sentence_b": item["b"],
                }
            )

        else:
            tn += 1

    precision = (
        tp / (tp + fp)
        if (tp + fp)
        else 0.0
    )

    recall = (
        tp / (tp + fn)
        if (tp + fn)
        else 0.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0.0
    )

    fpr = (
        fp / (fp + tn)
        if (fp + tn)
        else 0.0
    )

    return {
        "threshold": threshold,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "critical_false_positives": critical_false_positives,
        "elapsed": elapsed,
        "duplicate_ratio": result.duplicate_ratio,
    }


def test_semhash_similarity_dataset():

    records = build_records()

    print("\n" + "=" * 80)
    print("SemHash Threshold Benchmark")
    print("=" * 80)

    for threshold in THRESHOLDS:

        result = evaluate_threshold(
            records,
            threshold,
        )

        print(
            f"\nthreshold={result['threshold']:.2f}"
            f" | precision={result['precision']:.2%}"
            f" | recall={result['recall']:.2%}"
            f" | f1={result['f1']:.2%}"
            f" | fpr={result['fpr']:.2%}"
            f" | duplicate_ratio={result['duplicate_ratio']:.2%}"
            f" | time={result['elapsed']:.4f}s"
        )

        print(
            f"TP={result['tp']} "
            f"FP={result['fp']} "
            f"FN={result['fn']} "
            f"TN={result['tn']}"
        )

        if result["critical_false_positives"]:
            print("\nFalse positives:")

            for item in result["critical_false_positives"]:
                print(
                    f"  [{item['pair_index']}] "
                    f"{item['sentence_a']}"
                    f"  <->  "
                    f"{item['sentence_b']}"
                )

    assert len(records) == len(DATASET) * 2