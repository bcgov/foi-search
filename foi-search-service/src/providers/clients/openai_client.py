"""Reusable OpenAI client utility for embedding services."""

import time
from typing import List, Tuple
from config import get_config, ProviderConfig
import openai
import logging

logger = logging.getLogger(__name__)

class OpenAIEmbeddingClient:
    """Reusable OpenAI client wrapper for embedding requests."""

    def __init__(
        self,
        provider_config: ProviderConfig,
    ):
        self.model = provider_config.model_name
        self.api_key = provider_config.api_key
        self.api_base_url = provider_config.api_base_url
        self.organization = None
        self.timeout = provider_config.timeout
        self.max_retries = provider_config.max_retries
        self.retry_delay = provider_config.retry_delay

        self.client = self._init_client()

    def _init_client(self) -> openai.OpenAI:
        """Initialize OpenAI SDK client."""
        client_kwargs = {
            "api_key": self.api_key,
            "timeout": self.timeout,
        }

        if self.api_base_url:
            client_kwargs["base_url"] = self.api_base_url
        if self.organization:
            client_kwargs["organization"] = self.organization

        logger.debug("Initializing OpenAI client...")
        return openai.OpenAI(**client_kwargs)

    def embed(
        self,
        sentences: List[str],
        encoding_format: str = "float",
        **kwargs
    ) -> Tuple[List[List[float]], int]:
        """Call OpenAI embedding API with retries.

        Returns:
            Tuple of (embeddings list, total tokens used)
        """

        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=sentences,
                    encoding_format=encoding_format,
                    **kwargs
                )

                logger.debug("OpenAI embedding API response: %s", response)

                embeddings = [item.embedding for item in response.data]
                tokens_used = response.usage.total_tokens

                return embeddings, tokens_used

            except Exception as e:
                if attempt < self.max_retries:
                    wait = self.retry_delay * (2 ** attempt)
                    logger.warning(
                        f"OpenAI embed failed (attempt {attempt + 1}) — retrying in {wait}s: {e}"
                    )
                    time.sleep(wait)
                else:
                    logger.error(f"OpenAI embed failed after {self.max_retries + 1} attempts: {e}")
                    raise

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate if an OpenAI API key works."""
        try:
            client = openai.OpenAI(api_key=api_key)
            client.embeddings.create(
                model="text-embedding-3-small",
                input=["test"],
                encoding_format="float"
            )
            return True
        except Exception as e:
            logger.debug(f"OpenAI API key validation failed: {e}")
            return False
