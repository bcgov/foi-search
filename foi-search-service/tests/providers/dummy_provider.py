"""DummyProvider for testing purposes."""

from typing import Optional, Dict, Any, List
import numpy as np
import logging

from config import ProviderConfig, get_config
from providers.embedding_provider import EmbeddingProvider
from schemas.models import EmbeddingResult

logger = logging.getLogger(__name__)

class DummyProvider(EmbeddingProvider):
    """Dummy provider for testing purposes."""
    __provider_name__ = "dummy"

    def __init__(
        self,
        provider_config: Optional[ProviderConfig] = None,
        device: Optional[str] = None,
        normalize_embeddings: bool = True,
        **kwargs,
    ):
        """Initialize Dummy provider.

        Args:
            provider_config: Configuration for the provider
            device: Device to run on (ignored for dummy)
            normalize_embeddings: Whether to normalize embeddings
            **kwargs: Additional configuration
        """
        self.provider_config = provider_config if provider_config is not None else self._create_default_config()
        self.device = device
        self.normalize_embeddings = normalize_embeddings

        super().__init__(self.provider_config.model_name, **kwargs)

    def _create_default_config(self):
        """Create a default config for dummy provider without environment variables."""
        # Create a minimal config object that doesn't read from environment
        class DummyConfig:
            def __init__(self):
                self.provider_name = "dummy"
                self.model_name = "dummy-model"
                self.embedding_dimension = 384
                self.max_tokens = 512
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
        
        return DummyConfig()

    def _initialize_provider(self) -> None:
        """Initialize the dummy provider (no-op)."""
        logger.info(f"✓ Dummy provider initialized with model: {self.provider_config.model_name}")

    def _validate_config(self, **kwargs) -> Dict[str, Any]:
        """Validate dummy provider configuration."""
        return {
            "device": self.device,
            "normalize_embeddings": self.normalize_embeddings,
            **kwargs
        }

    def encode_sentences(
        self,
        sentences: List[str],
        batch_size: Optional[int] = None,
        show_progress: bool = True,
        **kwargs,
    ) -> EmbeddingResult:
        """Generate dummy embeddings for sentences."""
        dim = self.get_provider_info().embedding_dimension
        embeddings = np.random.rand(len(sentences), dim)
        
        if self.normalize_embeddings:
            # Normalize embeddings to unit vectors
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            embeddings = embeddings / (norms + 1e-8)
        
        return EmbeddingResult(
            embeddings=embeddings,
            model_name=self.model_name,
            provider_name=self.get_provider_info().provider_name,
            embedding_dimension=dim,
            num_sentences=len(sentences),
            tokens_used=sum(len(s.split()) for s in sentences),  # Simple word count
            cost_estimate=self.estimate_cost(sentences)
        )

    def encode_sentence(self, sentence: str, **kwargs) -> EmbeddingResult:
        """Generate dummy embedding for a single sentence."""
        return self.encode_sentences([sentence], **kwargs)

    def get_provider_info(self):
        """Get dummy provider information."""
        return self.provider_config
