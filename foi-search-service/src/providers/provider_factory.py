"""Provider factory for creating embedding providers.

This module provides a factory pattern for creating different embedding
providers based on configuration, making it easy to switch between
providers while maintaining a consistent interface.
"""

from typing import Any, Dict, List, Optional, Type, Union
from config import get_config, ProviderConfig
from providers.embedding_provider import EmbeddingProvider
from providers.openai_provider import OpenAIProvider
import logging

logger = logging.getLogger(__name__)

class ProviderFactory:
    """Factory for creating embedding providers.

    This factory manages the creation and configuration of different
    embedding providers, providing a unified interface for provider
    selection and consistent configuration management.
    """

    # Registry of available providers
    _providers: Dict[str, Type[EmbeddingProvider]] = {}

    @classmethod
    def _lazy_load_providers(cls) -> None:
        """Lazy load providers to avoid circular imports."""
        if not cls._providers:
            try:
                from providers.huggingface_provider import HuggingFaceProvider
                cls._providers.update({
                    "huggingface": HuggingFaceProvider,
                    "hf": HuggingFaceProvider,  # Alias
                    "local": HuggingFaceProvider,  # Alias
                    "sentence-transformers": HuggingFaceProvider,  # Alias
                    "openAI": OpenAIProvider,  # Alias for OpenAI models
                    "openai": OpenAIProvider,  # Alias for OpenAI models
                })
            except ImportError as e:
                logger.warning(f"Could not load HuggingFace provider: {e}")

            # Future providers can be added here
            # try:
            #     from providers.openai_provider import OpenAIProvider
            #     cls._providers.update({
            #         "openai": OpenAIProvider,
            #         "gpt": OpenAIProvider,  # Alias
            #     })
            # except ImportError:
            #     logger.debug("OpenAI provider not available")

    @classmethod
    def create_provider(
        cls, 
        provider_config: Optional[ProviderConfig] = None,
        device: Optional[str] = None,
        normalize_embeddings: bool = True,
        **kwargs
    ) -> EmbeddingProvider:
        """Create an embedding provider from configuration.

        Args:
            provider_config: Provider configuration object
            device: Device to run on ('cuda', 'cpu', or None for auto)
            normalize_embeddings: Whether to normalize embeddings
            **kwargs: Provider-specific configuration

        Returns:
            Initialized embedding provider

        Raises:
            ValueError: If provider is not supported
            RuntimeError: If provider fails to initialize
        """
        cls._lazy_load_providers()

        provider = get_config().provider if provider_config is None else provider_config

        provider_name = provider.provider_name.lower()

        if provider_name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(f"Unsupported provider: {provider.provider_name}. Available: {available}")

        provider_class = cls._providers[provider_name]

        try:
            logger.info(f"Creating {provider.provider_name} provider with model {provider.model_name}")
            
            # Merge provider-specific kwargs with defaults
            provider_kwargs = {
                "device": device,
                "normalize_embeddings": normalize_embeddings,
                **kwargs
            }
            
            return provider_class(provider_config=provider, **provider_kwargs)
            
        except ImportError as e:
            logger.error(f"Provider {provider.provider_name} dependencies not installed: {e}")
            raise ValueError(f"Provider {provider.provider_name} requires additional dependencies: {e}")
        except Exception as e:
            logger.error(f"Failed to create {provider.provider_name} provider: {e}")
            raise RuntimeError(f"Failed to initialize {provider.provider_name} provider: {e}")

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available provider names."""
        cls._lazy_load_providers()
        return list(set(cls._providers.keys()))

    @classmethod
    def get_provider_info(cls, provider: str) -> Dict[str, Any]:
        """Get information about a provider.

        Args:
            provider: Provider name

        Returns:
            Dictionary with provider information
        """
        cls._lazy_load_providers()
        provider_lower = provider.lower()

        if provider_lower not in cls._providers:
            raise ValueError(f"Unknown provider: {provider}")

        provider_class = cls._providers[provider_lower]

        info = {
            "name": provider,
            "class": provider_class.__name__,
            "description": provider_class.__doc__.strip().split("\n")[0]
            if provider_class.__doc__
            else "",
            "provider_name_attr": getattr(provider_class, "__provider_name__", provider_lower)
        }

        # Add model information if available
        if hasattr(provider_class, "list_available_models"):
            try:
                info["available_models"] = provider_class.list_available_models()
            except Exception as e:
                logger.warning(f"Could not get available models for {provider}: {e}")
                info["available_models"] = []

        return info

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[EmbeddingProvider]) -> None:
        """Register a new provider.

        Args:
            name: Provider name
            provider_class: Provider class

        Raises:
            ValueError: If provider class doesn't inherit from EmbeddingProvider
        """
        if not issubclass(provider_class, EmbeddingProvider):
            raise ValueError("Provider class must inherit from EmbeddingProvider")

        cls._lazy_load_providers()
        cls._providers[name.lower()] = provider_class
        logger.info(f"Registered provider: {name}")

    @classmethod
    def validate_provider_config(cls, provider_config: ProviderConfig) -> bool:
        """Validate a provider configuration.

        Args:
            provider_config: Configuration to validate

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        cls._lazy_load_providers()
        
        # Check if provider exists
        if provider_config.provider_name.lower() not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unknown provider: {provider_config.provider_name}. "
                f"Available: {available}"
            )

        # Validate required fields
        if not provider_config.model_name or not provider_config.model_name.strip():
            raise ValueError("model_name cannot be empty")

        if provider_config.embedding_dimension <= 0:
            raise ValueError("embedding_dimension must be positive")

        if provider_config.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

        return True
