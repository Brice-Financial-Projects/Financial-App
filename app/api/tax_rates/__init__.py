"""Tax rates API integration package."""

import os
from typing import Dict, Any

# Import core components
from .models import (
    TaxBracket,
    FederalTaxData,
    StateTaxData,
    FICATaxData,
    TaxCalculationRequest,
    TaxCalculationResponse
)
from .config import config
from .cache import cache

# Determine which client to use based on environment
use_mock = os.environ.get('USE_MOCK_TAX_API', 'True').lower() == 'true'

if use_mock:
    from .mock_client import client
else:
    from .client import client

# Export main components
__all__ = [
    'client',
    'config',
    'cache',
    'TaxBracket',
    'FederalTaxData',
    'StateTaxData',
    'FICATaxData',
    'TaxCalculationRequest',
    'TaxCalculationResponse'
] 