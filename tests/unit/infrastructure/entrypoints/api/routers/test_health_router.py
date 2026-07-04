from fastapi import FastAPI
from fastapi.testclient import TestClient

from infrastructure.entrypoints.api.routers.health import router


def test_should_return_health_response() -> None:
    client = _client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)

    return TestClient(app)
