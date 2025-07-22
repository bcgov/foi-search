import pytest
from fastapi.testclient import TestClient
from src.api.server import app

def test_root():
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert "health" in data

def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert isinstance(data["uptime"], (int, float))
    assert data["uptime"] >= 0

def test_models(monkeypatch):
    client = TestClient(app)
    class Provider:
        model_name = "mock-model"
        provider_name = "mock-provider"
        embedding_dimension = 384
    class MockConfig:
        provider = Provider()
    monkeypatch.setattr("src.config.get_config", lambda: MockConfig())
    r = client.get("/models")
    assert r.status_code == 200
    data = r.json()
    assert data["current_model"] == "mock-model"
    assert data["provider"] == "mock-provider"
    assert data["embedding_dimension"] == 384
