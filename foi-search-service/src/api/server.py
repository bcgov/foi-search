import logging
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.api.routers import index_router
from src.api.dependencies.dependencies import initialize_services

from src.api.models.core import HealthResponse, ModelInfo

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing FOI Search Service...")
    app.state.start_time = time.time()
    initialize_services()
    logger.info("✓ API server initialized successfully")
    yield
    logger.info("Shutting down API server...")

def create_app() -> FastAPI:
    app = FastAPI(
        title="FOI Search Service API",
        description="REST API for sentence tokenization and semantic search",
        version="1.0.0",
        docs_url="/docs",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(index_router)
    return app

app = create_app()

@app.get("/", response_model=dict)
async def root():
    return {
        "message": "FOI Search Service API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "services": ["index"],
    }

@app.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    uptime = int(time.time() - getattr(request.app.state, "start_time", time.time()))
    return HealthResponse(status="healthy", uptime=uptime)

@app.get("/models", response_model=ModelInfo)
async def get_model_info():
    try:
        from src.config import get_config

        provider = get_config().provider
        return ModelInfo(
            current_model=provider.model_name,
            provider=provider.provider_name,
            embedding_dimension=provider.embedding_dimension
        )
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    import argparse, uvicorn
    from src.config import get_config
    from src.utils.logging_utils import setup_logging

    log_level = get_config().global_config.log_level
    setup_logging(log_level)

    parser = argparse.ArgumentParser(description="FOI Search API Server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()
    logger.info("Starting FOI Search Service API...")
    print("🚀 FOI Search Service API Server\nDocs: /docs")
    uvicorn.run(
        "src.api.server:app",
        host=args.host,
        port=args.port,
        workers=args.workers,
        reload=args.reload,
        log_level=log_level,
    )

if __name__ == "__main__":
    main()
