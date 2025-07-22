"""Tests for SBERTSentenceTokenizer."""

import pytest

from config import ProviderConfig
from sbert_sentence_tokenizer import SBERTSentenceTokenizer
from providers.provider_factory import ProviderFactory
from tests.providers.dummy_provider import DummyProvider


class TestSBERTSentenceTokenizer:
    """Test the SBERTSentenceTokenizer class."""

    def setup_method(self):
        """Reset provider registry before each test."""
        ProviderFactory._providers = {}

    @pytest.fixture
    def provider_config(self):
        """Create a test provider configuration."""
        return ProviderConfig(
            provider_name="dummy",
            model_name="test-model",
            embedding_dimension=384,
            max_tokens=512,
            cost_per_1k_tokens=0.0,
            supports_batch=True
        )

    def test_initialization_success(self, provider_config):
        """Test successful tokenizer initialization."""
        # Register dummy provider
        ProviderFactory.register_provider("dummy", DummyProvider)

        tokenizer = SBERTSentenceTokenizer(
            provider_configuration=provider_config,
            max_token_length=512,
            max_words_length=100,
            token_char_estimate=4,
            device="cpu",
            normalize_embeddings=True
        )

        assert tokenizer.provider_config.provider_name == "dummy"
        assert tokenizer.max_token_length == 512
        assert tokenizer.max_words_length == 100
        assert tokenizer.token_char_estimate == 4
        assert tokenizer.device == "cpu"
        assert tokenizer.normalize_embeddings is True
        assert tokenizer.provider is not None

    def test_initialization_with_unknown_provider(self, provider_config):
        """Test initialization with unknown provider raises error."""
        provider_config.provider_name = "unknown"
        
        with pytest.raises(ValueError, match="Unknown provider: unknown"):
            SBERTSentenceTokenizer(
                provider_configuration=provider_config,
                max_token_length=512,
                max_words_length=100,
                token_char_estimate=4
            )

    def test_validate_config_invalid_model_name(self, provider_config):
        """Test validation with invalid model name."""
        ProviderFactory.register_provider("dummy", DummyProvider)
        provider_config.model_name = ""
        
        with pytest.raises(ValueError, match="model_name must be non-empty string"):
            SBERTSentenceTokenizer(
                provider_configuration=provider_config,
                max_token_length=512,
                max_words_length=100,
                token_char_estimate=4
            )

    def test_validate_config_invalid_max_seq_length(self, provider_config):
        """Test validation with invalid max sequence length."""
        ProviderFactory.register_provider("dummy", DummyProvider)
        
        with pytest.raises(ValueError, match="max_seq_length must be positive integer"):
            SBERTSentenceTokenizer(
                provider_configuration=provider_config,
                max_token_length=0,
                max_words_length=100,
                token_char_estimate=4
            )

    def test_validate_config_invalid_normalize_embeddings(self, provider_config):
        """Test validation with invalid normalize_embeddings type."""
        ProviderFactory.register_provider("dummy", DummyProvider)
        
        with pytest.raises(ValueError, match="normalize_embeddings must be boolean"):
            SBERTSentenceTokenizer(
                provider_configuration=provider_config,
                max_token_length=512,
                max_words_length=100,
                token_char_estimate=4,
                normalize_embeddings="invalid"
            )

    def test_list_available_providers(self):
        """Test listing available providers."""
        ProviderFactory.register_provider("dummy", DummyProvider)
        
        providers = SBERTSentenceTokenizer.list_available_providers()
        
        assert isinstance(providers, list)
        assert "dummy" in providers
