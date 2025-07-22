"""Hugging Face SBERT provider implementation.

This provider wraps the existing sentence-transformers functionality to
work with the new multi-provider architecture. It allows for embedding
sentences using Hugging Face models.
"""

from typing import Any, Dict, List, Optional, Tuple
from config import get_config, ProviderConfig
from providers.embedding_provider import EmbeddingProvider
from schemas.models import EmbeddingResult
from dataclasses import replace
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, PreTrainedTokenizer
import logging

logger = logging.getLogger(__name__)

class HuggingFaceProvider(EmbeddingProvider):
    """Hugging Face Sentence Transformers provider.

    This provider uses local sentence-transformer models from Hugging
    Face, providing fast, private, and cost-free embeddings.
    """
    __provider_name__ = "huggingface"

    def __init__(
        self,
        provider_config: Optional[ProviderConfig] = None,
        device: Optional[str] = None,
        normalize_embeddings: bool = True,
        **kwargs,
    ):
        """Initialize Hugging Face provider.

        Args:
            provider_config: Configuration for the provider
            device: Device to run on ('cuda', 'cpu', or None for auto)
            normalize_embeddings: Whether to normalize embeddings
            **kwargs: Additional configuration
        """
        self.provider_config = provider_config
        if self.provider_config is None:
            logger.info("HuggingFace provider configuration not provided, using default settings.")
            self.provider_config = get_config().provider

        self.device = device
        self.normalize_embeddings = normalize_embeddings
        self.include_metadata = get_config().tokenization.include_metadata

        super().__init__(provider_config.model_name, **kwargs)

    def _validate_config(self, **kwargs) -> Dict[str, Any]:
        """Validate Hugging Face specific configuration."""
        import torch

        # Set device
        if self.device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        return {
            "device": self.device,
            "max_seq_length": self.provider_config.max_tokens,
            "normalize_embeddings": self.normalize_embeddings,
            **kwargs,
        }

    def _initialize_provider(self) -> None:
        """Initialize sentence transformer model."""

        logger.info(f"Loading Hugging Face model: {self.model_name}")

        # Try to load the model with error handling
        self.model = self._load_model()
        self.model.max_seq_length = self.provider_config.max_tokens

        # Initialize tokenizer for detailed tokenization
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        except Exception as e:
            logger.warning(f"Could not load tokenizer for {self.model_name}: {e}")
            self.tokenizer = None

        logger.info(f"✓ Model loaded successfully on {self.device}")


    def _load_model(self):
        """Load model with fallback options."""
        try:
            return SentenceTransformer(self.model_name, device=self.device)
        except Exception as e:
            logger.warning(f"Failed to load {self.model_name}: {e}")

            raise RuntimeError(
                f"Failed to load any Hugging Face model. "
                f"Please check your internet connection and model availability. "
                f"Original error: {e}"
            )

    def is_model_loaded(self) -> bool:
        return hasattr(self, "model") and self.model is not None

    def encode_sentences(
            self,
            sentences: List[str],
            batch_size: Optional[int] = 32,
            show_progress: bool = True,
            **kwargs,
    ) -> EmbeddingResult:
        """Generate embeddings for sentences using Hugging Face model.

        Args:
            sentences: List of sentences to encode
            batch_size: Batch size for processing
            show_progress: Whether to show progress bar
            **kwargs: Additional parameters

        Returns:
            EmbeddingResult with embeddings and metadata
        """

        sentences, indices, _, _ = self.validate_sentences(
            sentences=sentences,
            max_token_length=self.provider_config.max_tokens
        )

        if not sentences:
            raise ValueError("No valid sentences to encode after validation")

        logger.debug(f"[{self.model_name}] Encoding {len(sentences)} sentences")

        embeddings = self.model.encode(
            sentences,
            batch_size=batch_size or 32,
            show_progress_bar=show_progress,
            normalize_embeddings=self.normalize_embeddings,
            **kwargs,
        )

        embedding_dim = embeddings.shape[-1] if embeddings.ndim > 1 else embeddings.shape[0]
        if embedding_dim != self.provider_config.embedding_dimension:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.provider_config.embedding_dimension}, got {embedding_dim}"
            )

        metadata = None
        estimated_tokens = None
        estimated_cost = None
        if self.include_metadata:
            metadata, estimated_tokens = self.__get_tokenization_metadata(
                sentences,
                tokenizer=getattr(self.model, 'tokenizer', None),
                max_length=self.provider_config.max_tokens,
                device=self.device,
                batch_size=batch_size,
                normalize_embeddings=self.normalize_embeddings
            )
            estimated_cost = self.estimate_cost(sentences)
        else:
            estimated_tokens, estimated_cost = self.estimate_tokens_and_cost(sentences)

        return EmbeddingResult(
            embeddings=embeddings,
            model_name=self.model_name,
            provider_name="huggingface",
            embedding_dimension=embeddings.shape[1],
            num_sentences=len(sentences),
            tokens_used=estimated_tokens,
            cost_estimate=estimated_cost,
            metadata=metadata,
        )

    def encode_sentence(self, sentence: str, **kwargs) -> EmbeddingResult:
        """Generate embedding for a single sentence.

        Args:
            sentence: Sentence to encode
            **kwargs: Additional parameters

        Returns:
            EmbeddingResult with embeddings and metadata
        """
        # Wrap single sentence into a list
        sentences, indices,_,_ = self.validate_sentences([sentence])
        if not sentences:
            raise ValueError("No valid sentence to encode after validation")

        logger.debug(f"[{self.model_name}] Encoding 1 sentence")

        embeddings = self.model.encode(
            sentence,
            batch_size=1,
            show_progress_bar=False,
            normalize_embeddings=self.normalize_embeddings,
            **kwargs,
        )

        embedding_dim = embeddings.shape[-1] if embeddings.ndim > 1 else embeddings.shape[0]
        if embedding_dim != self.provider_config.embedding_dimension:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.provider_config.embedding_dimension}, got {embedding_dim}"
            )

        metadata = None
        estimated_tokens = None
        estimated_cost = None
        if self.include_metadata:
            metadata, estimated_tokens = self.__get_tokenization_metadata(
                [sentence],
                tokenizer=getattr(self.model, 'tokenizer', None),
                max_length=self.provider_config.max_tokens,
                device=self.device,
                batch_size=None,
                normalize_embeddings=self.normalize_embeddings
            )
            estimated_cost = self.estimate_cost(sentences)
        else:
            estimated_tokens, estimated_cost = self.estimate_tokens_and_cost(sentences)

        return EmbeddingResult(
            embeddings=embeddings.reshape(1, -1),
            model_name=self.model_name,
            provider_name="huggingface",
            embedding_dimension=embedding_dim,
            num_sentences=1,
            tokens_used=estimated_tokens,
            cost_estimate=estimated_cost,
            metadata=metadata,
        )

    def __get_tokenization_metadata(
            self,
            sentences: List[str],
            tokenizer: Optional[PreTrainedTokenizer],
            max_length: int,
            device: str,
            batch_size: Optional[int] = None,
            normalize_embeddings: bool = True
    ) -> Tuple[Dict[str, Any], Optional[int]]:
        """
        Helper to extract tokenization metadata and token count.

        Args:
            sentences: List of sentences to tokenize
            tokenizer: HuggingFace tokenizer instance
            max_length: Maximum token length
            device: Device string (e.g., 'cpu', 'cuda')
            batch_size: Batch size used for encoding
            normalize_embeddings: Whether the embeddings were normalized

        Returns:
            A tuple of:
                - metadata dictionary
                - total token count (tokens_used)
        """
        if not tokenizer:
            return {
                "device": device,
                "normalize_embeddings": normalize_embeddings,
                "max_seq_length": max_length,
                "batch_size": batch_size,
                "tokens": None,
                "input_ids": None,
                "attention_mask": None,
            }, None

        tokenized = tokenizer(
            sentences[0] if len(sentences) == 1 else sentences,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )

        if hasattr(tokenized["input_ids"], '__iter__'):
            if hasattr(tokenized["input_ids"], 'tolist'):  # It's a tensor
                tokens_used = sum(len(input_ids) for input_ids in tokenized["input_ids"].tolist())
            else:  # It's already a list
                tokens_used = sum(len(input_ids) for input_ids in tokenized["input_ids"])
        else:
            tokens_used = len(tokenized["input_ids"])


        return {
            "device": device,
            "normalize_embeddings": normalize_embeddings,
            "max_seq_length": max_length,
            "batch_size": batch_size,
            "tokens": [tokenizer.tokenize(s) for s in sentences],
            "input_ids": tokenized["input_ids"].tolist() if hasattr(tokenized["input_ids"], 'tolist') else tokenized["input_ids"],
            "attention_mask": tokenized["attention_mask"].tolist() if hasattr(tokenized["attention_mask"], 'tolist') else tokenized["attention_mask"],
        }, tokens_used


    def get_provider_info(self) -> ProviderConfig:
        """Get Hugging Face provider information."""
        return replace(
            self.provider_config,
            additional_params={
                **(self.provider_config.additional_params or {}),
                "device": self.device,
                "normalize_embeddings": self.normalize_embeddings,
            }
        )

