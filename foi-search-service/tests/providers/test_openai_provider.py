import numpy as np
import pytest
from unittest.mock import patch, MagicMock

from config import ProviderConfig
from providers.openai_provider import OpenAIProvider
from schemas.models import EmbeddingResult


@pytest.fixture
def provider_config():
    return ProviderConfig(
        provider_name="openai",
        model_name="text-embedding-3-small",
        embedding_dimension=384,
        max_tokens=256,
        cost_per_1k_tokens=0.02,
        cost_per_1m_tokens=0.02
    )


@pytest.fixture
def provider_config_custom():
    return ProviderConfig(
        provider_name="openai",
        model_name="text-embedding-3-small",
        embedding_dimension=768,
        max_tokens=512,
        cost_per_1k_tokens=0.4
    )


class TestOpenAIProviderInitialization:
    """Test initialization and configuration of OpenAIProvider."""

    @patch('providers.openai_provider.OpenAIEmbeddingClient')
    def test_initialize_provider_success(self, mock_model_cls, provider_config):
        """Test initialization with automatic device selection."""
        with patch("providers.openai_provider.OpenAIEmbeddingClient") as MockClient:
            mock_client_instance = MockClient.return_value
            mock_model = MagicMock()
            mock_model_cls.return_value = mock_model

            provider = OpenAIProvider(provider_config)

            # The OpenAIEmbeddingClient should have been instantiated with the config
            MockClient.assert_called_once_with(provider_config=provider_config)
            # The test connection should call embed
            # mock_client_instance.embed.assert_called_once_with(["test connection"])
            assert provider.client == mock_client_instance


class TestOpenAIProviderEncoding:
    """Test sentence encoding using mocked OpenAI client."""

    @patch('providers.openai_provider.OpenAIEmbeddingClient')
    def test_encode_sentences_success(self, mock_client_cls, provider_config):
        sentences = ["This is a test sentence.", "Another test case."]
        mock_client = mock_client_cls.return_value

        # Mock embed return: (embeddings list, total token count)
        mock_embeddings = [[0.1] * provider_config.embedding_dimension] * len(sentences)
        mock_client.embed.return_value = (mock_embeddings, 30)

        provider = OpenAIProvider(provider_config)
        result = provider.encode_sentences(sentences, show_progress=False)

        # Assertions
        assert isinstance(result, EmbeddingResult)
        assert result.num_sentences == len(sentences)
        assert result.embedding_dimension == provider_config.embedding_dimension
        assert result.tokens_used == 30
        assert result.embeddings.shape == (2, provider_config.embedding_dimension)
        assert isinstance(result.cost_estimate, float)
        assert result.cost_estimate > 0

    @patch("providers.openai_provider.OpenAIEmbeddingClient")
    def test_encode_sentence_success(mock_client_class, provider_config):
        # Prepare mocks
        mock_client = MagicMock()
        mock_client.embed.return_value = ([np.random.rand(384).tolist()], 8)
        mock_client_class.return_value = mock_client

        provider = OpenAIProvider(provider_config)

        # Patch encode_sentences to return a dummy EmbeddingResult
        mock_result = EmbeddingResult(
            embeddings=np.random.rand(1, 384),
            model_name="text-embedding-3-small",
            provider_name="openai",
            embedding_dimension=384,
            num_sentences=1,
            tokens_used=8,
            cost_estimate=0.00016,
            metadata={"batch_size": 1}
        )

        with patch.object(provider, "encode_sentences", return_value=mock_result) as mock_encode_sentences:
            result = provider.encode_sentence("AI is transforming industries.")

        # Assertions
        mock_encode_sentences.assert_called_once_with(["AI is transforming industries."], show_progress=False)
        assert result.num_sentences == 1
        assert result.embedding_dimension == 384
        assert isinstance(result.embeddings, np.ndarray)