"""
Keycloak authentication module for FastAPI
"""
import httpx
from jose import jwt, JWTError
from fastapi import Request, HTTPException, status, Depends
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Global JWKS cache
jwks_cache: Optional[Dict[str, Any]] = None

async def fetch_jwks() -> Dict[str, Any]:
    """
    Fetch JSON Web Key Set (JWKS) from Keycloak
    """
    global jwks_cache
    from src.config import get_config
    config = get_config().global_config
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(config.keycloak_jwks_url, timeout=10.0)
            response.raise_for_status()
            jwks_cache = response.json()
            logger.info("JWKS fetched successfully")
            return jwks_cache
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch authentication keys"
        )

async def get_jwks() -> Dict[str, Any]:
    """
    Get JWKS, fetching if not cached
    """
    global jwks_cache
    
    if jwks_cache is None:
        jwks_cache = await fetch_jwks()
    
    return jwks_cache

async def refresh_jwks() -> Dict[str, Any]:
    """
    Force refresh of JWKS cache
    """
    global jwks_cache
    jwks_cache = None
    return await fetch_jwks()

def extract_token_from_header(authorization: str) -> str:
    """
    Extract JWT token from Authorization header
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    return authorization.split(" ")[1]

async def validate_jwt_token(token: str) -> Dict[str, Any]:
    """
    Validate JWT token against Keycloak JWKS
    """
    try:
        # Get unverified headers to extract kid (key ID)
        unverified_headers = jwt.get_unverified_header(token)
        kid = unverified_headers.get("kid")
        
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing key ID"
            )
        
        # Get JWKS
        jwks = await get_jwks()
        
        # Find the key with matching kid
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        
        if key is None:
            # Try refreshing JWKS in case of key rotation
            logger.info("Key not found in cache, refreshing JWKS")
            jwks = await refresh_jwks()
            key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
            
            if key is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: key not found"
                )

        from src.config import get_config
        config = get_config().global_config
        
        # Decode and validate token
        payload = jwt.decode(
            token,
            key,
            algorithms=[key["alg"]],
            audience=config.keycloak_audience,
            issuer=config.keycloak_issuer,
            options={"verify_at_hash": False}  # Disable at_hash check for access tokens
        )
        
        logger.debug(f"Token validated successfully for user: {payload.get('sub')}")
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}"
        )

async def keycloak_auth(request: Request) -> Dict[str, Any]:
    """
    FastAPI dependency for Keycloak authentication
    """
    # Extract Authorization header
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Extract token
    token = extract_token_from_header(auth_header)
    
    # Validate token
    payload = await validate_jwt_token(token)
    
    return payload