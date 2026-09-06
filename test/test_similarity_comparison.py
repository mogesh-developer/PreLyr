import os
import time
from dataclasses import dataclass

# Disable HF transfer and xet client features to avoid download CAS Client errors on Windows/HF Hub
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"
os.environ["HF_HUB_DISABLE_XET"] = "1"

import numpy as np
from sentence_transformers import SentenceTransformer
from model2vec import StaticModel


# ---------------------------------------------------------
# Test data
# ---------------------------------------------------------

@dataclass
class SimilarityPair:
    first: str
    second: str
    duplicate: bool
    category: str


TEST_PAIRS = [

    # =====================================================
    # TRUE SEMANTIC DUPLICATES
    # =====================================================

    SimilarityPair(
        "The backend uses Flask.",
        "Flask is used as the backend.",
        True,
        "semantic_duplicate",
    ),

    SimilarityPair(
        "The server crashed because authentication failed.",
        "Authentication failure caused the server to crash.",
        True,
        "semantic_duplicate",
    ),

    SimilarityPair(
        "The user cannot log in because the token is invalid.",
        "Login fails when the authentication token is invalid.",
        True,
        "semantic_duplicate",
    ),

    SimilarityPair(
        "The database connection was successful.",
        "The application connected to the database successfully.",
        True,
        "semantic_duplicate",
    ),

    SimilarityPair(
        "The API returned a 401 error.",
        "The server responded with an unauthorized 401 status.",
        True,
        "semantic_duplicate",
    ),

    SimilarityPair(
        "The application is running on port 8000.",
        "Port 8000 is being used by the application.",
        True,
        "semantic_duplicate",
    ),

    # =====================================================
    # DIFFERENT INFORMATION
    # =====================================================

    SimilarityPair(
        "The backend uses Flask.",
        "The backend uses FastAPI.",
        False,
        "different_information",
    ),

    SimilarityPair(
        "The database uses PostgreSQL.",
        "The database uses MongoDB.",
        False,
        "different_information",
    ),

    SimilarityPair(
        "The API returned a 401 error.",
        "The API returned a 500 error.",
        False,
        "different_information",
    ),

    SimilarityPair(
        "The server is running on port 8000.",
        "The server is running on port 9000.",
        False,
        "different_information",
    ),

    SimilarityPair(
        "Authentication failed because the token was invalid.",
        "Authentication succeeded because the token was valid.",
        False,
        "different_information",
    ),

    SimilarityPair(
        "The frontend loaded successfully.",
        "The database connection failed.",
        False,
        "different_information",
    ),

    # =====================================================
    # SIMILAR WORDS BUT DIFFERENT MEANING
    # =====================================================

    SimilarityPair(
        "The backend uses Flask.",
        "The backend documentation explains Flask.",
        False,
        "similar_but_different",
    ),

    SimilarityPair(
        "The database connection failed.",
        "The database connection succeeded.",
        False,
        "similar_but_different",
    ),

    SimilarityPair(
        "The server started successfully.",
        "The server failed to start.",
        False,
        "similar_but_different",
    ),

    SimilarityPair(
        "The user created an account.",
        "The user deleted an account.",
        False,
        "similar_but_different",
    ),
]


# ---------------------------------------------------------
# Similarity
# ---------------------------------------------------------

def cosine_similarity(a, b):
    a = np.asarray(a)
    b = np.asarray(b)

    denominator = (
        np.linalg.norm(a)
        * np.linalg.norm(b)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(a, b) / denominator
    )


# ---------------------------------------------------------
# Model adapters
# ---------------------------------------------------------

class SentenceTransformerAdapter:

    name = "SentenceTransformer"

    def __init__(self):
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def encode(self, texts):
        return self.model.encode(
            texts,
            normalize_embeddings=True,
        )


class Model2VecAdapter:

    name = "Model2Vec"

    def __init__(self):
        self.model = StaticModel.from_pretrained(
            "minishlab/potion-base-8M"
        )

    def encode(self, texts):
        return self.model.encode(texts)


# ---------------------------------------------------------
# Benchmark
# ---------------------------------------------------------

