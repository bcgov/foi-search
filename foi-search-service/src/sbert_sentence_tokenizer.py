"""SBERT-based Sentence Tokenizer Module for Semantic Similarity Tasks

This module provides sentence tokenization and embedding functionality using
multiple providers including Sentence-BERT (SBERT) models from Hugging Face,
OpenAI embeddings.


"""

from typing import Optional, List, Callable

from config import ProviderConfig
from schemas.models import TokenizationResult
from providers.provider_factory import ProviderFactory
import logging

logger = logging.getLogger(__name__)

class SBERTSentenceTokenizer:
    """Multi-provider sentence tokenizer and embedder for semantic similarity
    tasks.

    This class provides functionality to:
    - Tokenize sentences using multiple embedding providers (Hugging Face, OpenAI, etc.)
    - Generate sentence embeddings from various sources
    - Process single sentences or batches

    """

    def __init__(
            self,
            provider_configuration: ProviderConfig,
            max_token_length: int,
            max_words_length: int,
            token_char_estimate: int,
            device: Optional[str] = "cpu",
            normalize_embeddings: bool = True,
            **kwargs,
    ):
        """Initialize the multi-provider sentence tokenizer.

        Args:
            provider_configuration (ProviderConfig): Provider configuration object
            device: Device to run on (for local models: 'cuda', 'cpu', or None for auto)
            normalize_embeddings: Whether to normalize embeddings to unit vectors
            **kwargs: Additional provider-specific arguments

        Raises:
            ValueError: If provider is unknown or configuration is invalid
            ImportError: If provider dependencies are not installed

        Examples:

            # Explicit Hugging Face usage
            tokenizer = SBERTSentenceTokenizer(
                provider_config=ProviderConfig(
                    provider_name="huggingface",
                    model_name="all-MiniLM-L6-v2",
                    embedding_dimension=384,
                    max_tokens=256,
                    cost_per_1k_tokens=0.0,
                    supports_batch=True,
                    api_key=None
                ),
                max_token_length: 512,
                max_words_length: 100,
                token_char_estimate: 4,
                device="cuda",  # or "cpu" for CPU usage
                normalize_embeddings=True
            )

        """
        # Validate configuration
        self._validate_config(
            provider_configuration.model_name,
            provider_configuration.provider_name,
            max_token_length,
            normalize_embeddings
        )

        self.provider_config = provider_configuration

        self.device = device
        self.max_token_length = max_token_length
        self.max_words_length = max_words_length
        self.token_char_estimate = token_char_estimate
        self.normalize_embeddings = normalize_embeddings


        try:
            # Use factory to create provider instance
            self.provider = ProviderFactory.create_provider(
                provider_config=provider_configuration,
                device=device,
                normalize_embeddings=normalize_embeddings,
                **kwargs
            )

            logger.info(f"✓ Initialized {provider_configuration.provider_name} provider with model: {self.provider_config.model_name}")

        except Exception as e:
            raise ValueError(f"Failed to initialize provider {provider_configuration.provider_name}: {e}")

    def _validate_config(self, model_name: str, provider: str, max_seq_length: int, normalize_embeddings: bool) -> None:
        """Validate configuration parameters."""
        if not isinstance(model_name, str) or not model_name.strip():
            raise ValueError(f"model_name must be non-empty string, got {model_name}")

        if not isinstance(max_seq_length, int) or max_seq_length <= 0:
            raise ValueError(f"max_seq_length must be positive integer, got {max_seq_length}")

        if not isinstance(normalize_embeddings, bool):
            raise ValueError(f"normalize_embeddings must be boolean, got {normalize_embeddings}")

        available_providers = self.list_available_providers()
        if provider.lower() not in [p.lower() for p in available_providers]:
            raise ValueError(f"Unknown provider: {provider}. Available: {available_providers}")


    @classmethod
    def list_available_providers(cls) -> List[str]:
        """List all available providers."""
        return ProviderFactory.get_available_providers()

    def embedding_sentences(
        self,
        sentences: List[str],
        batch_size: int = 32,
        show_progress: bool = True,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> TokenizationResult:
        """Get detailed tokenization information for multiple sentences.

        Args:
            sentences: List of sentences to tokenize
            batch_size: Batch size for processing
            show_progress: Whether to show progress bar
            progress_callback: Optional callback function for progress updates (current, total)

        Returns:
            TokenizationResult containing comprehensive tokenization information
        """
        logger.debug(f"Tokenizing {len(sentences)} sentences using {self.provider_config.provider_name} provider")

        # Generate embeddings using the provider
        result = self.provider.encode_sentences(
            sentences, batch_size=batch_size, show_progress=show_progress
        )
        logger.debug(f"Tokenizing result: {result}")
        # Create structured result
        tokenization_result = TokenizationResult(
            sentences=sentences,
            embeddings=result.embeddings,
            model_name=result.model_name,
            embedding_dimension=result.embedding_dimension,
            num_sentences=result.num_sentences,
            provider=result.provider_name,
            tokens_used=result.tokens_used,
            cost_estimate=result.cost_estimate,
        )

        # Add detailed tokenization if available
        if result.metadata:
            tokenization_result.tokens = result.metadata.get("tokens", [])
            tokenization_result.input_ids = result.metadata.get("input_ids", [])
            tokenization_result.attention_mask = result.metadata.get("attention_mask", [])

        # Call progress callback if provided
        if progress_callback:
            progress_callback(len(sentences), len(sentences))

        return tokenization_result

    def embedding_sentence(
            self,
            sentence: str,
            progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> TokenizationResult:
        """Get detailed tokenization information for a single sentence.

        Args:
            sentence: Sentence to tokenize
            progress_callback: Optional callback function for progress updates (current, total)

        Returns:
            TokenizationResult containing comprehensive tokenization information
        """
        logger.debug(f"Tokenizing sentence using {self.provider_config.provider_name} provider")

        # Generate embeddings using the provider
        encoded = self.provider.encode_sentence(
            sentence
        )
        logger.debug(f"Tokenizing result: {encoded}")

        tokenization_result = TokenizationResult(
            sentences=[sentence],
            embeddings=encoded.embeddings,
            model_name=encoded.model_name,
            embedding_dimension=encoded.embedding_dimension,
            num_sentences=encoded.num_sentences,
            provider=encoded.provider_name,
            tokens_used=encoded.tokens_used,
            cost_estimate=encoded.cost_estimate,
        )

        # Add detailed tokenization if available
        if encoded.metadata:
            tokenization_result.tokens = encoded.metadata.get("tokens", [])[0]
            tokenization_result.input_ids = encoded.metadata.get("input_ids", [])[0]
            tokenization_result.attention_mask = encoded.metadata.get("attention_mask", [])[0]

        # Call progress callback if provided
        if progress_callback:
            progress_callback(1, 1)

        return tokenization_result
