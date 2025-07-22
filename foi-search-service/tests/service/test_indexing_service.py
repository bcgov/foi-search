import pytest
from unittest.mock import MagicMock
from src.services.indexing_service import IndexingService
from src.schemas.models import TokenizationResult

@pytest.fixture
def mock_solr_client():
    mock = MagicMock()
    mock.collection = "test_collection"
    mock.solr_url = "http://localhost:8983/solr/test_collection"
    mock.ping.return_value = True
    mock.document_exists_by_hashes.return_value = {"hash1", "hash3"}
    mock.document_exists_by_hash.return_value = True
    mock.index_tokenization_result.return_value = True
    return mock

@pytest.fixture
def dummy_tokenization_result():
    return TokenizationResult(
        sentences=["foo", "bar"],
        embeddings=[[0.1, 0.2], [0.3, 0.4]],
        model_name="test-model",
        embedding_dimension=2,
        num_sentences=2,
        provider="dummy",
        tokens_used=10,
        cost_estimate=0.01
    )

def test_init_with_client(mock_solr_client):
    service = IndexingService(solr_client=mock_solr_client)
    assert service.solr_client == mock_solr_client

def test_init_without_client():
    with pytest.raises(ValueError):
        IndexingService()

def test_document_exists_by_hashes_success(mock_solr_client):
    service = IndexingService(solr_client=mock_solr_client)
    hashes = ["hash1", "hash2", "hash3"]
    result = service.document_exists_by_hashes(hashes)
    assert result == {
        "hash1": True,
        "hash2": False,
        "hash3": True,
    }

def test_document_exists_by_hashes_exception(mock_solr_client):
    service = IndexingService(solr_client=mock_solr_client)
    mock_solr_client.document_exists_by_hashes.side_effect = Exception("Solr error")
    result = service.document_exists_by_hashes(["hash1"])
    assert result == {}

def test_document_exists_by_hash_success(mock_solr_client):
    service = IndexingService(solr_client=mock_solr_client)
    mock_solr_client.document_exists_by_hash.return_value = True
    assert service.document_exists_by_hash("hash1") is True

def test_document_exists_by_hash_false(mock_solr_client):
    service = IndexingService(solr_client=mock_solr_client)
    mock_solr_client.document_exists_by_hash.return_value = False
    assert service.document_exists_by_hash("hash2") is False

def test_document_exists_by_hash_exception(mock_solr_client):
    service = IndexingService(solr_client=mock_solr_client)
    mock_solr_client.document_exists_by_hash.side_effect = Exception("Error!")
    assert service.document_exists_by_hash("hash1") is False

def test_index_tokenization_result_success(mock_solr_client, dummy_tokenization_result):
    service = IndexingService(solr_client=mock_solr_client)
    mock_solr_client.index_tokenization_result.return_value = True
    assert service.index_tokenization_result(dummy_tokenization_result) is True

def test_index_tokenization_result_failure(mock_solr_client, dummy_tokenization_result):
    service = IndexingService(solr_client=mock_solr_client)
    mock_solr_client.index_tokenization_result.return_value = False
    assert service.index_tokenization_result(dummy_tokenization_result) is False

def test_index_tokenization_result_exception(mock_solr_client, dummy_tokenization_result):
    service = IndexingService(solr_client=mock_solr_client)
    mock_solr_client.index_tokenization_result.side_effect = Exception("Index error")
    assert service.index_tokenization_result(dummy_tokenization_result) is False

def test_batch_index_results_all_success(mock_solr_client, dummy_tokenization_result):
    service = IndexingService(solr_client=mock_solr_client)
    mock_solr_client.index_tokenization_result.return_value = True
    results = [dummy_tokenization_result, dummy_tokenization_result]
    assert service.batch_index_results(results) is True

def test_batch_index_results_partial_failure(mock_solr_client, dummy_tokenization_result):
    service = IndexingService(solr_client=mock_solr_client)
    # First succeeds, second fails
    mock_solr_client.index_tokenization_result.side_effect = [True, False]
    results = [dummy_tokenization_result, dummy_tokenization_result]
    assert service.batch_index_results(results) is False

def test_get_indexing_stats(mock_solr_client):
    service = IndexingService(solr_client=mock_solr_client)
    stats = service.get_indexing_stats()
    assert stats["solr_connected"] is True
    assert stats["solr_collection"] == "test_collection"
    assert stats["solr_ping"] is True

def test_get_indexing_stats_no_client():
    service = IndexingService(solr_client=MagicMock())
    service.solr_client = None
    stats = service.get_indexing_stats()
    assert stats["solr_connected"] is False
    assert "solr_collection" not in stats
