#!/usr/bin/env python3
"""
Model download script for FOI Search Service application.
Downloads sentence-transformers/all-MiniLM-L6-v2 during Docker build.
"""

import os
import sys
import logging
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def download_model(model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    """
    Download and cache the specified sentence transformer model.

    Args:
        model_name: Name of the model to download from HuggingFace Hub
    """
    try:
        logger.info(f"Starting download of model: {model_name}")

        # Verify cache directory exists
        cache_dir = os.environ.get('HF_HUB_CACHE', '/app/.cache/huggingface/hub')
        os.makedirs(cache_dir, exist_ok=True)
        logger.info(f"Using cache directory: {cache_dir}")

        # Download model - this will cache it automatically
        model = SentenceTransformer(model_name)

        # Test the model to ensure it's working
        test_sentences = ["This is a test sentence for model validation."]
        embeddings = model.encode(test_sentences)

        logger.info(f"Successfully downloaded {model_name}")
        logger.info(f"Model embedding dimension: {embeddings.shape[1]}")
        logger.info(f"Test embedding shape: {embeddings.shape}")

        return True

    except Exception as e:
        logger.error(f"Failed to download model {model_name}: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    download_model()