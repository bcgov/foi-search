"""Domain service for search operations."""

import logging
from typing import Any, Dict, List, Optional

from src.clients.solr_client import SolrClient

logger = logging.getLogger(__name__)


class SearchService:
    """Domain service for pure search operations."""

    def __init__(self, solr_client: SolrClient = None):
        """Initialize the search service.
        
        Args:
            solr_client: Solr client instance
        """
        if solr_client is None:
            raise ValueError("Solr client must be provided for search operations")

        self.solr_client = solr_client
        logger.info(f"Initialized SearchService with Solr Collection: {self.solr_client.collection}")

    def search_by_vector(
            self,
            query_vector: List[float],
            num_results: int = 10,
            similarity_threshold: Optional[float] = None,
            filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Perform vector similarity search in Solr.

        Args:
            query_vector: Embedding vector to search with
            num_results: Number of results to return
            similarity_threshold: Minimum similarity score to include in results
            filters: Additional filter queries

        Returns:
            Solr response dictionary with matching documents
        """
        logger.debug(f"Performing vector search with {len(query_vector)}-dimensional vector...")

        try:
            results = self.solr_client.search_similarity(
                vector=query_vector,
                rows=num_results
            )

            docs = results.get("response", {}).get("docs", [])

            # Filter by score if threshold is explicitly set
            if similarity_threshold is not None:
                docs = [doc for doc in docs if doc.get("score", 0.0) >= similarity_threshold]
                results["response"]["docs"] = docs
                results["response"]["numFound"] = len(docs)

            logger.debug(f"Vector search returned {len(docs)} result(s)")
            return results

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return {"error": str(e)}

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the search collection.
        
        Returns:
            Dictionary containing collection statistics
        """
        try:
            # Get total document count
            total_docs = self.solr_client.get_total_documents()

            stats = {
                "total_documents": total_docs,
                "solr_collection": self.solr_client.collection,
                "solr_url": self.solr_client.solr_url,
                "solr_ping": self.solr_client.ping(),
            }
            
            logger.info(f"Collection stats: {total_docs} documents")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}
