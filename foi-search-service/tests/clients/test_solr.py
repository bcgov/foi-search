import pytest
from unittest.mock import patch, MagicMock
from src.clients.solr_client import SolrClient

@pytest.fixture
def solr_client():
    return SolrClient(
        solr_url="http://localhost:8983/solr",
        collection="test_collection",
        timeout=1,
        max_retries=1,
        retry_delay=0
    )

@patch("src.clients.solr_client.requests.request")
def test_ping_success(mock_request, solr_client):
    response = MagicMock()
    response.status_code = 200
    mock_request.return_value = response
    assert solr_client.ping() is True

@patch("src.clients.solr_client.requests.request")
def test_ping_failure(mock_request, solr_client):
    mock_request.side_effect = Exception("Connection error")
    assert solr_client.ping() is False

@patch("src.clients.solr_client.SolrClient._make_request")
def test_index_documents_success(mock_make_request, solr_client):
    mock_response = MagicMock()
    mock_make_request.return_value = mock_response
    docs = [{"id": "1", "sentence": "foo"}]
    assert solr_client.index_documents(docs) is True

@patch("src.clients.solr_client.SolrClient._make_request")
def test_index_documents_exception(mock_make_request, solr_client):
    mock_make_request.side_effect = Exception("Solr error")
    docs = [{"id": "1", "sentence": "foo"}]
    assert solr_client.index_documents(docs) is False

def test_add_additional_fields(solr_client):
    doc = {"id": "1"}
    extra = {"foo": "bar"}
    updated = solr_client.add_additional_fields(doc, extra)
    assert updated["meta_foo"] == "bar"

def test_generate_sentence_hash(solr_client):
    h1 = solr_client._generate_sentence_hash("test sentence")
    h2 = solr_client._generate_sentence_hash("test sentence")
    h3 = solr_client._generate_sentence_hash("other sentence")
    assert isinstance(h1, str)
    assert h1 == h2
    assert h1 != h3

@patch("src.clients.solr_client.SolrClient.index_documents")
def test_index_tokenization_result_success(mock_index_docs, solr_client):
    mock_index_docs.return_value = True
    class FakeTokenizationResult:
        sentences = ["foo"]
        embeddings = [[0.1, 0.2]]
        model_name = "test"
        provider = "test"
        embedding_dimension = 2
        tokens = None
        input_ids = None
        attention_mask = None
        tokens_used = 123
        cost_estimate = 1.23
        num_sentences = 1
    result = FakeTokenizationResult()
    assert solr_client.index_tokenization_result(result) is True

@patch("src.clients.solr_client.SolrClient.index_documents")
def test_index_tokenization_result_failure(mock_index_docs, solr_client):
    mock_index_docs.return_value = False
    class FakeTokenizationResult:
        sentences = ["foo"]
        embeddings = [[0.1, 0.2]]
        model_name = "test"
        provider = "test"
        embedding_dimension = 2
        tokens = None
        input_ids = None
        attention_mask = None
        tokens_used = 123
        cost_estimate = 1.23
        num_sentences = 1
    result = FakeTokenizationResult()
    assert solr_client.index_tokenization_result(result) is False

@patch("src.clients.solr_client.SolrClient._make_request")
def test_search_similarity_success(mock_make_request, solr_client):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"response": {"docs": []}}
    mock_make_request.return_value = mock_resp
    result = solr_client.search_similarity([0.1, 0.2, 0.3])
    assert "response" in result

@patch("src.clients.solr_client.SolrClient._make_request")
def test_document_exists_by_hashes(mock_make_request, solr_client):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"response": {"docs": [{"sentence_hash": "abc"}]}}
    mock_make_request.return_value = mock_resp
    exists = solr_client.document_exists_by_hashes(["abc", "def"])
    assert "abc" in exists

@patch("src.clients.solr_client.SolrClient._make_request")
def test_document_exists_by_hash(mock_make_request, solr_client):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"response": {"docs": [{"id": "1"}]}}
    mock_make_request.return_value = mock_resp
    assert solr_client.document_exists_by_hash("abc") is True

@patch("src.clients.solr_client.SolrClient._make_request")
def test_document_exists_by_hash_false(mock_make_request, solr_client):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"response": {"docs": []}}
    mock_make_request.return_value = mock_resp
    assert solr_client.document_exists_by_hash("abc") is False

@patch("src.clients.solr_client.SolrClient._make_request")
def test_get_total_documents(mock_make_request, solr_client):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"response": {"numFound": 5}}
    mock_make_request.return_value = mock_resp
    assert solr_client.get_total_documents() == 5

@patch("src.clients.solr_client.SolrClient._make_request")
def test_delete_by_query_success(mock_make_request, solr_client):
    mock_make_request.return_value = MagicMock()
    assert solr_client.delete_by_query("foo:bar") is True

@patch("src.clients.solr_client.SolrClient._make_request")
def test_delete_by_query_failure(mock_make_request, solr_client):
    mock_make_request.side_effect = Exception("delete error")
    assert solr_client.delete_by_query("foo:bar") is False

@patch("src.clients.solr_client.SolrClient._make_request")
def test_commit_success(mock_make_request, solr_client):
    mock_make_request.return_value = MagicMock()
    assert solr_client.commit() is True

@patch("src.clients.solr_client.SolrClient._make_request")
def test_commit_failure(mock_make_request, solr_client):
    mock_make_request.side_effect = Exception("commit error")
    assert solr_client.commit() is False

@patch("src.clients.solr_client.SolrClient._make_request")
def test_optimize_success(mock_make_request, solr_client):
    mock_make_request.return_value = MagicMock()
    assert solr_client.optimize() is True

@patch("src.clients.solr_client.SolrClient._make_request")
def test_optimize_failure(mock_make_request, solr_client):
    mock_make_request.side_effect = Exception("optimize error")
    assert solr_client.optimize() is False

@patch("src.clients.solr_client.SolrClient._make_request")
def test_get_collection_info_success(mock_make_request, solr_client):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"collections": {}}
    mock_make_request.return_value = mock_resp
    info = solr_client.get_collection_info()
    assert "collections" in info

@patch("src.clients.solr_client.SolrClient._make_request")
def test_get_collection_info_failure(mock_make_request, solr_client):
    mock_make_request.side_effect = Exception("info error")
    info = solr_client.get_collection_info()
    assert "error" in info

@patch("src.clients.solr_client.SolrClient.ping")
def test_validate_connection_true(mock_ping):
    mock_ping.return_value = True
    assert SolrClient.validate_connection("http://localhost:8983/solr", "test_collection") is True

@patch("src.clients.solr_client.SolrClient.ping")
def test_validate_connection_false(mock_ping):
    mock_ping.return_value = False
    assert SolrClient.validate_connection("http://localhost:8983/solr", "test_collection") is False

@patch("src.clients.solr_client.SolrClient.ping")
def test_validate_connection_exception(mock_ping):
    mock_ping.side_effect = Exception("no conn")
    assert SolrClient.validate_connection("http://localhost:8983/solr", "test_collection") is False
