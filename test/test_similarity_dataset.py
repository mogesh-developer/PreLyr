import time

import numpy as np
from model2vec import StaticModel
from sklearn.metrics import confusion_matrix
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = "minishlab/potion-base-8M"

DATASET = [
    # ---------------------------------------------------------
    # Simple / technical paraphrases
    # ---------------------------------------------------------
    {
        "a": "The backend uses Flask.",
        "b": "Flask is used as the backend framework.",
        "duplicate": True,
        "category": "technical_paraphrase",
        "critical": False,
    },
    {
        "a": "The database connection succeeded.",
        "b": "The application connected to the database successfully.",
        "duplicate": True,
        "category": "technical_paraphrase",
        "critical": False,
    },
    {
        "a": "Authentication failed because the token was invalid.",
        "b": "The login failed due to an invalid authentication token.",
        "duplicate": True,
        "category": "technical_paraphrase",
        "critical": False,
    },
    {
        "a": "The server crashed during startup.",
        "b": "The application failed while starting the server.",
        "duplicate": True,
        "category": "technical_paraphrase",
        "critical": False,
    },

    # ---------------------------------------------------------
    # Numbers changed
    # ---------------------------------------------------------
    {
        "a": "The server runs on port 8000.",
        "b": "The server runs on port 9000.",
        "duplicate": False,
        "category": "port_changed",
        "critical": True,
    },
    {
        "a": "The request timeout is 30 seconds.",
        "b": "The request timeout is 60 seconds.",
        "duplicate": False,
        "category": "number_changed",
        "critical": True,
    },
    {
        "a": "The application requires Python 3.11.",
        "b": "The application requires Python 3.12.",
        "duplicate": False,
        "category": "version_changed",
        "critical": True,
    },

    # ---------------------------------------------------------
    # HTTP status codes
    # ---------------------------------------------------------
    {
        "a": "The server returned a 401 error.",
        "b": "The server returned a 500 error.",
        "duplicate": False,
        "category": "status_code_changed",
        "critical": True,
    },
    {
        "a": "The API returned status code 404.",
        "b": "The API returned status code 403.",
        "duplicate": False,
        "category": "status_code_changed",
        "critical": True,
    },

    # ---------------------------------------------------------
    # Negation / opposite meaning
    # ---------------------------------------------------------
    {
        "a": "The authentication token is valid.",
        "b": "The authentication token is invalid.",
        "duplicate": False,
        "category": "negation",
        "critical": True,
    },
    {
        "a": "The database connection succeeded.",
        "b": "The database connection failed.",
        "duplicate": False,
        "category": "success_failure",
        "critical": True,
    },
    {
        "a": "The deployment completed successfully.",
        "b": "The deployment did not complete successfully.",
        "duplicate": False,
        "category": "negation",
        "critical": True,
    },

    # ---------------------------------------------------------
    # Technology changed
    # ---------------------------------------------------------
    {
        "a": "The backend uses Flask.",
        "b": "The backend uses FastAPI.",
        "duplicate": False,
        "category": "technology_changed",
        "critical": True,
    },
    {
        "a": "The database uses PostgreSQL.",
        "b": "The database uses MongoDB.",
        "duplicate": False,
        "category": "technology_changed",
        "critical": True,
    },

    # ---------------------------------------------------------
    # Same topic, different fact
    # ---------------------------------------------------------
    {
        "a": "The frontend is running correctly.",
        "b": "The frontend is returning an error.",
        "duplicate": False,
        "category": "same_topic_different_fact",
        "critical": True,
    },
    {
        "a": "The server started successfully.",
        "b": "The server stopped unexpectedly.",
        "duplicate": False,
        "category": "same_topic_different_fact",
        "critical": True,
    },
    {
        "a": "The user account was created successfully.",
        "b": "The user account was deleted successfully.",
        "duplicate": False,
        "category": "same_topic_different_fact",
        "critical": True,
    },

    # ---------------------------------------------------------
    # Similar but distinct
    # ---------------------------------------------------------
    {
        "a": "The application uses Flask for the backend.",
        "b": "The documentation explains how Flask works.",
        "duplicate": False,
        "category": "similar_but_distinct",
        "critical": False,
    },
    {
        "a": "The database connection failed.",
        "b": "The database migration completed.",
        "duplicate": False,
        "category": "similar_but_distinct",
        "critical": False,
    },
    {
        "a": "The server is running on port 8000.",
        "b": "The server exposes the health endpoint.",
        "duplicate": False,
        "category": "similar_but_distinct",
        "critical": False,
    },

    # ---------------------------------------------------------
    # Unrelated
    # ---------------------------------------------------------
    {
        "a": "The application returned a 500 error.",
        "b": "The weather is sunny today.",
        "duplicate": False,
        "category": "unrelated",
        "critical": False,
    },
    {
        "a": "The PostgreSQL database is unavailable.",
        "b": "The user interface uses responsive design.",
        "duplicate": False,
        "category": "unrelated",
        "critical": False,
    },

    # ---------------------------------------------------------
    # Exact duplicates
    # ---------------------------------------------------------
    {
        "a": "The backend uses Flask.",
        "b": "The backend uses Flask.",
        "duplicate": True,
        "category": "exact_duplicate",
        "critical": False,
    },
    {
        "a": "The database connection succeeded.",
        "b": "The database connection succeeded.",
        "duplicate": True,
        "category": "exact_duplicate",
        "critical": False,
    },
    {
        "a": "The server returned a 401 error.",
        "b": "The server returned a 401 error.",
        "duplicate": True,
        "category": "exact_duplicate",
        "critical": False,
    },
        # ---------------------------------------------------------
    # Additional technical paraphrases
    # ---------------------------------------------------------
    {
        "a": "The API request was rejected because authentication failed.",
        "b": "Authentication failure caused the API request to be rejected.",
        "duplicate": True,
        "category": "technical_paraphrase",
        "critical": False,
    },
    {
        "a": "The PostgreSQL connection was established successfully.",
        "b": "The application successfully connected to PostgreSQL.",
        "duplicate": True,
        "category": "technical_paraphrase",
        "critical": False,
    },
    {
        "a": "The server is listening for incoming requests.",
        "b": "The server is accepting incoming requests.",
        "duplicate": True,
        "category": "technical_paraphrase",
        "critical": False,
    },
    {
        "a": "The application failed to connect to Redis.",
        "b": "The application could not establish a Redis connection.",
        "duplicate": True,
        "category": "technical_paraphrase",
        "critical": False,
    },
    {
        "a": "The user was successfully authenticated.",
        "b": "Authentication of the user completed successfully.",
        "duplicate": True,
        "category": "technical_paraphrase",
        "critical": False,
    },
    {
        "a": "The API returned an unauthorized response.",
        "b": "The API responded with an authentication failure.",
        "duplicate": True,
        "category": "technical_paraphrase",
        "critical": False,
    },

    # ---------------------------------------------------------
    # Port / number changes
    # ---------------------------------------------------------
    {
        "a": "The development server is running on port 3000.",
        "b": "The development server is running on port 4000.",
        "duplicate": False,
        "category": "port_changed",
        "critical": True,
    },
    {
        "a": "The application listens on port 8080.",
        "b": "The application listens on port 8081.",
        "duplicate": False,
        "category": "port_changed",
        "critical": True,
    },
    {
        "a": "The retry limit is 3 attempts.",
        "b": "The retry limit is 5 attempts.",
        "duplicate": False,
        "category": "number_changed",
        "critical": True,
    },
    {
        "a": "The maximum request size is 10 MB.",
        "b": "The maximum request size is 20 MB.",
        "duplicate": False,
        "category": "number_changed",
        "critical": True,
    },
    {
        "a": "The cache expires after 300 seconds.",
        "b": "The cache expires after 600 seconds.",
        "duplicate": False,
        "category": "number_changed",
        "critical": True,
    },

    # ---------------------------------------------------------
    # Version changes
    # ---------------------------------------------------------
    {
        "a": "The project uses Node.js 20.",
        "b": "The project uses Node.js 22.",
        "duplicate": False,
        "category": "version_changed",
        "critical": True,
    },
    {
        "a": "The application requires PostgreSQL 15.",
        "b": "The application requires PostgreSQL 16.",
        "duplicate": False,
        "category": "version_changed",
        "critical": True,
    },
    {
        "a": "The service depends on Python 3.10.",
        "b": "The service depends on Python 3.11.",
        "duplicate": False,
        "category": "version_changed",
        "critical": True,
    },

    # ---------------------------------------------------------
    # HTTP status changes
    # ---------------------------------------------------------
    {
        "a": "The endpoint returned HTTP 200.",
        "b": "The endpoint returned HTTP 201.",
        "duplicate": False,
        "category": "status_code_changed",
        "critical": True,
    },
    {
        "a": "The API returned HTTP 400.",
        "b": "The API returned HTTP 422.",
        "duplicate": False,
        "category": "status_code_changed",
        "critical": True,
    },
    {
        "a": "The server responded with status 503.",
        "b": "The server responded with status 504.",
        "duplicate": False,
        "category": "status_code_changed",
        "critical": True,
    },

    # ---------------------------------------------------------
    # Negation / state changes
    # ---------------------------------------------------------
    {
        "a": "The feature is enabled.",
        "b": "The feature is disabled.",
        "duplicate": False,
        "category": "state_changed",
        "critical": True,
    },
    {
        "a": "The cache is enabled in production.",
        "b": "The cache is disabled in production.",
        "duplicate": False,
        "category": "state_changed",
        "critical": True,
    },
    {
        "a": "The request was accepted.",
        "b": "The request was rejected.",
        "duplicate": False,
        "category": "state_changed",
        "critical": True,
    },
    {
        "a": "The service is healthy.",
        "b": "The service is unhealthy.",
        "duplicate": False,
        "category": "negation",
        "critical": True,
    },

    # ---------------------------------------------------------
    # Different technologies
    # ---------------------------------------------------------
    {
        "a": "The API is implemented with Flask.",
        "b": "The API is implemented with Django.",
        "duplicate": False,
        "category": "technology_changed",
        "critical": True,
    },
    {
        "a": "The application uses Redis for caching.",
        "b": "The application uses Memcached for caching.",
        "duplicate": False,
        "category": "technology_changed",
        "critical": True,
    },
    {
        "a": "The frontend is built with React.",
        "b": "The frontend is built with Vue.",
        "duplicate": False,
        "category": "technology_changed",
        "critical": True,
    },
    {
        "a": "The API uses REST.",
        "b": "The API uses GraphQL.",
        "duplicate": False,
        "category": "technology_changed",
        "critical": True,
    },

    # ---------------------------------------------------------
    # Different facts about the same subject
    # ---------------------------------------------------------
    {
        "a": "The database backup completed successfully.",
        "b": "The database backup failed.",
        "duplicate": False,
        "category": "success_failure",
        "critical": True,
    },
    {
        "a": "The deployment started successfully.",
        "b": "The deployment failed during startup.",
        "duplicate": False,
        "category": "success_failure",
        "critical": True,
    },
    {
        "a": "The API key was generated.",
        "b": "The API key was revoked.",
        "duplicate": False,
        "category": "same_topic_different_fact",
        "critical": True,
    },
    {
        "a": "The configuration file was loaded.",
        "b": "The configuration file was ignored.",
        "duplicate": False,
        "category": "same_topic_different_fact",
        "critical": True,
    },

    # ---------------------------------------------------------
    # Similar wording but different meaning
    # ---------------------------------------------------------
    {
        "a": "The server restarted after the deployment.",
        "b": "The server was restarted before the deployment.",
        "duplicate": False,
        "category": "temporal_difference",
        "critical": True,
    },
    {
        "a": "The user created a new account.",
        "b": "The administrator created a new account.",
        "duplicate": False,
        "category": "actor_changed",
        "critical": True,
    },
    {
        "a": "The application reads configuration from environment variables.",
        "b": "The application writes configuration to environment variables.",
        "duplicate": False,
        "category": "action_changed",
        "critical": True,
    },

    # ---------------------------------------------------------
    # Distinct but related information
    # ---------------------------------------------------------
    {
        "a": "The backend uses Flask.",
        "b": "The backend exposes a REST API.",
        "duplicate": False,
        "category": "related_distinct",
        "critical": False,
    },
    {
        "a": "The PostgreSQL database is running.",
        "b": "The PostgreSQL database contains user records.",
        "duplicate": False,
        "category": "related_distinct",
        "critical": False,
    },
    {
        "a": "The authentication service validates tokens.",
        "b": "The authentication service stores user sessions.",
        "duplicate": False,
        "category": "related_distinct",
        "critical": False,
    },
]


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


