from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class GlobalConfig:
    log_level: str = None
    log_file: Optional[str] = None
    default_provider: str = None
    enable_cache: bool = None

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
