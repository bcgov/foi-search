from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import os

@dataclass
class ProviderConfig:
    provider_name: str = None
    model_name: str = None
    embedding_dimension: int = None
    max_tokens: int = None
    cost_per_1k_tokens: Optional[float] = None
    cost_per_1m_tokens: Optional[float] = None
    supports_batch: bool = None
    api_key: Optional[str] = None
    additional_params: Optional[Dict[str, Any]] = field(default_factory=dict)
    api_base_url: Optional[str] = None
    max_retries: int = None
    retry_delay: float = None
    max_batch_size: int = None
    timeout: float = None

    def __post_init__(self):
        if not self.provider_name:
            self.provider_name = os.getenv("PROVIDER_NAME", "huggingface")
        if not self.model_name:
            self.model_name = os.getenv("MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
        if not self.embedding_dimension:
            self.embedding_dimension = int(os.getenv("EMBEDDING_DIM", "384"))
        if not self.max_tokens:
            self.max_tokens = int(os.getenv("MAX_TOKENS", "256"))
        if not self.cost_per_1k_tokens:
            self.cost_per_1k_tokens = float(os.getenv("COST_PER_1K", "0.0"))
        if not self.cost_per_1m_tokens:
            self.cost_per_1m_tokens = float(os.getenv("COST_PER_1M", "0.0"))
        if not isinstance(self.supports_batch, bool):
            self.supports_batch = os.getenv("SUPPORTS_BATCH", "true").lower() == "true"
        if not self.api_key:
            self.api_key = os.getenv("API_KEY", None)
        if not self.api_base_url:
            self.api_base_url = os.getenv("API_BASE_URL", None)
        if not self.max_retries:
            self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        if not self.retry_delay:
            self.retry_delay = float(os.getenv("RETRY_DELAY", "1.0"))
        if not self.max_batch_size:
            self.max_batch_size = int(os.getenv("MAX_BATCH_SIZE", "100"))
        if not self.timeout:
            self.timeout = float(os.getenv("TIMEOUT", "30.0"))
        if self.additional_params is None:
            self.additional_params = {}
        if not isinstance(self.additional_params, dict):
            raise ValueError("additional_params must be a dictionary")
