import pytest
import json
from schemas.models import EmbeddingResult
from dummy_provider import DummyProvider
from config import ProviderConfig

@pytest.fixture
def dummy_provider():
    # Create a simple config-like object that bypasses ProviderConfig environment loading
    class TestConfig:
        def __init__(self):
            self.provider_name = "dummy"
            self.model_name = "dummy-model"
            self.embedding_dimension = 384
            self.max_tokens = 256
            self.cost_per_1k_tokens = 0.0
            self.cost_per_1m_tokens = 0.0
            self.supports_batch = True
            self.api_key = None
            self.additional_params = {}
            self.api_base_url = None
            self.max_retries = 3
            self.retry_delay = 1.0
            self.max_batch_size = 100
            self.timeout = 30.0
    
    config = TestConfig()
    return DummyProvider(provider_config=config)


def test_estimate_cost(dummy_provider):
    sentences = ["This is a test.", "Another sentence."]
    cost = dummy_provider.estimate_cost(sentences)
    assert cost is not None
    assert isinstance(cost, float)

def test_estimate_cost_empty(dummy_provider):
    # Create a test config with zero cost
    class ZeroCostConfig:
        def __init__(self):
            self.provider_name = "test-provider"
            self.model_name = "test-model"
            self.embedding_dimension = 128
            self.max_tokens = 128
            self.cost_per_1k_tokens = 0.0
            self.cost_per_1m_tokens = 0.0
            self.supports_batch = True
            self.api_key = None
            self.additional_params = {}
            self.api_base_url = None
            self.max_retries = 3
            self.retry_delay = 1.0
            self.max_batch_size = 100
            self.timeout = 30.0

    provider = DummyProvider(provider_config=ZeroCostConfig())

    sentences = ["This is a Cost test.", "Another sentence."]
    cost = provider.estimate_cost(sentences)
    assert cost == 0.0

def test_estimate_cost_none(dummy_provider):
    # Create a test config with None cost
    class NoneCostConfig:
        def __init__(self):
            self.provider_name = "test-provider"
            self.model_name = "test-model"
            self.embedding_dimension = 128
            self.max_tokens = 128
            self.cost_per_1k_tokens = None
            self.cost_per_1m_tokens = None
            self.supports_batch = True
            self.api_key = None
            self.additional_params = {}
            self.api_base_url = None
            self.max_retries = 3
            self.retry_delay = 1.0
            self.max_batch_size = 100
            self.timeout = 30.0

    provider = DummyProvider(provider_config=NoneCostConfig())

    sentences = ["This is a Cost test.", "Another sentence."]
    cost = provider.estimate_cost(sentences)
    assert cost == 0.0


def test_validate_sentences(dummy_provider):
    sentences = ["valid sentence", "", "    ", None, "word " * 60]
    valid, indices, rejected, summary = dummy_provider.validate_sentences(
        sentences
    )
    assert isinstance(valid, list)
    assert isinstance(indices, list)
    assert isinstance(rejected, list)
    assert isinstance(summary, dict)

def test_validate_sentences_with_custom_limits(dummy_provider):
    sentences = ["valid sentence", "", "    ", None, "word " * 60]
    valid, indices, rejected, summary = dummy_provider.validate_sentences(
        sentences=sentences,
        max_token_length=100,
        max_words_length=50
    )
    assert isinstance(valid, list)
    assert isinstance(indices, list)
    assert isinstance(rejected, list)
    assert isinstance(summary, dict)

def test_encode_sentences(dummy_provider):
    result = dummy_provider.encode_sentences(["Hello", "world"])
    assert isinstance(result, EmbeddingResult)
    assert result.embeddings.shape == (2, 384)


def test_encode_single_sentence(dummy_provider):
    result = dummy_provider.encode_sentence("Hello")
    assert isinstance(result, EmbeddingResult)
    assert result.embeddings.shape == (1, 384)


def test_provider_info(dummy_provider):
    info = dummy_provider.get_provider_info()
    assert info.provider_name == "dummy"
    assert info.embedding_dimension == 384

def test_log_usage_logs_expected_json(caplog):
    # Arrange
    class TestLogConfig:
        def __init__(self):
            self.provider_name = "dummy"
            self.model_name = "dummy-model"
            self.embedding_dimension = 384
            self.max_tokens = 256
            self.cost_per_1k_tokens = 0.01
            self.cost_per_1m_tokens = 0.01
            self.supports_batch = True
            self.api_key = None
            self.additional_params = {}
            self.api_base_url = None
            self.max_retries = 3
            self.retry_delay = 1.0
            self.max_batch_size = 100
            self.timeout = 30.0
    
    provider = DummyProvider(provider_config=TestLogConfig())
    sentences = ["This is a test sentence.", "Another sentence."]

    # Act
    with caplog.at_level(20, logger="tokenembed"):
        provider.log_usage(sentences)

    # Assert
    # Find the JSON log message
    log_json = None
    for record in caplog.records:
        if "embedding_usage" in record.message:
            try:
                # Find the first `{` and parse from there
                json_start = record.message.index('{')
                log_json = json.loads(record.message[json_start:])
                break
            except (ValueError, json.JSONDecodeError):
                pass

    assert log_json is not None, "Expected embedding_usage log not found"
    assert log_json["event"] == "embedding_usage"
    assert log_json["provider"] == "dummy"
    assert log_json["model"] == "dummy-model"
    assert log_json["sentences_count"] == 2
