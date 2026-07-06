import os

os.environ["ENABLE_BACKGROUND_WORKERS"] = "false"

from fastapi.testclient import TestClient

from src.config.settings import get_settings

get_settings.cache_clear()

from src.main import app


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
