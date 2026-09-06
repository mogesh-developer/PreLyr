from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_optimize_clean_input():
    response = client.post(
        "/optimize",
        json={
            "text": "Explain what Flask is."
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["original_text"] == "Explain what Flask is."
    assert data["optimized_text"] == "Explain what Flask is."
    assert data["operations_applied"] == ["NO_OP"]


def test_optimize_redundant_input():
    response = client.post(
        "/optimize",
        json={
            "text": "Flask is used. Flask is used."
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["optimized_text"]
    assert "Flask" in data["optimized_text"]
    assert "DEDUPLICATE" in data["operations_applied"]


def test_optimize_returns_token_metrics():
    response = client.post(
        "/optimize",
        json={
            "text": "Flask is used. Flask is used."
        },
    )

    data = response.json()

    assert "original_tokens" in data
    assert "optimized_tokens" in data
    assert "token_reduction_percentage" in data

def test_generate_uses_prelyr_pipeline():
    response = client.post(
        "/generate",
        json={
            "text": "Flask is used. Flask is used."
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "response" in data
    assert "optimized_prompt" in data

    assert "Optimized Context" in data["optimized_prompt"]


def test_generate_preserves_clean_input():
    response = client.post(
        "/generate",
        json={
            "text": "Explain what Flask is."
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "Explain what Flask is." in data["optimized_prompt"]