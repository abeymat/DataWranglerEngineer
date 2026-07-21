from fastapi.testclient import TestClient

from app.main import create_app


def test_health_and_ready_endpoints() -> None:
    client = TestClient(create_app())

    health = client.get("/health")
    ready = client.get("/ready")

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert health.json()["openai_model"] == "gpt-5.6-sol"
    assert health.json()["openai_configured"] is False
    assert ready.status_code == 200
    assert ready.json() == {"status": "ready"}
