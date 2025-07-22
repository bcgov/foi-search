import pytest
from unittest.mock import MagicMock
import numpy as np
from src.services.document_service import DocumentService
from src.schemas.models import TokenizationResult

@pytest.fixture
def mock_tokenizer():
    mock = MagicMock()
    # embedding_sentences returns a TokenizationResult with one or more embeddings
    mock.embedding_sentences.return_value = TokenizationResult(
        sentences=["sentence1"],
        embeddings=np.array([[0.1, 0.2, 0.3]]),
        model_name="test-model",
        embedding_dimension=3,
        num_sentences=1,
        provider="dummy",
        tokens_used=5,
        cost_estimate=0.001
    )
    # embedding_sentence returns a TokenizationResult for one sentence
    mock.embedding_sentence.return_value = TokenizationResult(
        sentences=["sentence1"],
        embeddings=np.array([[0.1, 0.2, 0.3]]),
        model_name="test-model",
        embedding_dimension=3,
        num_sentences=1,
        provider="dummy",
        tokens_used=5,
        cost_estimate=0.001
    )
    return mock

@pytest.fixture
def mock_indexing_service():
    mock = MagicMock()
    # document_exists_by_hashes returns all as not existing by default
    mock.document_exists_by_hashes.return_value = {}
    mock.index_tokenization_result.return_value = True
    return mock

@pytest.fixture
def mock_search_service():
    mock = MagicMock()
    mock.search_by_vector.return_value = {
        "response": {
            "docs": [{"id": "doc1", "score": 0.99}],
            "numFound": 1,
        }
    }
    return mock

@pytest.fixture
def doc_service(mock_tokenizer, mock_indexing_service, mock_search_service):
    return DocumentService(
        tokenization_service=mock_tokenizer,
        indexing_service=mock_indexing_service,
        search_service=mock_search_service,
    )

def test_tokenize_and_index_new_sentences(doc_service, mock_tokenizer, mock_indexing_service):
    # Only new sentences (none exist in Solr)
    sentences = ["this is a test"]
    res = doc_service.tokenize_and_index(sentences)
    assert isinstance(res, TokenizationResult)
    assert mock_tokenizer.embedding_sentences.called
    assert mock_indexing_service.index_tokenization_result.called

def test_tokenize_and_index_no_new_sentences(doc_service, mock_indexing_service):
    # All sentences exist (simulate Solr response)
    doc_service.indexing_service.document_exists_by_hashes.return_value = {
        doc_service._generate_sentence_hash("foo"): True
    }
    res = doc_service.tokenize_and_index(["foo"])
    assert isinstance(res, TokenizationResult)
    assert res.num_sentences == 0
    assert not mock_indexing_service.index_tokenization_result.called

def test_tokenize_and_index_single_sentence(doc_service, mock_tokenizer, mock_indexing_service):
    sentence = "only one sentence"
    res = doc_service.tokenize_and_index_single_sentence(sentence)
    assert isinstance(res, TokenizationResult)
    assert mock_tokenizer.embedding_sentence.called
    assert mock_indexing_service.index_tokenization_result.called

def test_tokenize_and_index_single_sentence_index_fails(doc_service, mock_tokenizer, mock_indexing_service):
    mock_indexing_service.index_tokenization_result.return_value = False
    sentence = "fail this index"
    res = doc_service.tokenize_and_index_single_sentence(sentence)
    assert isinstance(res, TokenizationResult)
    assert mock_tokenizer.embedding_sentence.called

def test_search_similarity(doc_service, mock_tokenizer, mock_search_service):
    result = doc_service.search_similarity("find similar", num_results=5, similarity_threshold=0.8)
    assert "response" in result
    assert mock_tokenizer.embedding_sentences.called
    assert mock_search_service.search_by_vector.called

def test_batch_process_texts(doc_service, mock_tokenizer, mock_indexing_service):
    texts = [f"text {i}" for i in range(10)]
    results = doc_service.batch_process_texts(texts, batch_size=5)
    assert isinstance(results, list)
    assert all(isinstance(res, TokenizationResult) for res in results)
    assert mock_tokenizer.embedding_sentences.call_count == 2
    assert mock_indexing_service.index_tokenization_result.call_count == 2

def test_batch_process_texts_partial_failure(doc_service, mock_tokenizer, mock_indexing_service):
    # Simulate failure for the first batch, success for the second
    mock_indexing_service.index_tokenization_result.side_effect = [False, True]
    texts = [f"text {i}" for i in range(10)]
    results = doc_service.batch_process_texts(texts, batch_size=5)
    assert len(results) == 1  # Only second batch succeeded
