"""This module initializes the application configuration by loading environment variables and setting up configurations
for global settings, providers, and tokenization.
"""

from .env_loader import load_env
from .global_config import GlobalConfig
from .provider_config import ProviderConfig
from .tokenization_config import TokenizationConfig
from .solr_config import SolrConfig

# Singleton instance placeholder
_config_instance = None

class AppConfig:
    def __init__(self, env_file: str = ".env"):
        load_env(env_file)  # Load from .env first
        self.global_config = GlobalConfig()
        self.provider = ProviderConfig()
        self.tokenization = TokenizationConfig()
        self.solr = SolrConfig()

def get_config(env_file: str = ".env") -> AppConfig:
    global _config_instance
    if _config_instance is None:
        print(f"Initializing AppConfig with environment file: {env_file}")
        _config_instance = AppConfig(env_file)
    else:
        if env_file != ".env":
            print(f"Warning: get_config() called with '{env_file}', but config is already initialized.")
    return _config_instance

def reset_config():
    """Reset the AppConfig singleton (for testing)."""
    global _config_instance
    _config_instance = None
