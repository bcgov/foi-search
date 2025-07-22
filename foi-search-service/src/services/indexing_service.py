"""Domain service for indexing operations."""

import logging
from typing import Any, Dict, List, Optional

from src.clients.solr_client import SolrClient
from src.schemas.models import TokenizationResult

logger = logging.getLogger(__name__)

class IndexingService:
    """Domain service for pure indexing operations."""

    def __init__(
        self,
        solr_client: SolrClient = None,
        document_id_prefix: str = "doc",
    ):
        """Initialize the indexing service.
        
        Args:
            solr_client: Solr client instance (optional)
            document_id_prefix: Prefix for generated document IDs
        """
        if solr_client is None:
            raise ValueError("Solr client must be provided for indexing operations")

        self.solr_client = solr_client
        self.document_id_prefix = document_id_prefix
        
        logger.info(f"Initialized IndexingService with Solr Collection: {self.solr_client.collection}")

    def document_exists_by_hashes(self, document_hashes: List[str]) -> Dict[str, bool]:
        """Check if documents exist in Solr by their hashes.

        Args:
            document_hashes: List of document hashes to check

        Returns:
            Dictionary mapping each hash to a boolean indicating existence
        """
        try:
            # Solr client returns a set of hashes that exist
            existing_set = self.solr_client.document_exists_by_hashes(document_hashes)

            # Build result mapping each input hash to True/False
            result = {doc_hash: doc_hash in existing_set for doc_hash in document_hashes}

            for doc_hash, exists in result.items():
                logger.debug(f"Document with hash {doc_hash} exists: {exists}")

            return result
        except Exception as e:
            logger.error(f"Error checking document existence by hashes: {e}")
            return {}

    def document_exists_by_hash(self, document_hash: str) -> bool:
        """Check if a document exists in Solr by its hash.

        Args:
            document_hash: Hash of the document to check

        Returns:
            True if document exists, False otherwise
        """
        try:
            exists = self.solr_client.document_exists_by_hash(document_hash)
            logger.info(f"Document with hash {document_hash} exists: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking document existence by hash: {e}")
            return False

    def index_tokenization_result(
        self,
        tokenization_result: TokenizationResult,
        additional_fields: Optional[Dict[str, Any]] = None,
        document_id_prefix: Optional[str] = None
    ) -> bool:
        """Index tokenization result to Solr.
        
        Args:
            tokenization_result: The tokenization result to index
            additional_fields: Additional fields to include in documents
            document_id_prefix: Prefix for document IDs

        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.solr_client.index_tokenization_result(
                tokenization_result=tokenization_result,
                document_id_prefix=document_id_prefix,
                additional_fields=additional_fields
            )
            
            if success:
                logger.info(f"Successfully indexed {tokenization_result.num_sentences} documents to Solr")
            else:
                logger.error("Failed to index documents to Solr")
                
            return success
            
        except Exception as e:
            logger.error(f"Error during Solr indexing: {e}")
            return False

    def batch_index_results(
        self,
        tokenization_results: List[TokenizationResult],
        document_prefix: Optional[str] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Index multiple tokenization results to Solr.
        
        Args:
            tokenization_results: List of tokenization results to index
            document_prefix: Prefix for document IDs (defaults to instance setting)
            additional_fields: Additional fields for all documents

        Returns:
            True if all successful, False otherwise
        """

        prefix = document_prefix or self.document_id_prefix
        success_count = 0
        
        for i, result in enumerate(tokenization_results):
            batch_prefix = f"{prefix}_batch_{i}"
            
            # Update document prefix for this batch
            original_prefix = self.document_id_prefix
            self.document_id_prefix = batch_prefix
            
            try:
                success = self.index_tokenization_result(result, additional_fields)
                if success:
                    success_count += 1
                    
            finally:
                # Restore original prefix
                self.document_id_prefix = original_prefix
        
        logger.info(f"Batch indexing completed: {success_count}/{len(tokenization_results)} successful")
        return success_count == len(tokenization_results)

    def get_indexing_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexing configuration.
        
        Returns:
            Dictionary containing indexing information and stats
        """
        stats = {
            "solr_connected": self.solr_client is not None,
            "document_id_prefix": self.document_id_prefix,
        }
        
        if self.solr_client:
            stats["solr_collection"] = self.solr_client.collection
            stats["solr_url"] = self.solr_client.solr_url
            stats["solr_ping"] = self.solr_client.ping()
        
        return stats
