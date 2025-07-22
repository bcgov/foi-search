
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import numpy as np


@dataclass
class EmbeddingResult:
    """Result from embedding generation."""

    embeddings: np.ndarray
    model_name: str
    provider_name: str
    embedding_dimension: int
    num_sentences: int
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class TokenizationResult:
    """Structured result for tokenization operations."""
    sentences: List[str]
    embeddings: np.ndarray
    model_name: str
    embedding_dimension: int
    provider: str
    num_sentences: int
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    # Optional detailed tokenization info
    tokens: Optional[List[List[str]]] = None
    input_ids: Optional[List[List[int]]] = None
    attention_mask: Optional[List[List[int]]] = None

    @property
    def formatted_cost(self) -> Optional[str]:
        if self.cost_estimate is not None:
            return f"${self.cost_estimate:.8f}".rstrip("0").rstrip(".")
        return "$0.00"
