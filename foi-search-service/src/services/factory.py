"""Factory functions for creating application services with domain services."""

import logging

from src.clients.solr_client import SolrClient
from src.sbert_sentence_tokenizer import SBERTSentenceTokenizer

from .indexing_service import IndexingService
from .search_service import SearchService
from .document_service import DocumentService

from src.config import get_config

logger = logging.getLogger(__name__)


def create_document_service() -> DocumentService:
    """Factory function to create a complete document service with all domain services.
        
    Returns:
        Configured DocumentService instance
        
    Raises:
        ConnectionError: If Solr connection test fails
        ValueError: If configuration is invalid
    """
    # Create tokenizer
    config = get_config()
    provider_config = config.provider
    token_config = config.tokenization

    logger.info(f"Creating tokenizer with model: {provider_config.model_name}")

    tokenizer = SBERTSentenceTokenizer(
        provider_configuration=provider_config,
        max_token_length=token_config.max_token_length,
        max_words_length=token_config.max_words_length,
        token_char_estimate=token_config.token_char_estimate
    )
    
    # Create Solr Client
    solr_config = get_config().solr
    logger.info(f"Creating Solr client for {solr_config.solr_url}/{solr_config.collection}")
    solr_client = SolrClient(
        solr_url=solr_config.solr_url,
        collection=solr_config.collection,
        timeout=solr_config.timeout,
        max_retries=solr_config.max_retries,
        retry_delay=solr_config.retry_delay,
        username=solr_config.username,
        password=solr_config.password,
        verify_ssl=solr_config.verify_ssl,
    )

    # Test connection
    if not solr_client.ping():
        error_msg = f"Failed to connect to Solr at {solr_config.solr_url}/{solr_config.collection}"
        logger.error(error_msg)
        raise ConnectionError(error_msg)
    else:
        logger.info("Solr connection test successful")

    # Create domain services
    indexing_service = IndexingService(
        solr_client=solr_client,
        document_id_prefix=solr_config.document_id_prefix,
    )
    search_service = SearchService(solr_client=solr_client)
    
    # Create application service
    document_service = DocumentService(
        tokenization_service=tokenizer,
        indexing_service=indexing_service,
        search_service=search_service,
    )
    
    logger.info("DocumentService created successfully with all domain services")
    return document_service
