"""Tests for ProviderFactory."""
from unittest.mock import patch, MagicMock

import pytest

from config import ProviderConfig
from providers.huggingface_provider import HuggingFaceProvider
from providers.provider_factory import ProviderFactory
from dummy_provider import DummyProvider


class TestProviderFactory:
    """Test the ProviderFactory class."""

    def setup_method(self):
        """Reset provider registry before each test."""
        ProviderFactory._providers = {}

    def test_lazy_load_providers(self):
        """Test that providers are loaded lazily."""
        # Initially empty
        assert ProviderFactory._providers == {}
        
        # Triggers lazy loading
        providers = ProviderFactory.get_available_providers()
        
        # Should have loaded providers
        assert len(ProviderFactory._providers) > 0
        assert "huggingface" in ProviderFactory._providers

    def test_get_available_providers(self):
        """Test getting available providers."""
        providers = ProviderFactory.get_available_providers()
        
        assert isinstance(providers, list)
        assert len(providers) > 0
        assert "huggingface" in providers

    def test_register_provider(self):
        """Test registering a new provider."""
        ProviderFactory.register_provider("dummy", DummyProvider)
        
        providers = ProviderFactory.get_available_providers()
        assert "dummy" in providers

    def test_register_invalid_provider(self):
        """Test registering an invalid provider raises error."""
        class InvalidProvider:
            pass
        
        with pytest.raises(ValueError, match="Provider class must inherit from EmbeddingProvider"):
            ProviderFactory.register_provider("invalid", InvalidProvider)

    def test_get_provider_info(self):
        """Test getting provider information."""
        ProviderFactory.register_provider("dummy", DummyProvider)
        
        info = ProviderFactory.get_provider_info("dummy")
        
        assert info["name"] == "dummy"
        assert info["class"] == "DummyProvider"
        assert "description" in info

    def test_get_provider_info_unknown(self):
        """Test getting info for unknown provider raises error."""
        with pytest.raises(ValueError, match="Unknown provider: unknown"):
            ProviderFactory.get_provider_info("unknown")

    def test_create_provider_unknown(self):
        """Test creating unknown provider raises error."""
        provider_config = ProviderConfig(
            provider_name="unknown",
            model_name="test-model",
            embedding_dimension=384,
            max_tokens=512
        )

        with pytest.raises(ValueError, match="Unsupported provider: unknown"):
            ProviderFactory.create_provider(provider_config)

    def test_validate_provider_config_valid(self):
        """Test validating valid provider configuration."""
        ProviderFactory.register_provider("dummy", DummyProvider)
        
        provider_config = ProviderConfig(
            provider_name="dummy",
            model_name="test-model",
            embedding_dimension=384,
            max_tokens=512
        )
        
        assert ProviderFactory.validate_provider_config(provider_config) is True

    def test_validate_provider_config_unknown_provider(self):
        """Test validating configuration with unknown provider."""
        provider_config = ProviderConfig(
            provider_name="unknown",
            model_name="test-model",
            embedding_dimension=384,
            max_tokens=512
        )

        with pytest.raises(ValueError, match="Unknown provider: unknown"):
            ProviderFactory.validate_provider_config(provider_config)