"""Configuration settings for the tax rates API."""

import os
from dataclasses import dataclass


@dataclass
class TaxAPIConfig:
    """Configuration for tax API endpoints."""
    # API credentials
    api_key: str
    api_secret: str = None
    
    # Base URLs
    base_url: str
    federal_endpoint: str
    state_endpoint: str
    fica_endpoint: str
    
    # Timeout settings
    timeout_seconds: int = 30
    
    # Cache settings
    enable_cache: bool = True
    cache_expiry_seconds: int = 86400  # 24 hours
    

# Load configuration from environment variables
def load_config() -> TaxAPIConfig:
    """Load tax API configuration from environment variables."""
    return TaxAPIConfig(
        api_key=os.environ.get('TAX_API_KEY', ''),
        api_secret=os.environ.get('TAX_API_SECRET', ''),
        base_url=os.environ.get('TAX_API_BASE_URL', 'https://api.taxrates.io/v1'),
        federal_endpoint=os.environ.get('TAX_API_FEDERAL_ENDPOINT', '/federal/rates'),
        state_endpoint=os.environ.get('TAX_API_STATE_ENDPOINT', '/state/rates'),
        fica_endpoint=os.environ.get('TAX_API_FICA_ENDPOINT', '/fica/rates'),
        timeout_seconds=int(os.environ.get('TAX_API_TIMEOUT', '30')),
        enable_cache=os.environ.get('TAX_API_ENABLE_CACHE', 'True').lower() == 'true',
        cache_expiry_seconds=int(os.environ.get('TAX_API_CACHE_EXPIRY', '86400')),
    )


# Default configuration
config = load_config() 