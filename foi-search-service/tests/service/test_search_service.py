import pytest
from unittest.mock import MagicMock, patch
from src.services.search_service import SearchService

@pytest.fixture
def mock_solr_client():
    mock = MagicMock()
    mock.collection = "test_collection"
    mock.solr_url = "http://localhost:8983/solr/test_collection"
    mock.ping.return_value = True
    mock.get_total_documents.return_value = 42
    mock.search_similarity.return_value = {
        "response": {
            "docs": [
                {"id": "1", "score": 0.85},
                {"id": "2", "score": 0.65},
            ],
            "numFound": 2,
        }
    }
    return mock

def test_init_with_client(mock_solr_client):
    service = SearchService(solr_client=mock_solr_client)
    assert service.solr_client == mock_solr_client

def test_init_without_client():
    with pytest.raises(ValueError):
        SearchService()

def test_search_by_vector_basic(mock_solr_client):
    service = SearchService(solr_client=mock_solr_client)
    result = service.search_by_vector([0.1, 0.2, 0.3])
    assert "response" in result
    assert len(result["response"]["docs"]) == 2

def test_search_by_vector_with_threshold(mock_solr_client):
    service = SearchService(solr_client=mock_solr_client)
    # Should filter out doc with score 0.65
    result = service.search_by_vector([0.1, 0.2, 0.3], similarity_threshold=0.8)
    assert len(result["response"]["docs"]) == 1
    assert result["response"]["docs"][0]["score"] >= 0.8

def test_search_by_vector_exception(monkeypatch, mock_solr_client):
    service = SearchService(solr_client=mock_solr_client)
    mock_solr_client.search_similarity.side_effect = Exception("Solr down")
    result = service.search_by_vector([0.1, 0.2, 0.3])
    assert "error" in result
    assert "Solr down" in result["error"]

def test_get_collection_stats(mock_solr_client):
    service = SearchService(solr_client=mock_solr_client)
    stats = service.get_collection_stats()
    assert stats["total_documents"] == 42
    assert stats["solr_collection"] == "test_collection"
    assert stats["solr_ping"] is True

def test_get_collection_stats_exception(mock_solr_client):
    service = SearchService(solr_client=mock_solr_client)
    mock_solr_client.get_total_documents.side_effect = Exception("Stats error")
    stats = service.get_collection_stats()
    assert "error" in stats
    assert "Stats error" in stats["error"]
