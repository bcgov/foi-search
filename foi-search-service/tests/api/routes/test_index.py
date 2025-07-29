import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from src.api.routers.index import router
from src.services.document_service import DocumentService
from src.api.dependencies.dependencies import get_document_service
from src.auth.keycloak_auth import keycloak_auth
from src.api.routers.index import security

app = FastAPI()
app.include_router(router)

@pytest.fixture(autouse=True)
def clear_service_cache():
    get_document_service.cache_clear()
    yield
    get_document_service.cache_clear()

class FakeCredentials:
    # Mimic fastapi.security.HTTPAuthorizationCredentials
    def __init__(self):
        self.scheme = "Bearer"
        self.credentials = "test-token"

def fake_security():
    return FakeCredentials()

@patch("src.api.dependencies.dependencies.create_document_service")
def test_add_documents_success(mock_create_document_service):
    mock_service = MagicMock(spec=DocumentService)
    mock_service.tokenize_and_index.return_value.num_sentences = 1
    mock_create_document_service.return_value = mock_service
    app.dependency_overrides[security] = fake_security

    client = TestClient(app)
    response = client.post("/index/add", json={"sentences": ["foo"], "metadata": {}})
    assert response.status_code == 200
    data = response.json()
    assert data["documents_added"] == 1

@patch("src.api.dependencies.dependencies.create_document_service")
def test_add_documents_validation_exception(mock_create_document_service):
    from src.api.exceptions.exceptions import ValidationException

    mock_service = MagicMock(spec=DocumentService)
    mock_service.tokenize_and_index.side_effect = ValidationException("Bad data")
    mock_create_document_service.return_value = mock_service
    app.dependency_overrides[security] = fake_security

    client = TestClient(app)
    payload = {"sentences": ["test"], "metadata": {}}
    response = client.post("/index/add", json=payload)
    assert response.status_code == 400
    assert "Bad data" in response.json()["detail"]

@patch("src.api.dependencies.dependencies.create_document_service")
def test_add_documents_internal_error(mock_create_document_service):
    mock_service = MagicMock(spec=DocumentService)
    mock_service.tokenize_and_index.side_effect = Exception("Oops!")
    mock_create_document_service.return_value = mock_service
    app.dependency_overrides[security] = fake_security

    client = TestClient(app)
    payload = {"sentences": ["foo"], "metadata": {}}
    response = client.post("/index/add", json=payload)
    assert response.status_code == 500
    assert "Oops!" in response.json()["detail"]

@patch("src.api.dependencies.dependencies.create_document_service")
def test_semantic_search_success(mock_create_document_service):
    mock_service = MagicMock(spec=DocumentService)
    mock_service.search_similarity.return_value = {
        "response": {
            "numFound": 1,
            "start": 0,
            "maxScore": 0.9,
            "numFoundExact": True,
            "docs": [
                {
                    "id": "test_id",
                    "sentence": ["sentence"],
                    "score": 0.95,
                    "meta_source": "unit-test"
                }
            ]
        }
    }
    mock_create_document_service.return_value = mock_service

    app.dependency_overrides[security] = fake_security

    client = TestClient(app)
    payload = {"query": "query here", "top_k": 1, "threshold": 0.5}
    response = client.post("/index/semantic-search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["numFound"] == 1
    assert data["docs"][0]["id"] == "test_id"
    assert data["docs"][0]["sentence"] == "sentence"
    assert data["docs"][0]["score"] == 0.95
    assert data["docs"][0]["source"] == "unit-test"

@patch("src.api.dependencies.dependencies.create_document_service")
def test_semantic_search_empty_query(mock_create_document_service):
    mock_service = MagicMock(spec=DocumentService)
    mock_create_document_service.return_value = mock_service
    app.dependency_overrides[security] = fake_security

    client = TestClient(app)
    payload = {"query": "", "top_k": 1, "threshold": 0.5}
    response = client.post("/index/semantic-search", json=payload)
    assert response.status_code == 400
    assert "Query cannot be empty" in response.json()["detail"]

@patch("src.api.dependencies.dependencies.create_document_service")
def test_semantic_search_internal_error(mock_create_document_service):
    mock_service = MagicMock(spec=DocumentService)
    mock_service.search_similarity.side_effect = Exception("DB fail")
    mock_create_document_service.return_value = mock_service
    app.dependency_overrides[security] = fake_security

    client = TestClient(app)
    payload = {"query": "something", "top_k": 1, "threshold": 0.5}
    response = client.post("/index/semantic-search", json=payload)
    assert response.status_code == 500
    assert "DB fail" in response.json()["detail"]
