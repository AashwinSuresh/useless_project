"""
Automated unit & integration test suite for FastAPI backend endpoints.
"""
import sys
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data.get("status") == "ok"
    assert "version" in data
    print("[PASS] Health endpoint test passed.")


def test_validation_empty_query():
    res = client.post("/search", json={"query": "   "})
    assert res.status_code == 422
    print("[PASS] Empty query validation test passed.")


def test_validation_too_long_query():
    res = client.post("/search", json={"query": "a" * 501})
    assert res.status_code == 422
    print("[PASS] Long query validation test passed.")


def test_search_endpoint():
    res = client.post("/search", json={"query": "Why did my friend say okay?"})
    assert res.status_code == 200
    data = res.json()
    assert data["query"] == "Why did my friend say okay?"
    assert len(data["results"]) == 5
    # Verify probability normalization
    total_prob = sum(r["probability"] for r in data["results"])
    assert total_prob == 100, f"Expected total probability 100, got {total_prob}"
    # Verify absurdity scores
    for r in data["results"]:
        assert 0.0 <= r["absurdity"] <= 1.0
    # Verify recommendation and uselessness score
    assert "recommendation" in data
    assert 70 <= data["uselessness_score"] <= 99
    print("[PASS] Search endpoint test passed (Probabilities strictly sum to 100%, Absurdity valid, Score valid).")


if __name__ == "__main__":
    test_health_endpoint()
    test_validation_empty_query()
    test_validation_too_long_query()
    test_search_endpoint()
    print("\nALL API TESTS PASSED SUCCESSFULLY!")
