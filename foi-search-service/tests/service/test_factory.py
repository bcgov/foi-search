import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_config():
    class ProviderConfig:
        model_name = "test-model"
    class TokenConfig:
        max_token_length = 100
        max_words_length = 20
        token_char_estimate = 2
    class SolrConfig:
        solr_url = "http://localhost:8983/solr"
        collection = "test_collection"
        timeout = 10
        max_retries = 3
        retry_delay = 1
        username = "admin"
        password = "pass"
        verify_ssl = True
        document_id_prefix = "doc"
    class Config:
        provider = ProviderConfig()
        tokenization = TokenConfig()
        solr = SolrConfig()
    return Config()

@patch("src.services.factory.get_config")
@patch("src.clients.solr_client.SolrClient")
@patch("src.sbert_sentence_tokenizer.SBERTSentenceTokenizer")
def test_create_document_service_success(
    mock_tokenizer_cls, mock_solr_cls, mock_get_config, mock_config
):

    import importlib
    import src.services.factory as factory_module
    importlib.reload(factory_module)

    # Mock config
    mock_get_config.return_value = mock_config

    # Mock tokenizer and solr client instances
    mock_tokenizer = MagicMock()
    mock_tokenizer_cls.return_value = mock_tokenizer
    mock_solr_client = MagicMock()
    mock_solr_client.ping.return_value = True
    mock_solr_cls.return_value = mock_solr_client

    # Run factory
    from src.services.factory import create_document_service
    doc_service = create_document_service()

    assert hasattr(doc_service, "tokenization_service")
    assert hasattr(doc_service, "indexing_service")
    assert hasattr(doc_service, "search_service")
    mock_tokenizer_cls.assert_called_once()
    mock_solr_cls.assert_called_once()
    assert doc_service.tokenization_service is mock_tokenizer
    assert doc_service.indexing_service.solr_client is mock_solr_client
    assert doc_service.search_service.solr_client is mock_solr_client

@patch("src.services.factory.get_config")
@patch("src.clients.solr_client.SolrClient")
@patch("src.sbert_sentence_tokenizer.SBERTSentenceTokenizer")
def test_create_document_service_solr_ping_fails(
    mock_tokenizer_cls, mock_solr_cls, mock_get_config, mock_config
):
    import importlib
    import src.services.factory as factory_module
    importlib.reload(factory_module)

    mock_get_config.return_value = mock_config
    mock_tokenizer_cls.return_value = MagicMock()
    mock_solr_client = MagicMock()
    mock_solr_client.ping.return_value = False
    mock_solr_cls.return_value = mock_solr_client

    with pytest.raises(ConnectionError) as ex:
        factory_module.create_document_service()
    assert "Failed to connect to Solr" in str(ex.value)
