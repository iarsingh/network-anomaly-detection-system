from fastapi.testclient import TestClient
from netanom.main import app

client = TestClient(app)


def test_high_and_low():
    assert client.post("/score", json={'error_rate': 0.4, 'p95_ms': 800, 'unique_dest': 90}).json()["label"]
    high = client.post("/score", json={'error_rate': 0.4, 'p95_ms': 800, 'unique_dest': 90}).json()
    low = client.post("/score", json={'error_rate': 0.01, 'p95_ms': 40, 'unique_dest': 4}).json()
    assert high["label"] != low["label"]
    assert high["score"] > low["score"]


def test_missing_is_refused():
    body = dict({'error_rate': 0.4, 'p95_ms': 800, 'unique_dest': 90})
    body.pop("error_rate")
    assert client.post("/score", json=body).status_code == 422
