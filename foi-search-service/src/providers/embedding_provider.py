"""Base provider interface for embedding services.

This module defines the abstract interface that all embedding providers
must implement, ensuring consistent behavior across different services
(Hugging Face, OpenAI, etc.).

All EmbeddingProvider subclasses must:
- Define _initialize_provider() to load their model/API client
- Validate provider-specific kwargs in _validate_config()
- Return consistent shapes in encode_sentences/encode_single_sentence
- Use EmbeddingResult to report embeddings and metadata
"""
import math
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from schemas.models import EmbeddingResult
from config import get_config, ProviderConfig
from utils.validation_utils import validate_sentences
import json
import logging

logger = logging.getLogger(__name__)

class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers.

    All embedding providers (Hugging Face, OpenAI, Azure, etc.) must
    implement this interface to ensure consistent behavior across the
    application.
    """

    def __init__(self, model_name: str, **kwargs):
        """Initialize the embedding provider.

        Args:
            model_name: Name of the model to use
            **kwargs: Provider-specific configuration
        """
        self.model_name = model_name
        self.config = self._validate_config(**kwargs)
        self._initialize_provider()

    @abstractmethod
    def _initialize_provider(self) -> None:
        """Initialize the provider-specific components."""
        pass

    @abstractmethod
    def _validate_config(self, **kwargs) -> Dict[str, Any]:
        """Validate and return provider-specific configuration."""
        pass

    @abstractmethod
    def encode_sentences(
        self,
        sentences: List[str],
        batch_size: Optional[int] = None,
        show_progress: bool = True,
        **kwargs,
    ) -> EmbeddingResult:
        """Generate embeddings for a list of sentences.

        Args:
            sentences: List of sentences to encode
            batch_size: Optional batch size for processing
            show_progress: Whether to show progress bar
            **kwargs: Provider-specific parameters

        Returns:
            EmbeddingResult containing embeddings and metadata
        """
        pass

    @abstractmethod
    def encode_sentence(self, sentence: str, **kwargs) -> EmbeddingResult:
        """Generate embedding for a single sentence.

        Args:
            sentence: Sentence to encode
            **kwargs: Provider-specific parameters

        Returns:
            EmbeddingResult containing embeddings and metadata
        """
        pass

    @abstractmethod
    def get_provider_info(self) -> ProviderConfig:
        """Get information about the provider and model.

        Returns:
            ProviderConfig with model and provider details
        """
        pass

    def estimate_cost(self, sentences: List[str]) -> Optional[float]:
        """Estimate the cost for processing given sentences.

        Args:
            sentences: List of sentences to process

        Returns:
            Estimated cost in USD, or None if not applicable
        """
        provider_info = self.get_provider_info()

        if provider_info.cost_per_1k_tokens is None or provider_info.cost_per_1k_tokens <= 0:
            return 0.0

        estimated_tokens = self.estimate_tokens(sentences)

        cost = (estimated_tokens / 1000.0) * provider_info.cost_per_1k_tokens
        return cost

    def estimate_tokens(self, sentences: List[str]) -> int:
        """
        Estimate the number of tokens based on character length using a rough heuristic.

        Args:
            sentences (List[str]): List of input sentences.

        Returns:
            int: Estimated token count.
        """
        return sum(
            math.ceil(len(sentence) / get_config().tokenization.token_char_estimate)
            for sentence in sentences if sentence.strip()
        )

    def estimate_tokens_and_cost(self, sentences: List[str]) -> Tuple[int, float]:
        """
        Estimate the number of tokens and the associated cost for processing a list of sentences.

        This method calculates the approximate number of tokens using a heuristic based on
        character length and estimates the cost of processing these tokens using the configured
        provider's rate (in USD per 1,000 tokens).

        Args:
            sentences (List[str]): A list of input sentences to be processed.

        Returns:
            Tuple[int, float]: A tuple containing:
                - int: The estimated number of tokens.
                - float: The estimated cost in USD.
        """
        tokens = self.estimate_tokens(sentences)
        provider_info = self.get_provider_info()
        cost = (tokens / 1000.0) * provider_info.cost_per_1k_tokens if provider_info.cost_per_1k_tokens else 0.0
        return tokens, cost

    def log_usage(self, sentences: List[str]) -> None:
        """Log usage metrics as a structured JSON object."""

        cost = self.estimate_cost(sentences)
        cost_formatted = f"${cost:.8f}".rstrip("0").rstrip(".") if cost else "$0.00"

        info = self.get_provider_info()
        log_data = {
            "event": "embedding_usage",
            "provider": info.provider_name,
            "model": info.model_name,
            "embedding_dimension": info.embedding_dimension,
            "max_tokens": info.max_tokens,
            "sentences_count": len(sentences),
            "cost_estimate": cost,
            "cost_formatted": cost_formatted,
        }

        logger.info(json.dumps(log_data, ensure_ascii=False))

    def validate_sentences(
            self,
            sentences: List[str],
            max_token_length: Optional[int] = None,
            max_words_length: Optional[int] = None
    ) -> Tuple[List[str], List[int], List[Dict], Dict[str, int]]:

        if max_token_length is None:
            max_token_length = get_config().tokenization.max_token_length
        if max_words_length is None:
            max_words_length = get_config().tokenization.max_words_length

        max_chars = max_token_length * get_config().tokenization.token_char_estimate

        return validate_sentences(
            sentences=sentences,
            max_chars=max_chars,
            max_words=max_words_length
        )

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return self.__class__.__name__.replace("Provider", "").lower()

    @property
    def embedding_dimension(self) -> int:
        """Get the embedding dimension for the current model."""
        return self.get_provider_info().embedding_dimension
