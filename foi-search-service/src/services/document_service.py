"""Application service that orchestrates domain services for document operations."""

import logging
from typing import Any, Dict, List, Optional

from src.sbert_sentence_tokenizer import SBERTSentenceTokenizer
from .indexing_service import IndexingService
from .search_service import SearchService
from src.schemas.models import TokenizationResult
import numpy as np

logger = logging.getLogger(__name__)


class DocumentService:
    """Application service that orchestrates domain services for document operations."""

    def __init__(
            self,
            tokenization_service: SBERTSentenceTokenizer,
            indexing_service: IndexingService,
            search_service: SearchService,
    ):
        """Initialize the document service.
        
        Args:
            tokenization_service: Domain service for tokenization
            indexing_service: Domain service for indexing
            search_service: Domain service for search
        """
        self.tokenization_service = tokenization_service
        self.indexing_service = indexing_service
        self.search_service = search_service

        logger.info("Initialized DocumentService with all domain services")

    def _generate_sentence_hash(self, sentence: str) -> str:
        """Generate a unique hash for a sentence."""
        import hashlib

        return hashlib.sha256(f"{sentence}".encode()).hexdigest()

    def tokenize_and_index(
            self,
            sentences: List[str],
            batch_size: int = 32,
            show_progress: bool = True,
            additional_fields: Optional[Dict[str, Any]] = None,
    ) -> TokenizationResult:
        """Tokenize sentences and index to Solr.
        
        Args:
            sentences: List of sentences to tokenize
            batch_size: Batch size for tokenization
            show_progress: Whether to show progress during tokenization
            additional_fields: Additional fields to include in Solr documents

        Returns:
            TokenizationResult containing the tokenization data
        """
        logger.info(f"Starting tokenization and indexing of {len(sentences)} sentences")

        # Generate hashes for all input sentences
        hash_map = {s: self._generate_sentence_hash(s) for s in sentences}

        # Check which hashes already exist in Solr
        existing_hashes = self.indexing_service.document_exists_by_hashes(list(hash_map.values()))

        # Filter out sentences that already exist (based on hash)
        new_sentences = [
            sentence for sentence, sentence_hash in hash_map.items()
            if not existing_hashes.get(sentence_hash, False)
        ]

        if len(new_sentences) > 0:
            # Step 1: Tokenize sentences
            tokenization_result = self.tokenization_service.embedding_sentences(
                sentences=new_sentences,
                batch_size=batch_size,
                show_progress=show_progress
            )

            # Step 2: Index to Solr
            success = self.indexing_service.index_tokenization_result(
                tokenization_result=tokenization_result,
                additional_fields=additional_fields
            )

            if not success:
                logger.warning("Solr indexing failed, but tokenization result is still valid")

            return tokenization_result
        else:
            logger.debug("All sentences already exist in Solr, skipping tokenization and indexing")
            return TokenizationResult(
                sentences=[],
                embeddings=np.array([]),
                model_name="unknown",
                embedding_dimension=0,
                provider="unknown",
                num_sentences=0
            )

    def tokenize_and_index_single_sentence(
            self,
            sentence: str,
            additional_fields: Optional[Dict[str, Any]] = None,
    ) -> TokenizationResult:
        """Tokenize a single sentence and index to Solr.
        
        Args:
            sentence: Sentence to tokenize
            additional_fields: Additional fields for Solr document
            
        Returns:
            Dictionary containing tokenization details and indexing status
        """
        logger.debug(f"Tokenizing and indexing single sentence: {sentence[:50]}...")

        # Step 1: Tokenize
        tokenization_result = self.tokenization_service.embedding_sentence(
            sentence=sentence
        )

        # Step 2: Index to Solr
        success = self.indexing_service.index_tokenization_result(
            tokenization_result=tokenization_result,
            additional_fields=additional_fields
        )

        if not success:
            logger.warning("Solr indexing failed for single sentence, but tokenization result is still valid")

        return tokenization_result

    def search_similarity(
            self,
            sentence: str,
            num_results: int = 10,
            similarity_threshold: Optional[float] = None,
            filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Perform vector similarity search.
        
        Args:
            sentence: Sentence to find similar matches for
            num_results: Number of results to return
            similarity_threshold: Minimum similarity score
            filters: Additional filter queries
            
        Returns:
            Search results from Solr
        """
        logger.debug(f"Orchestrating vector search with sentence: {sentence}")

        sentences = [sentence]
        tokenization_result = self.tokenization_service.embedding_sentences(
            sentences=sentences,
            batch_size=1,
            show_progress=False
        )

        embedding = tokenization_result.embeddings[0]

        return self.search_service.search_by_vector(
            embedding.tolist(), num_results, similarity_threshold, filters
        )

    def batch_process_texts(
            self,
            texts: List[str],
            batch_size: int = 32,
            document_id_prefix: Optional[str] = None,
            additional_fields: Optional[Dict[str, Any]] = None,
    ) -> List[TokenizationResult]:
        """Process multiple batches of text and index to Solr.
        
        Args:
            texts: List of all texts to process
            batch_size: Size of each processing batch
            document_id_prefix: Prefix for document IDs
            additional_fields: Additional fields for all documents

        Returns:
            List of TokenizationResult objects for each batch
        """
        results = []

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1}: {len(batch_texts)} texts")

            # Step 1: Tokenize batch
            tokenization_result = self.tokenization_service.embedding_sentences(
                sentences=batch_texts,
                batch_size=min(batch_size, 32)  # Internal tokenizer batch size
            )

            # Step 2: Index batch
            success = self.indexing_service.index_tokenization_result(
                tokenization_result=tokenization_result,
                document_id_prefix=document_id_prefix,
                additional_fields=additional_fields
            )

            if success:
                results.append(tokenization_result)
            else:
                logger.warning(f"Failed to index batch {i // batch_size + 1}")

        logger.info(f"Completed batch processing: {len(results)} successful batches, {len(texts)} total texts")
        return results