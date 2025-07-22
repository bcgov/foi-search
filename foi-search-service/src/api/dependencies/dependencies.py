
from functools import lru_cache
from src.services.document_service import DocumentService
from src.services.factory import create_document_service


@lru_cache()
def get_document_service() -> DocumentService:
    """Get the main application service for document operations."""
    return create_document_service()


@lru_cache()
def initialize_services() -> None:
    """Initialize all services at startup."""
    get_document_service()
    # Add any other service initializations here
