import pytest
from unittest.mock import patch, MagicMock
from providers.clients.openai_client import OpenAIEmbeddingClient
from config import ProviderConfig

# Helper: fake ProviderConfig for tests
@pytest.fixture
def fake_config():
    return ProviderConfig(
        model_name="text-embedding-ada-002",
        api_key="fake-key",
        api_base_url="https://api.fake.com",
        timeout=15,
        max_retries=2,
        retry_delay=0.01,   # Small delay for faster tests
    )

def mock_response(embeddings=[[0.1, 0.2]], total_tokens=5):
    # Simulate OpenAI API embedding response
    class Usage:
        def __init__(self, total_tokens):
            self.total_tokens = total_tokens
    class Item:
        def __init__(self, embedding):
            self.embedding = embedding
    class Response:
        def __init__(self, embeddings, total_tokens):
            self.data = [Item(emb) for emb in embeddings]
            self.usage = Usage(total_tokens)
    return Response(embeddings, total_tokens)

@patch("providers.clients.openai_client.openai.OpenAI")
def test_embed_success(mock_openai, fake_config):
    mock_client = MagicMock()
    mock_client.embeddings = MagicMock()  # <-- Add this!
    mock_client.embeddings.create.return_value = mock_response([[0.9, 0.7]], total_tokens=3)
    mock_openai.return_value = mock_client

    client = OpenAIEmbeddingClient(fake_config)
    result, tokens = client.embed(["hello"])
    assert result == [[0.9, 0.7]]
    assert tokens == 3
    mock_client.embeddings.create.assert_called_once_with(
        model="text-embedding-ada-002",
        input=["hello"],
        encoding_format="float"
    )

@patch("providers.clients.openai_client.openai.OpenAI")
def test_embed_retries_and_fails(mock_openai, fake_config):
    mock_client = MagicMock()
    mock_client.embeddings.create.side_effect = Exception("API Down!")
    mock_openai.return_value = mock_client

    client = OpenAIEmbeddingClient(fake_config)
    # Should raise after retries
    with pytest.raises(Exception, match="API Down!"):
        client.embed(["fail"])

    # embed() should be called (max_retries + 1) times
    assert mock_client.embeddings.create.call_count == fake_config.max_retries + 1

@patch("providers.clients.openai_client.openai.OpenAI")
def test_embed_recovers_on_retry(mock_openai, fake_config):
    mock_client = MagicMock()
    # First call fails, second call succeeds
    mock_client.embeddings.create.side_effect = [Exception("1st fail"), mock_response([[1.0, 2.0]], 10)]
    mock_openai.return_value = mock_client

    client = OpenAIEmbeddingClient(fake_config)
    result, tokens = client.embed(["retry"])
    assert result == [[1.0, 2.0]]
    assert tokens == 10
    assert mock_client.embeddings.create.call_count == 2

@patch("providers.clients.openai_client.openai.OpenAI")
def test_validate_api_key_success(mock_openai):
    mock_client = MagicMock()
    mock_client.embeddings.create.return_value = mock_response()
    mock_openai.return_value = mock_client

    assert OpenAIEmbeddingClient.validate_api_key("good-key") is True

@patch("providers.clients.openai_client.openai.OpenAI")
def test_validate_api_key_fail(mock_openai):
    mock_client = MagicMock()
    mock_client.embeddings.create.side_effect = Exception("bad key")
    mock_openai.return_value = mock_client

    assert OpenAIEmbeddingClient.validate_api_key("bad-key") is False