def run_benchmark(adapter):

    print()
    print("=" * 70)
    print(adapter.name)
    print("=" * 70)

    true_scores = []
    false_scores = []

    start = time.perf_counter()

    for pair in TEST_PAIRS:

        embeddings = adapter.encode(
            [pair.first, pair.second]
        )

        score = cosine_similarity(
            embeddings[0],
            embeddings[1],
        )

        if pair.duplicate:
            true_scores.append(score)
        else:
            false_scores.append(score)

        print(
            f"\n[{pair.category}]"
            f"\nExpected duplicate : {pair.duplicate}"
            f"\nSimilarity          : {score:.4f}"
            f"\nA                   : {pair.first}"
            f"\nB                   : {pair.second}"
        )

    elapsed = time.perf_counter() - start

    print()
    print("-" * 70)
    print(f"Total inference time : {elapsed:.4f}s")

    print(
        f"Average TRUE score  : "
        f"{np.mean(true_scores):.4f}"
    )

    print(
        f"Average FALSE score : "
        f"{np.mean(false_scores):.4f}"
    )

    print(
        f"Minimum TRUE score  : "
        f"{np.min(true_scores):.4f}"
    )

    print(
        f"Maximum FALSE score : "
        f"{np.max(false_scores):.4f}"
    )

    return {
        "model": adapter.name,
        "time": elapsed,
        "true_scores": true_scores,
        "false_scores": false_scores,
    }


# ---------------------------------------------------------
# Threshold analysis
# ---------------------------------------------------------

def evaluate_thresholds(result):

    print()
    print("=" * 70)
    print(f"THRESHOLD ANALYSIS - {result['model']}")
    print("=" * 70)

    true_scores = result["true_scores"]
    false_scores = result["false_scores"]

    thresholds = [
        0.70,
        0.75,
        0.80,
        0.85,
        0.90,
        0.92,
        0.94,
        0.96,
    ]

    for threshold in thresholds:

        true_positive = sum(
            score >= threshold
            for score in true_scores
        )

        false_positive = sum(
            score >= threshold
            for score in false_scores
        )

        total_true = len(true_scores)
        total_false = len(false_scores)

        recall = (
            true_positive / total_true
            if total_true
            else 0
        )

        false_positive_rate = (
            false_positive / total_false
            if total_false
            else 0
        )

        print(
            f"\nThreshold: {threshold:.2f}"
            f"\n  Duplicate detection : "
            f"{true_positive}/{total_true}"
            f"\n  Recall              : "
            f"{recall:.2%}"
            f"\n  False positives     : "
            f"{false_positive}/{total_false}"
            f"\n  False positive rate  : "
            f"{false_positive_rate:.2%}"
        )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print()
    print("PRELYR SEMANTIC SIMILARITY COMPARISON")
    print("=" * 70)

    # -----------------------------------------------------
    # Model loading
    # -----------------------------------------------------

    print("\nLoading SentenceTransformer...")

    start = time.perf_counter()

    sentence_model = SentenceTransformerAdapter()

    sentence_load_time = (
        time.perf_counter() - start
    )

    print(
        f"SentenceTransformer load: "
        f"{sentence_load_time:.4f}s"
    )

    # -----------------------------------------------------

    print("\nLoading Model2Vec...")

    start = time.perf_counter()

    model2vec_model = Model2VecAdapter()

    model2vec_load_time = (
        time.perf_counter() - start
    )

    print(
        f"Model2Vec load: "
        f"{model2vec_load_time:.4f}s"
    )

    # -----------------------------------------------------
    # Run benchmarks
    # -----------------------------------------------------

    sentence_result = run_benchmark(
        sentence_model
    )

    model2vec_result = run_benchmark(
        model2vec_model
    )

    # -----------------------------------------------------
    # Threshold analysis
    # -----------------------------------------------------

    evaluate_thresholds(
        sentence_result
    )

    evaluate_thresholds(
        model2vec_result
    )

    # -----------------------------------------------------
    # Final comparison
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("FINAL COMPARISON")
    print("=" * 70)

    print(
        f"\nSentenceTransformer:"
        f"\n  Load time      : {sentence_load_time:.4f}s"
        f"\n  Inference time : {sentence_result['time']:.4f}s"
    )

    print(
        f"\nModel2Vec:"
        f"\n  Load time      : {model2vec_load_time:.4f}s"
        f"\n  Inference time : {model2vec_result['time']:.4f}s"
    )


if __name__ == "__main__":
    main()