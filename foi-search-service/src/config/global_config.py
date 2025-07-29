from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class GlobalConfig:
    log_level: str = None
    log_file: Optional[str] = None
    default_provider: str = None
    enable_cache: bool = None
    keycloak_issuer: str = None
    keycloak_audience: str = None
    keycloak_jwks_url: str = None

    def __post_init__(self):
        if not self.log_level:
            self.log_level = os.getenv("LOG_LEVEL", "info")
        if not self.log_file:
            self.log_file = os.getenv("LOG_FILE", None)
        if not self.default_provider:
            self.default_provider = os.getenv("DEFAULT_PROVIDER", "huggingface")
        # Only override enable_cache if value not provided
        if self.enable_cache is None:
            self.enable_cache = os.getenv("ENABLE_CACHE", "true").lower() != "false"
        if not self.keycloak_issuer:
            self.keycloak_issuer = os.getenv("KEYCLOAK_ISSUER", "http://localhost:8080/auth/realms/myrealm")
        if not self.keycloak_audience:
            self.keycloak_audience = os.getenv("KEYCLOAK_AUDIENCE", "my-audience")
        if not self.keycloak_jwks_url:
            self.keycloak_jwks_url = os.getenv("KEYCLOAK_JWKS_URL", "http://localhost:8080/auth/realms/myrealm/protocol/openid-connect/certs")
