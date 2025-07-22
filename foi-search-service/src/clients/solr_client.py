"""Solr client utility for indexing tokenization results."""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING, Set
import uuid
import requests
import numpy as np

if TYPE_CHECKING:
    from src.schemas.models import TokenizationResult

logger = logging.getLogger(__name__)


class SolrClient:
    """Reusable Solr client wrapper for indexing documents and embeddings."""

    def __init__(
        self,
        solr_url: str,
        collection: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify_ssl: bool = True,
    ):
        """Initialize Solr client.
        
        Args:
            solr_url: Base URL of Solr server (e.g., "http://localhost:8983/solr")
            collection: Name of the Solr collection/core
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            retry_delay: Initial delay between retries (exponential backoff)
            username: Basic auth username (optional)
            password: Basic auth password (optional)
            verify_ssl: Whether to verify SSL certificates
        """
        self.solr_url = solr_url.rstrip('/')
        self.collection = collection
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.verify_ssl = verify_ssl
        
        # Setup authentication
        self.auth = None
        if username and password:
            self.auth = (username, password)
        
        # Build base URLs
        self.base_url = f"{self.solr_url}/{collection}"
        self.update_url = f"{self.solr_url}/{collection}/update?commit=true"
        self.select_url = f"{self.solr_url}/{collection}/select"
        
        logger.info(f"Initialized Solr client for collection '{collection}' at {self.solr_url}")

    def _make_request(
        self, 
        method: str, 
        url: str, 
        data: Optional[Union[str, bytes]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """Make HTTP request with retries and error handling."""

        if headers is None:
            headers = {}

        for attempt in range(self.max_retries + 1):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    data=data,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                    auth=self.auth,
                    verify=self.verify_ssl
                )
                response.raise_for_status()
                return response

            except requests.exceptions.HTTPError as http_err:
                # Log response body if available
                if 'response' in locals() and response is not None:
                    logger.error(f"HTTP error: {http_err}, response body: {response.text}")
                else:
                    logger.error(f"HTTP error: {http_err}, no response body available")
                if attempt < self.max_retries:
                    wait = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Solr request failed (attempt {attempt + 1}) — retrying in {wait}s: {http_err}")
                    time.sleep(wait)
                else:
                    logger.error(f"Solr request failed after {self.max_retries + 1} attempts: {http_err}")
                    raise

            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception: {e}")
                if attempt < self.max_retries:
                    wait = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Solr request failed (attempt {attempt + 1}) — retrying in {wait}s: {e}")
                    time.sleep(wait)
                else:
                    logger.error(f"Solr request failed after {self.max_retries + 1} attempts: {e}")
                    raise

    def ping(self) -> bool:
        """Check if Solr server and collection are accessible."""
        try:
            ping_url = f"{self.base_url}/admin/ping"
            response = self._make_request("GET", ping_url)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Solr ping failed: {e}")
            return False

    def index_document(self, document: Dict[str, Any]) -> bool:
        """Index a single document to Solr.
        
        Args:
            document: Document to index

        Returns:
            True if successful, False otherwise
        """
        return self.index_documents([document])

    def index_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Index multiple documents to Solr.
        
        Args:
            documents: List of documents to index

        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare the update data
            update_data = json.dumps(documents, ensure_ascii=False)
            
            headers = {
                "Content-Type": "application/json; charset=utf-8"
            }
            
            params = {}

            response = self._make_request(
                "POST",
                f"{self.update_url}",
                data=update_data.encode('utf-8'),
                params=params,
                headers=headers
            )
            
            logger.info(f"Successfully indexed {len(documents)} documents to Solr")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index documents to Solr: {e}")
            return False

    def add_additional_fields(self, doc: Dict[str, Any], additional_fields: Optional[Dict[str, Any]] = None):
        if additional_fields:
            doc.update({f"meta_{k}": v for k, v in additional_fields.items()})
        return doc

    #TODO : Move this to a utility module if used elsewhere
    def _generate_sentence_hash(self, sentence: str) -> str:
        """Generate a unique hash for a sentence."""
        import hashlib

        return hashlib.sha256(f"{sentence}".encode()).hexdigest()

    def index_tokenization_result(
        self, 
        tokenization_result: "TokenizationResult",
        document_id_prefix: str = "doc",
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Index a TokenizationResult to Solr.
        
        Args:
            tokenization_result: The tokenization result to index
            document_id_prefix: Prefix for document IDs
            additional_fields: Additional fields to add to each document

        Returns:
            True if successful, False otherwise
        """
        try:
            documents = []
            
            for i, sentence in enumerate(tokenization_result.sentences):
                doc = {
                    "id": f"{document_id_prefix}_{uuid.uuid4()}",
                    "sentence_hash": self._generate_sentence_hash(sentence),
                    "sentence": sentence,
                    "model_name": tokenization_result.model_name,
                    "provider": tokenization_result.provider,
                    "embedding_dimension": tokenization_result.embedding_dimension,
                    "sentence_index": i,
                }
                
                # Add embedding as vector field (convert numpy array to list)
                if tokenization_result.embeddings is not None and i < len(tokenization_result.embeddings):
                    embedding = tokenization_result.embeddings[i]
                    if isinstance(embedding, np.ndarray):
                        doc["embedding_vector"] = embedding.tolist()
                    else:
                        doc["embedding_vector"] = embedding
                
                # Add optional tokenization details
                if tokenization_result.tokens and i < len(tokenization_result.tokens):
                    doc["tokens"] = tokenization_result.tokens[i]
                
                if tokenization_result.input_ids and i < len(tokenization_result.input_ids):
                    doc["input_ids"] = tokenization_result.input_ids[i]
                
                if tokenization_result.attention_mask and i < len(tokenization_result.attention_mask):
                    doc["attention_mask"] = tokenization_result.attention_mask[i]
                
                # Add cost information if available
                if tokenization_result.tokens_used is not None:
                    doc["tokens_used_total"] = tokenization_result.tokens_used
                    
                if tokenization_result.cost_estimate is not None:
                    doc["cost_estimate_total"] = tokenization_result.cost_estimate
                
                # Add any additional fields
                doc = self.add_additional_fields(doc, additional_fields)
                
                documents.append(doc)
            
            success = self.index_documents(documents)
            
            if success:
                logger.info(
                    f"Successfully indexed {len(documents)} sentences from tokenization result "
                    f"(model: {tokenization_result.model_name}, provider: {tokenization_result.provider})"
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to index tokenization result: {e}")
            return False

    def search_similarity(
            self,
            vector: List[float],
            fields: Optional[List[str]] = None,
            filters: Optional[Dict[str, Any]] = None,
            rows: int = 10,
            start: int = 0,
            threshold: float = 0.7,
            vector_field: str = "embedding_vector"
    ) -> Dict[str, Any]:
        """
        Perform vector similarity search in Solr.

        Args:
            vector: List of floats representing the query embedding
            fields: Fields to return (e.g., ["id", "sentence", "score"])
            filters: Optional filter queries (e.g., {"tag": "cooking"})
            rows: Number of results to return
            start: Offset for pagination
            threshold: Minimum similarity threshold
            vector_field: Solr field name for the dense vector

        Returns:
            Solr response as a dictionary
        """
        try:
            vector_str = "[" + ",".join(f"{x:.6f}" for x in vector) + "]"

            params = {
                "q": f"{{!vectorSimilarity f={vector_field} minReturn={threshold}}}{vector_str}",
                "rows": rows,
                "start": start,
                "wt": "json",
                "fl": ",".join(fields) if fields else "*,score",
                "sort": "score desc"
            }

            response = self._make_request("GET", self.select_url, params=params)

            return response.json()

        except Exception as e:
            return {"error": str(e)}

    def document_exists_by_hashes(self, hashes: List[str]) -> Set[str]:
        """
        Check which of the given sentence hashes already exist in Solr.

        Args:
            hashes: List of sentence hashes to check.

        Returns:
            Set of existing hashes.
        """
        if not hashes:
            return set()

        fq_query = "sentence_hash:(" + " OR ".join(f'"{h}"' for h in hashes) + ")"

        params = {
            "q": "*:*",
            "fq": fq_query,
            "rows": len(hashes),
            "wt": "json",
            "fl": "sentence_hash"
        }

        response = self._make_request("GET", self.select_url, params=params)
        docs = response.json().get("response", {}).get("docs", [])

        return {doc["sentence_hash"] for doc in docs if "sentence_hash" in doc}

    def document_exists_by_hash(
            self,
            sentence_hash: str
    ) -> bool:
        """
        Check if a document with the given sentence hash already exists in Solr.

        Args:
            sentence_hash: The hash of the sentence to check.

        Returns:
            True if a document with the same hash exists; otherwise, False.
        """
        if not sentence_hash:
            return False  # Avoid querying with empty hash

        try:
            params = {
                "q": "*:*",
                "fq": f"sentence_hash:\"{sentence_hash}\"",  # Quotes ensure exact match
                "rows": 1,
                "wt": "json",
                "fl": "id"
            }

            response = self._make_request("GET", self.select_url, params=params)
            json_data = response.json()
            docs = json_data.get("response", {}).get("docs", [])

            return bool(docs)

        except Exception as e:
            logger.warning(f"Failed to check document existence by hash: {e}")
            return False

    def get_total_documents(self) -> int:
        """
        Get the total number of documents in the Solr collection.

        Returns:
            Total document count as an integer.
        """
        try:
            params = {
                "q": "*:*",
                "rows": 0,  # We don't need actual documents
                "wt": "json"
            }

            response = self._make_request("GET", self.select_url, params=params)
            return response.json().get("response", {}).get("numFound", 0)
        except Exception as e:
            logger.error(f"Error fetching total document count: {e}")
            return 0

    def delete_by_query(self, query: str, commit: bool = True) -> bool:
        """Delete documents matching a query.
        
        Args:
            query: Query to select documents for deletion
            commit: Whether to commit immediately
            
        Returns:
            True if successful, False otherwise
        """
        try:
            delete_data = {
                "delete": {
                    "query": query
                }
            }
            
            if commit:
                delete_data["commit"] = {}
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = self._make_request(
                "POST", 
                self.update_url, 
                data=json.dumps(delete_data),
                headers=headers
            )
            
            logger.info(f"Successfully deleted documents matching query: {query}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            return False

    def commit(self) -> bool:
        """Explicitly commit changes to Solr."""
        try:
            commit_data = {"commit": {}}
            headers = {"Content-Type": "application/json"}
            
            response = self._make_request(
                "POST", 
                self.update_url, 
                data=json.dumps(commit_data),
                headers=headers
            )
            
            logger.info("Successfully committed changes to Solr")
            return True
            
        except Exception as e:
            logger.error(f"Failed to commit: {e}")
            return False

    def optimize(self) -> bool:
        """Optimize the Solr index."""
        try:
            optimize_data = {"optimize": {}}
            headers = {"Content-Type": "application/json"}
            
            response = self._make_request(
                "POST", 
                self.update_url, 
                data=json.dumps(optimize_data),
                headers=headers
            )
            
            logger.info("Successfully optimized Solr index")
            return True
            
        except Exception as e:
            logger.error(f"Failed to optimize: {e}")
            return False

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the Solr collection."""
        try:
            admin_url = f"{self.solr_url}/admin/collections"
            params = {
                "action": "CLUSTERSTATUS",
                "collection": self.collection,
                "wt": "json"
            }
            
            response = self._make_request("GET", admin_url, params=params)
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {"error": str(e)}

    @staticmethod
    def validate_connection(solr_url: str, collection: str) -> bool:
        """Validate if Solr connection and collection are accessible."""
        try:
            client = SolrClient(solr_url, collection)
            return client.ping()
        except Exception as e:
            logger.debug(f"Solr connection validation failed: {e}")
            return False
