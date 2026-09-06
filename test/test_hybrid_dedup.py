import time

from model2vec import StaticModel
from rapidfuzz import fuzz
from sklearn.metrics.pairwise import cosine_similarity

from app.processors.safety import SafetyValidator


MODEL_NAME = "minishlab/potion-base-8M"


def lexical_similarity(sentence_a: str, sentence_b: str) -> float:
    return fuzz.ratio(sentence_a, sentence_b)


def strategy_a(
    semantic_score: float,
    lexical_score: float,
    sentence_a: str,
    sentence_b: str,
    safety: SafetyValidator,
) -> bool:
    """
    Baseline:
    semantic + lexical + safety
    """

    return (
        semantic_score >= 0.85
        and lexical_score >= 50
        and safety.is_safe_to_deduplicate(
            sentence_a,
            sentence_b,
        )
    )


def strategy_b(
    semantic_score: float,
    lexical_score: float,
    sentence_a: str,
    sentence_b: str,
    safety: SafetyValidator,
) -> bool:
    """
    Semantic-first:
    strong semantic similarity + safety.
    Lexical similarity is only observed, not required.
    """

    return (
        semantic_score >= 0.85
        and safety.is_safe_to_deduplicate(
            sentence_a,
            sentence_b,
        )
    )


def strategy_c(
    semantic_score: float,
    lexical_score: float,
    sentence_a: str,
    sentence_b: str,
    safety: SafetyValidator,
) -> bool:
    """
    Adaptive threshold:

    >= 0.90
        semantic + safety

    0.85 - 0.90
        semantic + lexical + safety

    < 0.85
        reject
    """

    safety_ok = safety.is_safe_to_deduplicate(
        sentence_a,
        sentence_b,
    )

    if not safety_ok:
        return False

    if semantic_score >= 0.90:
        return True

    if semantic_score >= 0.85 and lexical_score >= 50:
        return True

    return False


def calculate_metrics(results, strategy):
    tp = fp = tn = fn = 0

    false_positives = []

    for item in results:

        predicted = strategy(
            semantic_score=item["semantic"],
            lexical_score=item["lexical"],
            sentence_a=item["a"],
            sentence_b=item["b"],
            safety=item["safety"],
        )

        expected = item["expected"]

        if predicted and expected:
            tp += 1

        elif predicted and not expected:
            fp += 1
            false_positives.append(item)

        elif not predicted and expected:
            fn += 1

        else:
            tn += 1

    precision = (
        tp / (tp + fp)
        if tp + fp
        else 0
    )

    recall = (
        tp / (tp + fn)
        if tp + fn
        else 0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0
    )

    fpr = (
        fp / (fp + tn)
        if fp + tn
        else 0
    )

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr,
        "false_positives": false_positives,
    }


