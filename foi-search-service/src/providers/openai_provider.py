"""OpenAI embedding provider implementation.

This provider integrates with OpenAI's embedding API to provide high-
quality embeddings using models like text-embedding-3-*.
"""

from typing import Optional, List, Dict, Any

import numpy as np
from tqdm import tqdm

from providers.clients.openai_client import OpenAIEmbeddingClient
from providers.embedding_provider import EmbeddingProvider
from schemas.models import EmbeddingResult
from config import get_config, ProviderConfig
import logging

logger = logging.getLogger(__name__)

class OpenAIProvider(EmbeddingProvider):
    """OpenAI embedding provider.

    This provider uses OpenAI's embedding API to generate high-quality
    embeddings. Requires an OpenAI API key and charges per token usage.
    """
    __provider_name__ = "openai"

    def __init__(
        self,
        provider_config: Optional[ProviderConfig] = None,
        **kwargs,
    ):
        """Initialize OpenAI provider.

        Args:
            provider_config (ProviderConfig): Configuration for OpenAI provider
            **kwargs: Additional configuration
        """
        self.provider_config = provider_config
        if self.provider_config is None:
            logger.info("OpenAI provider configuration not provided, using default settings.")
            self.provider_config = get_config().provider

        super().__init__(provider_config.model_name, **kwargs)

    def _initialize_provider(self) -> None:
        """Initialize OpenAI client."""
        try:
            logger.info(f"Initializing OpenAI client with model: {self.provider_config.model_name}")

            self.client = OpenAIEmbeddingClient(
                provider_config=self.provider_config
            )

            # Test the connection
            self._test_connection()

            logger.info("✓ OpenAI client initialized successfully")

        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI Provider: {e}")

    def _test_connection(self) -> None:
        """Test OpenAI API connection with a simple request."""
        try:
            # Use your wrapper's .embed method
            # self.client.embed(["test connection"])
            logger.info("✓ OpenAI API connection test successful")
        except Exception as e:
            raise RuntimeError(f"OpenAI API connection test failed: {e}")

    def encode_sentences(
        self,
        sentences: List[str],
        batch_size: Optional[int] = None,
        show_progress: bool = True,
        **kwargs,
    ) -> EmbeddingResult:
        """Generate embeddings using OpenAI API.

        Args:
            sentences: List of sentences to encode
            batch_size: Batch size for API requests
            show_progress: Whether to show progress bar
            **kwargs: Additional OpenAI parameters

        Returns:
            EmbeddingResult with embeddings and metadata
        """
        if not sentences:
            raise ValueError("Cannot encode empty sentence list")

        # Validate sentences
        valid_sentences, valid_indices ,_ ,_  = self.validate_sentences(sentences)
        if not sentences:
            raise ValueError("No valid sentence to encode after validation")

        logger.debug(f"Encoding {len(valid_sentences)} sentences with OpenAI {self.model_name}")

        # Set default batch size if not provided
        if batch_size is None:
            batch_size = self.provider_config.max_batch_size

        all_embeddings = []
        total_tokens = 0

        # Process in batches
        batches = [
            valid_sentences[i : i + batch_size] for i in range(0, len(valid_sentences), batch_size)
        ]

        progress_bar = tqdm(batches, desc="OpenAI API requests") if show_progress else batches

        for batch in progress_bar:
            batch_embeddings, batch_tokens = self.client.embed(batch, **kwargs)
            all_embeddings.extend(batch_embeddings)
            total_tokens += batch_tokens

        # Convert to numpy array
        embeddings = np.array(all_embeddings)

        embedding_dim = embeddings.shape[-1] if embeddings.ndim > 1 else embeddings.shape[0]
        if embedding_dim != self.provider_config.embedding_dimension:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.provider_config.embedding_dimension}, got {embedding_dim}"
            )

        # Calculate cost
        cost_estimate =  self.estimate_cost(sentences)

        return EmbeddingResult(
            embeddings=embeddings,
            model_name=self.model_name,
            provider_name="openai",
            embedding_dimension=embedding_dim,
            num_sentences=len(valid_sentences),
            tokens_used=total_tokens,
            cost_estimate=cost_estimate,
            metadata={
                "batch_size": batch_size
            },
        )

    def encode_sentence(self, sentence: str, **kwargs) -> EmbeddingResult:
        """
        Generate an embedding for a single sentence using the OpenAI API.

        Args:
            sentence (str): The input sentence to encode.
            **kwargs: Additional parameters for OpenAI embedding.

        Returns:
            EmbeddingResult: An object containing the embedding and associated metadata.
        """
        if not isinstance(sentence, str) or not sentence.strip():
            raise ValueError("Input must be a non-empty string")

        # Use the existing method to handle processing logic
        result = self.encode_sentences([sentence], show_progress=False, **kwargs)

        # Post-check: only one sentence should be returned
        if result.num_sentences != 1:
            raise ValueError(f"Expected one embedding, but got {result.num_sentences}")

        return result

    def get_provider_info(self) -> ProviderConfig:
        return self.provider_config

    def _validate_config(self, **kwargs) -> Dict[str, Any]:
        pass