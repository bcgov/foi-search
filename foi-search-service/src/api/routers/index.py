"""Index Router - Indexed Similarity Search Operations """

import logging
import time
from fastapi import APIRouter, Depends, HTTPException
from src.api.models.index_models import AddDocumentsRequest, AddDocumentsResponse, SemanticSearchResponse, \
    SemanticSearchRequest, SearchDoc
from src.api.dependencies.dependencies import get_document_service
from src.services.document_service import DocumentService
from src.api.exceptions.exceptions import ValidationException
from fastapi import Security
from fastapi.security import HTTPBearer

security = HTTPBearer()

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/index", tags=["index"])

@router.post("/add", response_model=AddDocumentsResponse, dependencies=[Security(security)])
async def add_documents(
    request: AddDocumentsRequest,
    document_service: DocumentService = Depends(get_document_service),
):
    """Add documents to the search index.

    - **sentences**: List of sentences to add

    Returns confirmation with index status, persistence info, and optional build time.
    """
    try:
        start_time = time.time()
        logger.debug(f"Adding {len(request.sentences)} documents to index")

        result = document_service.tokenize_and_index(
            sentences=request.sentences,
            additional_fields=request.metadata,
        )

        processing_time = time.time() - start_time
        logger.info(f"Finished indexing {result.num_sentences} sentences.")

        return AddDocumentsResponse(
            message="Documents added successfully!",
            documents_added=len(request.sentences),
            total_documents=len(request.sentences),
            index_status="built",
            build_time=processing_time,
        )


    except ValidationException as ve:
        logger.warning(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error adding documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/semantic-search", response_model=SemanticSearchResponse, dependencies=[Security(security)])
async def semantic_search(
        request: SemanticSearchRequest,
        document_service: DocumentService = Depends(get_document_service)
):
    """Perform semantic search on indexed documents.
    - **query**: The query sentence to search for
    - **top_k**: Number of top results to return (default 10)
    - **threshold**: Similarity threshold for results (default 0.7)
    Returns a list of documents matching the query with their similarity scores.
    """
    try:
        start_time = time.time()
        logger.debug(f"Performing semantic search for query: {request.query}")
        if not request.query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        results = document_service.search_similarity(
            sentence=request.query,
            num_results=request.top_k,
            similarity_threshold=request.threshold
        )

        processing_time = time.time() - start_time

        response_data = results.get("response", {})
        docs = response_data.get("docs", [])
        logger.info(f"Search completed in {processing_time:.2f} seconds, found {len(docs)} results.")

        return SemanticSearchResponse(
            numFound=response_data.get("numFound", 0),
            start=response_data.get("start", 0),
            maxScore=response_data.get("maxScore", 0.0),
            numFoundExact=response_data.get("numFoundExact", True),
            docs=[
                SearchDoc(
                    id=doc.get("id", "").removeprefix("None_"),
                    sentence=doc.get("sentence", [])[0] if doc.get("sentence") else "",
                    score=doc.get("score", 0.0),
                    **{
                        key.removeprefix("meta_"): value
                        for key, value in doc.items()
                        if key.startswith("meta_") and key.removeprefix("meta_") not in {"id", "sentence", "score"}
                    }
                ) for doc in docs
            ]
        )

    except HTTPException as he:
        logger.warning(f"HTTP error during search: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Error during semantic search: {e}")
        raise HTTPException(status_code=500, detail=str(e))
