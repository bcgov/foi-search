"""API Routers Package.

This package contains organized API routers for different functionality areas:
- index: Indexed search operations
"""

from src.api.routers.index import router as index_router

__all__ = ["index_router"]