def test_hybrid_strategies():

    from test.test_similarity_dataset import DATASET

    start = time.perf_counter()

    model = StaticModel.from_pretrained(
        MODEL_NAME
    )

    safety = SafetyValidator()

    sentences = []

    for item in DATASET:
        sentences.append(item["a"])
        sentences.append(item["b"])

    unique_sentences = list(
        dict.fromkeys(sentences)
    )

    embeddings = model.encode(
        unique_sentences
    )

    embedding_map = {
        sentence: embedding
        for sentence, embedding in zip(
            unique_sentences,
            embeddings,
        )
    }

    results = []

    for item in DATASET:
        sentence_a = item["a"]
        sentence_b = item["b"]
        expected_duplicate = item["duplicate"]

        semantic_score = cosine_similarity(
            [embedding_map[sentence_a]],
            [embedding_map[sentence_b]],
        )[0][0]

        lexical_score = lexical_similarity(
            sentence_a,
            sentence_b,
        )

        results.append(
            {
                "a": sentence_a,
                "b": sentence_b,
                "expected": expected_duplicate,
                "semantic": float(semantic_score),
                "lexical": float(lexical_score),
                "safety": safety,
            }
        )

    strategies = {
        "Strategy A": strategy_a,
        "Strategy B": strategy_b,
        "Strategy C": strategy_c,
    }

    for name, strategy in strategies.items():

        metrics = calculate_metrics(
            results,
            strategy,
        )

        print("\n" + "=" * 60)
        print(name)
        print("=" * 60)

        print(
            f"precision = {metrics['precision']:.2%}"
        )

        print(
            f"recall    = {metrics['recall']:.2%}"
        )

        print(
            f"f1        = {metrics['f1']:.2%}"
        )

        print(
            f"fpr       = {metrics['fpr']:.2%}"
        )

        print(
            f"TP={metrics['tp']} "
            f"FP={metrics['fp']} "
            f"FN={metrics['fn']} "
            f"TN={metrics['tn']}"
        )

        print(
            f"false_positives = "
            f"{len(metrics['false_positives'])}"
        )

        if metrics["false_positives"]:

            print("\nFalse positives:")

            for item in metrics["false_positives"]:

                print(
                    f"\n"
                    f"A: {item['a']}\n"
                    f"B: {item['b']}\n"
                    f"semantic={item['semantic']:.4f} "
                    f"lexical={item['lexical']:.2f}"
                )

        if name == "Strategy B":
            false_negatives = [
                item
                for item in results
                if (
                    item["expected"]
                    and not strategy(
                        semantic_score=item["semantic"],
                        lexical_score=item["lexical"],
                        sentence_a=item["a"],
                        sentence_b=item["b"],
                        safety=item["safety"],
                    )
                )
            ]

            if false_negatives:
                print("\nFalse negatives:")

                for item in false_negatives:
                    safety_ok = item["safety"].is_safe_to_deduplicate(
                        item["a"],
                        item["b"],
                    )
                    print(
                        f"\nA: {item['a']}\n"
                        f"B: {item['b']}\n"
                        f"semantic={item['semantic']:.4f} "
                        f"lexical={item['lexical']:.2f} "
                        f"safety={safety_ok}"
                    )

    elapsed = time.perf_counter() - start

    print("\n" + "=" * 60)
    print(f"Total evaluation time: {elapsed:.4f}s")
    print("=" * 60)

    assert len(results) == len(DATASET)

def test_strategy_b_threshold_sweep():
    from test.test_similarity_dataset import DATASET

    model = StaticModel.from_pretrained(MODEL_NAME)
    safety = SafetyValidator()

    sentences = []

    for item in DATASET:
        sentences.append(item["a"])
        sentences.append(item["b"])

    unique_sentences = list(dict.fromkeys(sentences))

    embeddings = model.encode(unique_sentences)

    embedding_map = {
        sentence: embedding
        for sentence, embedding in zip(
            unique_sentences,
            embeddings,
        )
    }

    results = []

    for item in DATASET:
        sentence_a = item["a"]
        sentence_b = item["b"]
        expected_duplicate = item["duplicate"]

        semantic_score = cosine_similarity(
            [embedding_map[sentence_a]],
            [embedding_map[sentence_b]],
        )[0][0]

        safety_ok = safety.is_safe_to_deduplicate(
            sentence_a,
            sentence_b,
        )

        results.append(
            {
                "a": sentence_a,
                "b": sentence_b,
                "expected": expected_duplicate,
                "semantic": float(semantic_score),
                "safety": safety_ok,
            }
        )

    thresholds = [
        0.60,
        0.65,
        0.70,
        0.75,
        0.80,
        0.85,
        0.90,
        0.95,
    ]

    print("\n")
    print("=" * 75)
    print("STRATEGY B — THRESHOLD SWEEP")
    print("=" * 75)

    for threshold in thresholds:

        tp = fp = tn = fn = 0

        for item in results:

            predicted = (
                item["semantic"] >= threshold
                and item["safety"]
            )

            expected = item["expected"]

            if predicted and expected:
                tp += 1

            elif predicted and not expected:
                fp += 1

            elif not predicted and expected:
                fn += 1

            else:
                tn += 1

        precision = (
            tp / (tp + fp)
            if tp + fp
            else 0
        )

        recall = (
            tp / (tp + fn)
            if tp + fn
            else 0
        )

        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0
        )

        fpr = (
            fp / (fp + tn)
            if fp + tn
            else 0
        )

        print(
            f"\n"
            f"threshold={threshold:.2f} | "
            f"precision={precision:.2%} | "
            f"recall={recall:.2%} | "
            f"f1={f1:.2%} | "
            f"fpr={fpr:.2%}"
        )

        print(
            f"TP={tp} "
            f"FP={fp} "
            f"FN={fn} "
            f"TN={tn}"
        )

    assert len(results) == len(DATASET)