def calculate_metrics(y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[False, True],
    ).ravel()

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
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr,
    }


def test_model2vec_similarity_dataset():
    print("\nLoading Model2Vec...")

    start = time.perf_counter()

    model = StaticModel.from_pretrained(MODEL_NAME)

    load_time = time.perf_counter() - start

    print(f"Model load time: {load_time:.4f}s")
    print(f"Dataset size: {len(DATASET)} pairs")

    # Encode every unique sentence only once.
    sentences = list(
        dict.fromkeys(
            sentence
            for pair in DATASET
            for sentence in (pair["a"], pair["b"])
        )
    )

    start = time.perf_counter()

    embeddings = model.encode(sentences)

    inference_time = time.perf_counter() - start

    embedding_map = {
        sentence: embedding
        for sentence, embedding in zip(
            sentences,
            embeddings,
        )
    }

    print(f"Embedding time: {inference_time:.4f}s")
    print(f"Unique sentences: {len(sentences)}")

    similarities = []

    for pair in DATASET:
        score = cosine_similarity(
            [embedding_map[pair["a"]]],
            [embedding_map[pair["b"]]],
        )[0][0]

        similarities.append(
            {
                **pair,
                "score": float(score),
            }
        )

    print("\nThreshold evaluation")
    print("-" * 80)

    for threshold in THRESHOLDS:
        y_true = [
            item["duplicate"]
            for item in similarities
        ]

        y_pred = [
            item["score"] >= threshold
            for item in similarities
        ]

        metrics = calculate_metrics(
            y_true,
            y_pred,
        )

        critical_false_positives = sum(
            1
            for item in similarities
            if item["critical"]
            and item["score"] >= threshold
            and not item["duplicate"]
        )

        print(
            f"threshold={threshold:.2f} | "
            f"precision={metrics['precision']:.2%} | "
            f"recall={metrics['recall']:.2%} | "
            f"f1={metrics['f1']:.2%} | "
            f"fpr={metrics['fpr']:.2%} | "
            f"critical_fp={critical_false_positives}"
        )

    print("\nPair scores")
    print("-" * 80)

    for item in similarities:
        print(
            f"{item['score']:.4f} | "
            f"{str(item['duplicate']):5} | "
            f"{item['category']:25} | "
            f"{item['a']}  <->  {item['b']}"
        )

        