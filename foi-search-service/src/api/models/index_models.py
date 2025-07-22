"""AddDocumentsRequest and AddDocumentsResponse models for handling document addition requests."""
from email.policy import default

from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import List, Optional, Dict, Any

class AddDocumentsRequest(BaseModel):
    sentences: List[str] = Field(..., description="Sentences to add to the index")
    metadata: Dict[str, Any] = Field(..., description="Metadata for all sentences")

    @model_validator(mode="before")
    def validate_input(cls, values):
        sentences = values.get("sentences")
        if not sentences:
            raise ValueError("Sentences list cannot be empty")
        if len(sentences) > 1000:
            raise ValueError("Maximum 1000 sentences per batch")
        return values

class AddDocumentsResponse(BaseModel):
    message: str
    documents_added: int
    total_documents: int
    index_status: str
    build_time: Optional[float] = None

    @property
    def formatted_build_time(self) -> Optional[str]:
        if self.build_time is not None:
            return f"{self.build_time:.8f} seconds"
        return None

class SemanticSearchRequest(BaseModel):
    query: str = Field(..., description="Query sentence for semantic search")  # Required field (no default)
    top_k: int = Field(10, description="Number of results to return")          # Default=10
    threshold: float = Field(0.7, description="Threshold for semantic similarity") # Default=0.7

class SearchDoc(BaseModel):
    id: str
    sentence: str = None
    score: float
    model_config = ConfigDict(extra="allow")


class SemanticSearchResponse(BaseModel):
    numFound: int
    start: int
    maxScore: float
    numFoundExact: bool
    docs: List[SearchDoc]
