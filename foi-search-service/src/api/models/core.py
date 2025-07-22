from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    uptime: float

class ModelInfo(BaseModel):
    current_model: str
    provider: str
    embedding_dimension: int
